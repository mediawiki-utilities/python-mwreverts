from . import defaults
from .detector import Detector


def detect(checksum_revisions, radius=defaults.RADIUS):
    """
    Detects reverts that occur in a sequence of revisions.  Note that,
    `revision` data meta will simply be returned in the case of a revert.

    This function serves as a convenience wrapper around calls to
    :class:`mwreverts.Detector`'s :func:`~mwreverts.Detector.process`
    method.

    :Parameters:
        checksum_revisions : `iterable` ( (checksum, revision) )
            an iterable over tuples of checksum and revision meta data
        radius : int
            a positive integer indicating the maximum revision distance that a
            revert can span.

    :Return:
        a iterator over :class:`mwreverts.Revert`

    :Example:
        >>> import mwreverts
        >>>
        >>> checksum_revisions = [
        ...     ("aaa", {'rev_id': 1}),
        ...     ("bbb", {'rev_id': 2}),
        ...     ("aaa", {'rev_id': 3}),
        ...     ("ccc", {'rev_id': 4})
        ... ]
        >>>
        >>> list(mwreverts.detect(checksum_revisions))
        [Revert(reverting={'rev_id': 3},
                reverteds=[{'rev_id': 2}],
                reverted_to={'rev_id': 1})]

    """

    revert_detector = Detector(radius)

    for checksum, revision in checksum_revisions:
        revert = revert_detector.process(checksum, revision)
        if revert is not None:
            yield revert
