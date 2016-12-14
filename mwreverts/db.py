"""
This module provides a set of convenience function for detecting revert
status via a mwdb database connection.

.. autofunction:: check
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
        before_fmt = before.short_format()
    else:
        before_fmt = Timestamp(time.time()).short_format()
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
        >>> reverting, reverted, reverted_to = \
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

    # Convert to an iterable of (checksum, rev) pairs for detect() to consume
    checksum_revisions = chain(
        ((rev.rev_sha1 or DummyChecksum(), rev)
         for rev in past_revs),
        [(current_rev.rev_sha1 or DummyChecksum(), current_rev)],
        ((rev.rev_sha1 or DummyChecksum(), rev)
         for rev in future_revs),
    )

    reverting, reverted, reverted_to = None, None, None
    for revert in detect(checksum_revisions, radius=radius):
        if reverting is None and revert.reverting.rev_id == rev_id:
            reverting = revert

        if reverted is None and \
           rev_id in {rev.rev_id for rev in revert.reverteds}:
            reverted = revert

        if reverted_to is None and revert.reverted_to.rev_id == rev_id:
            reverted_to = revert

    return reverting, reverted, reverted_to
