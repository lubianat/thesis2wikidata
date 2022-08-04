import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import unicodedata
from pathlib import Path
import pickle
import requests, PyPDF2, io
from tqdm import tqdm

HERE = Path(__file__).parent.resolve()


def main():
    url = "https://www.teses.usp.br/index.php?option=com_jumi&fileid=9&Itemid=159&lang=pt-br&id=95131&prog=95001&exp=0&pagina=1"
    a = requests.get(url)
    soup = BeautifulSoup(unicodedata.normalize("NFKD", a.text))
    n_pages = soup.find("div", class_="dadosLinha")
    n_pages = int(n_pages.text.split()[-1])
    list_of_thesis = []

    for i in tqdm(range(0, n_pages + 1)):
        url = f"https://www.teses.usp.br/index.php?option=com_jumi&fileid=9&Itemid=159&lang=pt-br&id=95131&prog=95001&exp=0&pagina={i}"
        a = requests.get(url)
        soup = BeautifulSoup(unicodedata.normalize("NFKD", a.text))
        list_elements = soup.find_all("div", class_="dadosLinha dadosCor2")

        for element in list_elements:
            new_thesis = AcademicThesis(university="Universidade de São Paulo")

            extract_basic_info(element, new_thesis)
            thesis_url = requests.get(new_thesis.href)
            soup = BeautifulSoup(unicodedata.normalize("NFKD", thesis_url.text))
            extract_advanced_info(soup, new_thesis)

            list_of_thesis.append(new_thesis)

    with open(f"{HERE}/picklefiles/thesis.pickle", "wb") as handle:
        pickle.dump(list_of_thesis, handle, protocol=pickle.HIGHEST_PROTOCOL)

    all_people = []
    for thesis in list_of_thesis:
        all_people.extend(thesis.committee)
        all_people.append(thesis.author)

    all_people = list(set(all_people))
    all_people.sort()
    HERE.joinpath("raw_curation_tables").joinpath("people.txt").write_text(
        "\n".join(all_people)
    )

    all_topics = []
    for thesis in list_of_thesis:
        all_topics.extend(thesis.topics)

    all_topics = list(set(all_topics))
    all_topics.sort()
    HERE.joinpath("raw_curation_tables").joinpath("topics.txt").write_text(
        "\n".join(all_topics)
    )


def extract_advanced_info(soup, new_thesis):
    box = soup.findAll(True, {"class": ["DocumentoTituloTexto", "DocumentoTexto"]})
    for i, a in enumerate(box):
        if box[i - 1].text == "Data de Publicação":
            new_thesis.publication_date = f"+{a.text}T00:00:00Z/11"
        if box[i - 1].text == "Documento":
            new_thesis.degree = a.text
        if box[i - 1].text == "DOI":
            new_thesis.doi = a.text
        if box[i - 1].text == "Banca examinadora":
            new_thesis.committee = clean_committee(a.text)
        if box[i - 1].text == "Palavras-chave em português":
            new_thesis.topics = clean_topic(a.text)
        if box[i - 1].text == "Título em inglês":
            new_thesis.title_en = a.text
        if box[i - 1].text == "Título em português":
            new_thesis.title_pt = a.text
    links = soup.find_all("a", href=True)
    for link in links:
        if link.has_attr("href"):
            if "pdf" in link["href"]:
                url = "https://teses.usp.br" + link["href"]
                response = requests.get(url)
                with io.BytesIO(response.content) as open_pdf_file:
                    read_pdf = PyPDF2.PdfFileReader(open_pdf_file)
                    num_pages = read_pdf.getNumPages()
                    if num_pages < 20:
                        continue
                    else:
                        new_thesis.n_pages = num_pages


def extract_basic_info(element, new_thesis):
    name = element.find("div", class_="dadosDocNome")
    names = name.text.split(", ")
    new_thesis.author = names[1].strip() + " " + names[0].strip()
    new_thesis.href = element.find("a", href=True)["href"]
    new_thesis.program = element.find("div", class_="dadosDocUnidade").text


def clean_topic(text):
    topic_list = text.split("\n")
    topic_list = [a for a in topic_list if a != ""]
    topic_list = [a.split("(")[0] for a in topic_list]
    return topic_list


def clean_committee(text):
    committee_list = text.split("\n")
    committee_list = [a for a in committee_list if a != ""]
    committee_list = [a.split("(")[0] for a in committee_list]
    committee_list = [a.split(", ")[1] + " " + a.split(", ")[0] for a in committee_list]
    return committee_list


@dataclass
class AcademicThesis:
    """Class for keeping track of each thesis."""

    href: str = ""
    author: str = ""
    committee: list = field(default_factory=list)
    topics: list = field(default_factory=list)
    n_pages: int = None

    title_pt: str = ""
    title_en: str = ""

    degree: str = ""
    university: str = ""
    program: str = ""
    publication_date: str = ""
    doi: str = ""


if __name__ == "__main__":
    main()
