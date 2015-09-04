from collections import namedtuple

Revert = namedtuple("Revert", ['reverting', 'reverteds', 'reverted_to'])
"""
Represents a revert event.  This class behaves like
:class:`collections.namedtuple`.  Note that the datatypes of `reverting`,
`reverteds` and `reverted_to` is not specified since those types will depend
on the revision data provided during revert detection.

:Attributes:
    **reverting**
        The reverting revision data : `mixed`
    **reverteds**
        The reverted revision data (ordered chronologically) : list( `mixed` )
    **reverted_to**
        The reverted-to revision data : `mixed`
"""
