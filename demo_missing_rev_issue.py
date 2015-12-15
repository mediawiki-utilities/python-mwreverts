import mwapi

import mwreverts.api

session = mwapi.Session("https://pt.wikipedia.org")


def format_revert(revert):
    if revert is None:
        return ""
    else:
        return " ".join([str(revert.reverting['revid']),
                         str([r['revid'] for r in revert.reverteds]),
                         str(revert.reverted_to['revid'])])

reverting, reverted, reverted_to = mwreverts.api.check(session, 39707330)
print("reverting:", format_revert(reverting))
print("reverted:", format_revert(reverted))
print("reverted_to:", format_revert(reverted_to))
