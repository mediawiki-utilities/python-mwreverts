import mwreverts.db

import mwdb

enwiki = mwdb.Schema("mysql+pymysql://enwiki.labsdb/enwiki_p" +
                     "?read_default_file=~/replica.my.cnf")


def format_revert(revert):
    if revert is None:
        return ""
    else:
        return " ".join([str(revert.reverting.rev_id),
                         str([r.rev_id for r in revert.reverteds]),
                         str(revert.reverted_to.rev_id)])

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
