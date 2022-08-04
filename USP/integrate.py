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

    thesis = parsed_thesis[0]
    author_qid = dicts["people"].get(thesis.author)
    committee_qids = [dicts["people"][name] for name in thesis.committee]
    print(dicts["topics"])
    print(dicts["topics"]["Extração de Informação"])
    topic_qids = [dicts["topics"][topic] for topic in thesis.topics]

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
    for qid in committee_qids:
        statements += f'LAST|P9161|{qid}|S854|"{thesis.href}"' + "\n"
    for qid in topic_qids:
        statements += f'LAST|P921|{qid}|S854|"{thesis.href}"' + "\n"
    print(thesis)
    statements += f'{author_qid}|P1026|LAST|S854|"{thesis.href}"'
    url = render_qs_url(statements)
    print(url)


if __name__ == "__main__":
    main()
