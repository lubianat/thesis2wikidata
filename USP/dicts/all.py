import json
from pathlib import Path
from unicodedata import normalize

__all__ = [
    "dicts",
]

HERE = Path(__file__).parent.resolve()
for path in HERE.glob("*.json"):
    print(path)

dicts = {
    path.stem: json.loads(normalize("NFKD", path.read_text()))
    for path in HERE.glob("*.json")
}
