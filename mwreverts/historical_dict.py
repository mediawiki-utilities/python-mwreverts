from collections import deque

import jsonable


class HistoricalDict(jsonable.Type, dict):
    '''
    A datastructure for efficiently storing and retrieving a
    limited number of records based on keys.
    '''
    __slots__ = ('maxsize', 'history')

    def initialize(self, maxsize, history=None):
        '''size specifies the maximum amount of history to keep'''
        super().__init__()

        self.maxsize = int(maxsize)
        self.history = deque(maxlen=self.maxsize)  # Preserves order history

        # If `items` are specified, then initialize with them
        if history is not None:
            for key, value in history:
                self.insert(key, value)

    def __setitem__(self, key, value):
        self.insert(key, value)

    def insert(self, key, value):
        '''Adds a new key-value pair. Returns any discarded values.'''

        # Add to history and catch expectorate
        if len(self.history) == self.maxsize:
            expectorate = self.history[0]
        else:
            expectorate = None

        self.history.append((key, value))

        # Add to the appropriate list of values
        if key in self:
            super().__getitem__(key).append(value)
        else:
            super().__setitem__(key, [value])

        # Clean up old values
        if expectorate is not None:
            old_key, old_value = expectorate
            super().__getitem__(old_key).pop(0)
            if len(super().__getitem__(old_key)) == 0:
                super().__delitem__(old_key)

            return (old_key, old_value)

    def __getitem__(self, key):
        if key in self:
            return super().__getitem__(key)[-1]
        else:
            raise KeyError(key)

    def up_to(self, key):
        '''Gets the recently inserted values up to a key'''
        for okey, ovalue in reversed(self.history):
            if okey == key:
                break
            else:
                yield ovalue

    def last(self):
        return self.history[-1]

    def __eq__(self, other):
        if not hasattr(other, "history"):
            return False
        else:
            return self.history == other.history
