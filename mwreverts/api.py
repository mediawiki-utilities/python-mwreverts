"""
This module provides a set of convenience function for detecting revert
status via a MediaWiki API.

.. autofunction:: check
"""

from itertools import chain

from mwtypes import Timestamp

from . import defaults
from .dummy_checksum import DummyChecksum
from .functions import detect


def n_edits_after(session, rev_id, page_id, n, timestamp=None, rvprop=None):
    doc = session.get(action='query', prop='revisions', pageids=page_id,
                      rvstartid=rev_id, rvend=timestamp, rvdir='newer',
                      rvlimit=n, rvprop=rvprop)

    page_doc = list(doc['query']['pages'].values())[0]
    revisions = page_doc.get('revisions', [])
    if 'revisions' in page_doc:
        del page_doc['revisions']
    for revision_doc in revisions:
        revision_doc['page'] = page_doc
        yield revision_doc


def n_edits_before(session, rev_id, page_id, n, timestamp=None, rvprop=None):
    doc = session.get(action='query', prop='revisions', pageids=page_id,
                      rvstartid=rev_id, rvend=timestamp, rvdir='older',
                      rvlimit=n, rvprop=rvprop)

    page_doc = list(doc['query']['pages'].values())[0]
    # Reverse order because of the query pattern
    revisions = reversed(page_doc.get('revisions', []))
    if 'revisions' in page_doc:
        del page_doc['revisions']
    for revision_doc in revisions:
        revision_doc['page'] = page_doc
        yield revision_doc


def get_page_id(session, rev_id):
    doc = session.get(action='query', prop='revisions', revids=rev_id,
                      rvprop=['ids'])

    if 'badrevids' in doc['query']:
        raise KeyError("Revision {0} not found.".format(rev_id))
    page_doc = list(doc['query']['pages'].values())[0]
    return page_doc['pageid']


def check(session, rev_id, page_id=None, radius=defaults.RADIUS,
          before=None, window=None, rvprop=None):
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

        >>> import mwapi
        >>> import mwreverts.api
        >>>
        >>> session = mwapi.Session("https://en.wikipedia.org")
        >>>
        >>> def print_revert(revert):
        ...     if revert is None:
        ...         print(None)
        ...     else:
        ...         print(revert.reverting['revid'],
        ...               [r['revid'] for r in revert.reverteds],
        ...               revert.reverted_to['revid'])
        ...
        >>> reverting, reverted, reverted_to = \
        ...     mwreverts.api.check(session, 679778587)
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

    rvprop = set(rvprop) if rvprop is not None else set()

    # If we don't have the page_id, we're going to need to look them up
    if page_id is None:
        page_id = get_page_id(session, rev_id)

    # Load history and current rev
    current_and_past_revs = list(n_edits_before(
        session,
        rev_id,
        page_id,
        n=radius + 1,
        rvprop={'ids', 'timestamp', 'sha1'} | rvprop
    ))

    if len(current_and_past_revs) < 1:
        raise KeyError("Revision {0} not found in page {1}."
                       .format(rev_id, page_id))

    current_rev, past_revs = (
        current_and_past_revs[-1],  # Current rev is the last one returned
        current_and_past_revs[:-1]  # The rest are past revs
    )
    if current_rev['revid'] != rev_id:
        raise KeyError("Revision {0} not found in page {1}."
                       .format(rev_id, page_id))

    if window is not None and before is None:
        before = Timestamp(current_rev['timestamp']) + window

    # Load future revisions
    future_revs = list(n_edits_after(
        session,
        rev_id + 1,
        page_id,
        n=radius,
        timestamp=before,
        rvprop={'ids', 'timestamp', 'sha1'} | rvprop
    ))

    # Convert to an iterable of (checksum, rev) pairs for detect() to consume
    checksum_revisions = chain(
        ((rev['sha1'] if 'sha1' in rev else DummyChecksum(), rev)
         for rev in past_revs),
        [(current_rev.get('sha1', DummyChecksum()), current_rev)],
        ((rev['sha1'] if 'sha1' in rev else DummyChecksum(), rev)
         for rev in future_revs),
    )

    reverting, reverted, reverted_to = None, None, None
    for revert in detect(checksum_revisions, radius=radius):
        if reverting is None and revert.reverting['revid'] == rev_id:
            reverting = revert

        if reverted is None and \
           rev_id in {rev['revid'] for rev in revert.reverteds}:
            reverted = revert

        if reverted_to is None and revert.reverted_to['revid'] == rev_id:
            reverted_to = revert

    return reverting, reverted, reverted_to
