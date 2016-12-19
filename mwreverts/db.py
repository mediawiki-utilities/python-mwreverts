"""
This module provides a set of convenience function for detecting revert
status via a mwdb database connection.

.. autofunction:: check

.. autofunction:: check_archive
"""
import time
from itertools import chain

from mwtypes import Timestamp
from sqlalchemy import and_

from . import defaults
from .dummy_checksum import DummyChecksum
from .functions import detect


def n_edits_after(schema, rev_id, page_id, n, before=None):
    if before is not None:
        before_fmt = bytes(before.short_format(), 'utf8')
    else:
        before_fmt = bytes(Timestamp(time.time()).short_format(), 'utf8')
    with schema.transaction() as session:
        result = session.query(schema.revision).filter(
            and_(schema.revision.c.rev_page == page_id,
                 schema.revision.c.rev_id > rev_id,
                 schema.revision.c.rev_timestamp <= before_fmt)).order_by(
            schema.revision.c.rev_id.asc()).limit(n)

        for row in result:
            yield row


def n_edits_before(schema, rev_id, page_id, n, rvprop=None):
    with schema.transaction() as session:
        result = session.query(schema.revision).filter(
            and_(schema.revision.c.rev_page == page_id,
                 schema.revision.c.rev_id < rev_id)).order_by(
            schema.revision.c.rev_id.desc()).limit(n)

        # Reverse order because of the query pattern
        rows = reversed(list(result))
        for row in rows:
            yield row


def get_page_id(schema, rev_id):
    with schema.transaction() as session:
        row = session.query(schema.revision.c.rev_page).filter(
            schema.revision.c.rev_id == rev_id).first()

        return row[0]


def check(schema, rev_id, page_id=None, radius=defaults.RADIUS,
          before=None, window=None):
    """
    Checks the revert status of a revision.  With this method, you can
    determine whether an edit is a 'reverting' edit, was 'reverted' by another
    edit and/or was 'reverted_to' by another edit.

    :Parameters:
        session : :class:`mwapi.Session`
            An API session to make use of
        rev_id : int
            the ID of the revision to check
        page_id : int
            the ID of the page the revision occupies (slower if not provided)
        radius : int
            a positive integer indicating the maximum number of revisions
            that can be reverted
        before : :class:`mwtypes.Timestamp`
            if set, limits the search for *reverting* revisions to those which
            were saved before this timestamp
        window : int
            if set, limits the search for *reverting* revisions to those which
            were saved within `window` seconds after the reverted edit
        rvprop : set( str )
            a set of properties to include in revisions

    :Returns:
        A triple :class:`mwreverts.Revert` | `None`

        * reverting -- If this edit reverted other edit(s)
        * reverted -- If this edit was reverted by another edit
        * reverted_to -- If this edit was reverted to by another edit

    :Example:

        >>> import mwdb
        >>> import mwreverts.api
        >>>
        >>> schema = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
                                 "?read_default_file=~/replica.my.cnf")
        >>>
        >>> def print_revert(revert):
        ...     if revert is None:
        ...         print(None)
        ...     else:
        ...         print(revert.reverting['rev_id'],
        ...               [r['rev_id'] for r in revert.reverteds],
        ...               revert.reverted_to['rev_id'])
        ...
        >>> reverting, reverted, reverted_to = \\
        ...     mwreverts.db.check(schema, 679778587)
        >>> print_revert(reverting)
        None
        >>> print_revert(reverted)
        679778743 [679778587] 679742862
        >>> print_revert(reverted_to)
        None

    """

    rev_id = int(rev_id)
    radius = int(radius)
    if radius < 1:
        raise TypeError("invalid radius.  Expected a positive integer.")

    page_id = int(page_id) if page_id is not None else None
    before = Timestamp(before) if before is not None else None

    # If we don't have the page_id, we're going to need to look them up
    if page_id is None:
        page_id = get_page_id(schema, rev_id)

    # Load history and current rev
    current_and_past_revs = list(n_edits_before(
        schema, rev_id + 1, page_id, n=radius + 1))

    if len(current_and_past_revs) < 1:
        raise KeyError("Revision {0} not found in page {1}."
                       .format(rev_id, page_id))

    current_rev, past_revs = (
        current_and_past_revs[-1],  # Current rev is the last one returned
        current_and_past_revs[:-1]  # The rest are past revs
    )
    if current_rev.rev_id != rev_id:
        raise KeyError("Revision {0} not found in page {1}."
                       .format(rev_id, page_id))

    if window is not None and before is None:
        before = Timestamp(current_rev.rev_timestamp) + window

    # Load future revisions
    future_revs = list(n_edits_after(
        schema, rev_id, page_id, n=radius, before=before))

    return build_revert_tuple(
        rev_id, past_revs, current_rev, future_revs, radius)


def n_archived_edits_after(schema, rev_id, namespace, title,
                           timestamp, n, before=None):
    if before is not None:
        before_fmt = bytes(before.short_format(), 'utf8')
    else:
        before_fmt = bytes(Timestamp(time.time()).short_format(), 'utf8')
    with schema.transaction() as session:
        result = session.query(schema.archive).filter(
            and_(schema.archive.c.ar_namespace == namespace,
                 schema.archive.c.ar_title == title,
                 schema.archive.c.ar_rev_id > rev_id,
                 schema.archive.c.ar_timestamp >= bytes(timestamp.short_format(), 'utf8'),
                 schema.archive.c.ar_timestamp <= before_fmt)).order_by(
            schema.archive.c.ar_rev_id.asc()).limit(n)

        for row in result:
            yield row


def n_archived_edits_before(schema, rev_id, namespace, title,
                            timestamp, n, rvprop=None):
    with schema.transaction() as session:
        result = session.query(schema.archive).filter(
            and_(schema.archive.c.ar_namespace == namespace,
                 schema.archive.c.ar_title == title,
                 schema.archive.c.ar_timestamp < bytes(timestamp.short_format(), 'utf8'),
                 schema.archive.c.ar_rev_id < rev_id)).order_by(
            schema.archive.c.ar_rev_id.desc()).limit(n)

        # Reverse order because of the query pattern
        rows = reversed(list(result))
        for row in rows:
            yield row


def get_archived_namespace_title_and_timestamp(schema, rev_id):
    with schema.transaction() as session:
        row = session.query(
            schema.archive.c.ar_namespace,
            schema.archive.c.ar_title,
            schema.archive.c.ar_timestamp).filter(
            schema.archive.c.ar_rev_id == rev_id).first()

    return row[0], row[1], Timestamp(row[2])


def check_archive(schema, rev_id, namespace=None, title=None, timestamp=None,
                  radius=defaults.RADIUS,
                  before=None, window=None):
    """
    Checks the revert status of an archived revision (from a deleted page).
    With this method, you can determine whether an edit is a 'reverting'
    edit, was 'reverted' by another edit and/or was 'reverted_to' by
    another edit.

    :Parameters:
        session : :class:`mwapi.Session`
            An API session to make use of
        rev_id : int
            the ID of the revision to check
        namespace : int
            the namespace ID of the page the revision exists in
        title : str
            the title of the page the revision exists in
        timestamp : :class:`mwtypes.Timestamp`
            the timestamp that the revision for `rev_id` was saved
        radius : int
            a positive integer indicating the maximum number of revisions
            that can be reverted
        before : :class:`mwtypes.Timestamp`
            if set, limits the search for *reverting* revisions to those which
            were saved before this timestamp
        window : int
            if set, limits the search for *reverting* revisions to those which
            were saved within `window` seconds after the reverted edit
        rvprop : set( str )
            a set of properties to include in revisions

    :Returns:
        A triple :class:`mwreverts.Revert`

        * reverting -- If this edit reverted other edit(s)
        * reverted -- If this edit was reverted by another edit
        * reverted_to -- If this edit was reverted to by another edit

    """

    rev_id = int(rev_id)
    radius = int(radius)
    if radius < 1:
        raise TypeError("invalid radius.  Expected a positive integer.")

    namespace = int(namespace) if namespace is not None else None
    title = str(title) if title is not None else None
    timestamp = Timestamp(timestamp) if timestamp is not None else None
    before = Timestamp(before) if before is not None else None

    # If we don't have the page_id, we're going to need to look them up
    if namespace is None or title is None or timestamp is None:
        namespace, title, timestamp = \
            get_archived_namespace_title_and_timestamp(schema, rev_id)

    # Load history and current rev
    current_and_past_revs = list(n_archived_edits_before(
        schema, rev_id + 1, namespace, title, timestamp + 1, n=radius + 1))

    if len(current_and_past_revs) < 1:
        raise KeyError("Revision {0} not found in page {1}(ns={2}) @ {3}."
                       .format(rev_id, title, namespace, timestamp))

    current_rev, past_revs = (
        current_and_past_revs[-1],  # Current rev is the last one returned
        current_and_past_revs[:-1]  # The rest are past revs
    )
    if current_rev.ar_rev_id != rev_id:
        raise KeyError("Revision {0} not found in page {1}(ns={2}) @ {3}."
                       .format(rev_id, title, namespace, timestamp))

    if window is not None and before is None:
        before = Timestamp(current_rev.ar_timestamp) + window

    # Load future revisions
    future_revs = list(n_archived_edits_after(
        schema, rev_id, namespace, title, timestamp, n=radius, before=before))

    return build_revert_tuple(
        rev_id, past_revs, current_rev, future_revs, radius)


def build_revert_tuple(rev_id, past_revs, current_rev, future_revs, radius):
    # Convert to an iterable of (checksum, rev) pairs for detect() to consume
    checksum_revisions = chain(
        ((get_sha1(rev) or DummyChecksum(), rev)
         for rev in past_revs),
        [(get_sha1(current_rev) or DummyChecksum(), current_rev)],
        ((get_sha1(rev) or DummyChecksum(), rev)
         for rev in future_revs),
    )

    reverting, reverted, reverted_to = None, None, None
    for revert in detect(checksum_revisions, radius=radius):
        if reverting is None and get_rev_id(revert.reverting) == rev_id:
            reverting = revert

        if reverted is None and \
           rev_id in {get_rev_id(rev) for rev in revert.reverteds}:
            reverted = revert

        if reverted_to is None and get_rev_id(revert.reverted_to) == rev_id:
            reverted_to = revert

    return reverting, reverted, reverted_to


def get_rev_id(row):
    if hasattr(row, 'rev_id'):
        return row.rev_id
    else:
        return row.ar_rev_id


def get_sha1(row):
    if hasattr(row, 'rev_sha1'):
        return row.rev_sha1
    else:
        return row.ar_sha1
