"""
``$ mwpersistence revdocs2reverts -h``
::

    Extracts reverts from a page-partitioned sequence of JSON revision
    documents.

    Usage:
        revdocs2reverts (-h|--help)
        revdocs2reverts [<input-file>...] [--radius=<revs>] [--use-sha1]
                        [--threads=<num>] [--output=<path>] [--compress=<type>]
                        [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to file containing page-partitioned
                            JSON revision documents. [default: <stdin>]
        --radius=<revs>     The maximum number of revisions that a revert can
                            reference. [default: 15]
        --use-sha1          Use the sha1 field even if a text field is
                            available.
        --threads=<num>     If a collection of files are provided, how many
                            processor threads? [default: <cpu_count>]
        --output=<path>     Write output to a directory with one output file
                            per input path.  [default: <stdout>]
        --compress=<type>   If set, output written to the output-dir will be
                            compressed in this format. [default: bz2]
        --verbose           Print progress information to stderr.
        --debug             Print debug logs.
"""
import hashlib
import logging
import sys
from itertools import groupby

import mwcli

from .. import defaults
from ..detector import Detector

logger = logging.getLogger(__name__)


def process_args(args):

    return {'radius': int(args['--radius']),
            'use_sha1': bool(args['--use-sha1'])}


def revdocs2reverts(rev_docs, radius=defaults.RADIUS, use_sha1=False,
                    verbose=False):
    """
    Converts a sequence of page-partitioned revision documents into a sequence
    of reverts.

    :Params:
        rev_docs : `iterable` ( `dict` )
            a page-partitioned sequence of revision documents
        radius : `int`
            The maximum number of revisions that a revert can reference.
        use_sha1 : `bool`
            Use the sha1 field as the checksum for comparison.
        verbose : `bool`
            Print dots and stuff
    """

    page_rev_docs = groupby(rev_docs, lambda rd: rd['page'])

    for page_doc, rev_docs in page_rev_docs:
        if verbose:
            sys.stderr.write(page_doc['title'] + ": ")
            sys.stderr.flush()

        detector = Detector(radius=radius)
        for rev_doc in rev_docs:
            if not use_sha1 and 'text' not in rev_doc:
                logger.warn("Skipping {0}: 'text' field not found in {0}"
                            .format(rev_doc['id'], rev_doc))
                continue

            if use_sha1:
                checksum = rev_doc['sha1']
            elif 'text' in rev_doc:
                text_bytes = bytes(rev_doc['text'], 'utf8', 'replace')
                checksum = hashlib.sha1(text_bytes).digest()

            revert = detector.process(checksum, rev_doc)

            if revert:
                yield revert.to_json()
                if verbose:
                    sys.stderr.write("r")
                    sys.stderr.flush()
            else:
                if verbose:
                    sys.stderr.write(".")
                    sys.stderr.flush()

        if verbose:
            sys.stderr.write("\n")
            sys.stderr.flush()

streamer = mwcli.Streamer(
    __doc__,
    __name__,
    revdocs2reverts,
    process_args
)

main = streamer.main
