import pickle
from pathlib import Path
from parse import AcademicThesis
from dicts.all import dicts
from unicodedata import normalize
from wdcuration import render_qs_url

HERE = Path(__file__).parent.resolve()


def main():
    with open(f"{HERE}/picklefiles/thesis.pickle", "rb") as handle:
        parsed_thesis = pickle.load(handle)

    statements = ""
    for thesis in parsed_thesis:
        statements += get_statements_for_thesis(thesis)
    HERE.joinpath("quickstatements.qs").write_text(statements)


def get_statements_for_thesis(thesis):
    author_qid = dicts["people"].get(thesis.author)
    committee_tuples = [(name, dicts["people"][name]) for name in thesis.committee]
    topic_tuples = [
        (topic.strip(), dicts["topics"][topic.strip()]) for topic in thesis.topics
    ]

    uni_qid = dicts["institutions"][normalize("NFKD", thesis.university)]
    program_qid = dicts["institutions"][thesis.program]
    instance_qid = dicts["instances"][normalize("NFKD", thesis.degree)]

    # Hardcoded for USP
    publisher_qid = "Q113337576"
    statements = f"""
CREATE
LAST|Len|"{thesis.title_en}"
LAST|Den|"academic thesis"
LAST|Lpt|"{thesis.title_pt}"
LAST|Dpt|"{thesis.degree.lower()}"
LAST|P31|{instance_qid}
LAST|P123|{publisher_qid}
LAST|P1476|en:"{thesis.title_en}"
LAST|P1476|pt:"{thesis.title_pt}"
LAST|P50|{author_qid}|S854|"{thesis.href}"
LAST|P356|"{thesis.doi.upper()}"|S854|"{thesis.href}" 
LAST|P953|"{thesis.href}"|"S854|"{thesis.href}"
LAST|P577|{thesis.publication_date}|S854|"{thesis.href}"
LAST|P4101|{uni_qid}|P9945|{program_qid}|S854|"{thesis.href}"
"""
    if thesis.n_pages is not None:
        statements += f'LAST|P1104|{thesis.n_pages}|S854|"{thesis.href}"' + "\n"
    for tuple in committee_tuples:
        statements += (
            f'LAST|P9161|{tuple[1]}|S5997|"{tuple[0]}"|S854|"{thesis.href}"' + "\n"
        )
    for tuple in topic_tuples:
        if tuple[0] != "ambíguo":
            statements += (
                f'LAST|P921|{tuple[1]}|S5997|"{tuple[0]}"|S854|"{thesis.href}"' + "\n"
            )
    statements += f'{author_qid}|P1026|LAST|S854|"{thesis.href}"'
    return statements


if __name__ == "__main__":
    main()
