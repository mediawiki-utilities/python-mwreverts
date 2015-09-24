import mwcli

router = mwcli.Router(
    "mwreverts",
    "A set of utilities for detecting reverting activity in " +
        " MediaWiki projects.",
    {'dump2reverts': "Extracts reverts from historical XML dumps",
     'revdocs2reverts': "Extracts reverts from page-partitioned revision " +
                        "documents."}
)

main = router.main
