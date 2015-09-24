r"""
``$ mwpersistence dump2reverts -h``
::

    Extracts reverts from an XML dump.

    Usage:
        dump2reverts (-h|--help)
        dump2reverts [<input-file>...] [--radius=<num>] [--use-sha1]
                     [--threads=<num>] [--output=<path>] [--compress=<type>]
                     [--verbose] [--debug]

    Options:
        -h|--help           Print this documentation
        <input-file>        The path to file containing MediaWiki XML
                            [default: <stdin>]
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
        --verbose           Print dots and stuff to stderr
        --debug             Print debug logs.
"""
import mwcli
import mwxml
import mwxml.utilities

from .revdocs2reverts import process_args, revdocs2reverts


def dump2reverts(dump, **kwargs):
    docs = mwxml.utilities.dump2revdocs(dump)
    return revdocs2reverts(docs, **kwargs)

streamer = mwcli.Streamer(
    __doc__,
    __name__,
    dump2reverts,
    process_args,
    file_reader=mwxml.Dump.from_file
)

main = streamer.main
