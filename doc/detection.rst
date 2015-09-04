Detection
=========

The primary purpose of this library is to provide facilities to aid in
detecting reverting activity.  You are provided with two options.  :func:`mwreverts.detect` takes an iterable of (checksum, revision_data)
pairs and returns an iterator of :class:`mwreverts.Revert`.  :class:`mwreverts.Detector`, on the other hand, provides a :func:`~mwreverts.Detector.process` method that allows you to process revisions one-at-a-time.

.. autofunction:: mwreverts.detect

.. autoclass:: mwreverts.Detector
  :members:

.. autoclass:: mwreverts.Revert
