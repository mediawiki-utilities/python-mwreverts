import mwapi
import mwreverts.api

session = mwapi.Session("https://en.wikipedia.org")


def print_revert(revert):
    if revert is None:
        print(None)
    else:
        print(revert.reverting['revid'],
              [r['revid'] for r in revert.reverteds],
              revert.reverted_to['revid'])

reverting, reverted, reverted_to = mwreverts.api.check(session, 679778587)
print_revert(reverting)
print_revert(reverted)
print_revert(reverted_to)
