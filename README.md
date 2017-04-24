[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.556790.svg)](https://doi.org/10.5281/zenodo.556790)

# MediaWiki reverts

This library provides a set of utilities for detecting reverting activity in
MediaWiki projects.

* **Installation:** ``pip install mwreverts``
* **Documentation:** https://pythonhosted.org/mwreverts
* **Repositiory:** https://github.com/mediawiki-utilities/python-mwreverts
* **License:** MIT

## Basic example

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

## Author
* Aaron Halfaker -- https://github.com/halfak

## Cite as
Aaron Halfaker. (2017). mediawiki-utilities/python-mwreverts: v0.1.4 [Data set]. Zenodo. http://doi.org/10.5281/zenodo.556790

## See also 
* https://meta.wikimedia.org/wiki/Research:Revert
