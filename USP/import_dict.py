import pandas as pd
import os
from pathlib import Path
import json

HERE = Path(__file__).parent.resolve()
DICTS = HERE.joinpath("dicts")
path = f'{HERE.joinpath("data/bioinfo.xlsx")}'
os.system(
    f"wget -O {path} https://docs.google.com/spreadsheets/d/e/2PACX-1vTaS91hLfWcTLdd7hlJbJsR1nMHWTvRYq-UyhgJdiocER35DtYu8rp_DpBv8bAO9Svb7QFR6Dn51i_G/pub?output=xlsx"
)

topics = pd.read_excel(HERE.joinpath("data/bioinfo.xlsx"), sheet_name="Tópicos")
people = pd.read_excel(HERE.joinpath("data/bioinfo.xlsx"), sheet_name="Pessoas")

people_dict = json.loads(DICTS.joinpath("people.json").read_text())
topics_dict = json.loads(DICTS.joinpath("topics.json").read_text())

for i, row in topics.iterrows():
    topics_dict[row["name"]] = str(row["wikidata_id"])

for i, row in people.iterrows():
    people_dict[row["name"]] = row["wikidata_id"]


DICTS.joinpath("people.json").write_text(
    json.dumps(people_dict, indent=4, sort_keys=True, ensure_ascii=False)
)

DICTS.joinpath("topics.json").write_text(
    json.dumps(topics_dict, indent=4, ensure_ascii=False)
)
