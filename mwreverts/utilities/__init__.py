"""
This module implements a set of utilities for generating revert datasets from
the command-line.  When the mwreverts python package is installed, a
`mwreverts` utility should be available from the
command-line.  Run `mwreverts -h` for more information:


mwreverts dump2reverts
++++++++++++++++++++++
.. automodule:: mwreverts.utilities.dump2reverts
    :noindex:

mwreverts revdocs2reverts
+++++++++++++++++++++++++
.. automodule:: mwreverts.utilities.revdocs2reverts
    :noindex:

"""
from .dump2reverts import dump2reverts
from .revdocs2reverts import revdocs2reverts

__all__ = [dump2reverts, revdocs2reverts]
