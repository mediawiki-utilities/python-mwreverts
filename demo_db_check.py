import mwreverts.db

import mwdb

enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
                     "?read_default_file=~/replica.my.cnf")


def format_revert(revert):
    if revert is None:
        return ""
    else:
        return " ".join([str(get_rev_id(revert.reverting)),
                         str([get_rev_id(r) for r in revert.reverteds]),
                         str(get_rev_id(revert.reverted_to))])

def get_rev_id(row):
    if hasattr(row, 'rev_id'):
        return row.rev_id
    else:
        return row.ar_rev_id

reverting, reverted, reverted_to = mwreverts.db.check(enwiki, 679778587)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.db.check(enwiki, reverted.reverting.rev_id)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.db.check(enwiki, reverting.reverted_to.rev_id)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")
print("Checking an archived edit")
print("---------------")


reverting, reverted, reverted_to = \
    mwreverts.db.check_archive(enwiki, 587400097)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.db.check_archive(enwiki, reverted.reverting.ar_rev_id)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.db.check_archive(enwiki, reverting.reverted_to.ar_rev_id)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))
