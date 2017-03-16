"""
This library provides a set of utilities for detecting identity reverts in
revisioned content.

:Basic example:

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
from .detector import Detector, Revert
from .functions import detect
from .dummy_checksum import DummyChecksum
from .about import (__name__, __version__, __author__, __author_email__,
                    __description__, __license__, __url__)

__all__ = [Detector, Revert, detect, DummyChecksum,
           __name__, __version__, __author__, __author_email__,
           __description__, __license__, __url__]
