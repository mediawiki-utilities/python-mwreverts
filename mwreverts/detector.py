from . import defaults
from .historical_dict import HistoricalDict
from .revert import Revert


class Detector(HistoricalDict):
    """
    Detects revert events in a stream of revisions (to the same page) based on
    matching checksums.  To detect reverts, construct an instance of this class
    and call :func:`~mwreverts.Detector.process` in chronological order.

    See https://meta.wikimedia.org/wiki/R:Identity_revert

    :Parameters:
        radius : int
            a positive integer indicating the maximum revision distance that a
            revert can span.

    :Example:
        >>> import mwreverts
        >>> detector = mwreverts.Detector()
        >>>
        >>> detector.process("aaa", {'rev_id': 1})
        >>> detector.process("bbb", {'rev_id': 2})
        >>> detector.process("aaa", {'rev_id': 3})
        Revert(reverting={'rev_id': 3},
               reverteds=[{'rev_id': 2}],
               reverted_to={'rev_id': 1})
        >>> detector.process("ccc", {'rev_id': 4})

    """

    def initialize(self, radius=defaults.RADIUS):
        if radius < 1:
            raise TypeError("invalid radius. Expected a positive integer.")

        super().initialize(maxsize=radius + 1)

    def process(self, checksum, revision=None):
        """
        Process a new revision and detect a revert if it occurred.  Note that
        you can pass whatever you like as `revision` and it will be returned in
        the case that a revert occurs.

        :Parameters:
            checksum : str
                Any identity-machable string-based hash of revision content
            revision : `mixed`
                Revision metadata.  Note that any data will just be returned
                in the case of a revert.

        :Returns:
            a :class:`~mwreverts.Revert` if one occured or `None`
        """
        revert = None

        if checksum in self:  # potential revert

            reverteds = list(self.up_to(checksum))

            if len(reverteds) > 0:  # If no reverted revisions, this is a noop
                revert = Revert(revision, reverteds, self[checksum])

        self.insert(checksum, revision)
        return revert
