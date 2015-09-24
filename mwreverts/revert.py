import jsonable


class Revert(jsonable.Type):
    """
    Represents a revert event.  This class behaves like
    :class:`collections.namedtuple`.  Note that the datatypes of `reverting`,
    `reverteds` and `reverted_to` is not specified since those types will
    depend on the revision data provided during revert detection.

    :Attributes:
        **reverting**
            The reverting revision data : `mixed`
        **reverteds**
            The reverted revision data (ordered chronologically) :
            list( `mixed` )
        **reverted_to**
            The reverted-to revision data : `mixed`
    """
    __slots__ = ('reverting', 'reverteds', 'reverted_to')

    def initialize(self, reverting=None, reverteds=None, reverted_to=None):
        self.reverting = reverting
        self.reverteds = list(reverteds or [])
        self.reverted_to = reverted_to

    def __iter__(self):
        yield self.reverting
        yield self.reverteds
        yield self.reverted_to

    def __eq__(self, other):
        if isinstance(other, tuple):
            return tuple(self) == other

    def __getitem__(self, index):
        if index == 0:
            return self.reverting
        elif index == 1:
            return self.reverteds
        else:
            return self.reverted_to
