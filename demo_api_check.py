import mwapi
import mwapi.cli
import mwreverts.api

session = mwapi.Session("https://en.wikipedia.org")


def format_revert(revert):
    if revert is None:
        return ""
    else:
        return " ".join([str(revert.reverting['revid']),
                         str([r['revid'] for r in revert.reverteds]),
                         str(revert.reverted_to['revid'])])

reverting, reverted, reverted_to = mwreverts.api.check(session, 679778587)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.api.check(session, reverted.reverting['revid'])
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.api.check(session, reverting.reverted_to['revid'])
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")
print("Let's to detect from deleted edits")
print("---------------")

mwapi.cli.do_login(session, "English Wikipedia")
reverting, reverted, reverted_to = \
    mwreverts.api.check_deleted(session, 587400097)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.api.check_deleted(session, reverted.reverting['revid'])
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))

print("---------------")

reverting, reverted, reverted_to = \
    mwreverts.api.check_deleted(session, reverting.reverted_to['revid'])
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))
