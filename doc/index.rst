MediaWiki Reverts
=================
This library provides a set of utilities for detecting reverts (see :class:`mwreverts.Detector` and :func:`mwreverts.detect`) and identifying
the reverted status of edits to a MediaWiki wiki.

There's also revert status checking functions for the API (see :func:`mwreverts.api.check` and :func:`mwreverts.api.check_deleted`) and database (see :func:`mwreverts.db.check` and :func:`mwreverts.db.check_archive`)

:Installation: ``pip install mwreverts``
:Repository: https://github.com/mediawiki-utilities/python-mwreverts


Contents
--------

.. toctree::
   :maxdepth: 2

   detection
   api
   db

Authors
-------
* Aaron Halfaker -- https://github.com/halfak


.. code::

  MIT LICENSE

  Copyright (c) 2015 Aaron Halfaker

  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files (the "Software"), to deal
  in the Software without restriction, including without limitation the rights
  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
  copies of the Software, and to permit persons to whom the Software is
  furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
