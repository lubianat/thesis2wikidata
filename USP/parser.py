import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, field
import unicodedata


def main():
    url = "https://www.teses.usp.br/index.php?option=com_jumi&fileid=19&Itemid=87&lang=pt-br&g=1&b7=Bioinform%C3%A1tica&c7=c&o7"
    a = requests.get(url)
    soup = BeautifulSoup(unicodedata.normalize("NFKD", a.text))
    list_elements = soup.find_all("div", class_="dadosLinha dadosCor2")

    @dataclass
    class AcademicThesis:
        """Class for keeping track of each thesis."""

        href: str = ""
        author: str = ""
        committee: list = field(default_factory=list)
        topics: list = field(default_factory=list)

        title: str = ""
        degree: str = ""
        university: str = ""
        program: str = ""
        publication_date: str = ""
        doi: str = ""

    list_of_thesis = []
    for element in list_elements:
        new_thesis = AcademicThesis(university="Universidade de São Paulo")

        name = element.find("div", class_="dadosDocNome")
        names = name.text.split(", ")
        new_thesis.author = names[1] + " " + names[0]
        new_thesis.href = element.find("a", href=True)["href"]
        new_thesis.title = element.find("div", class_="dadosDocTitulo").text
        new_thesis.program = element.find("div", class_="dadosDocUnidade").text

        thesis_url = requests.get(new_thesis.href)
        soup = BeautifulSoup(unicodedata.normalize("NFKD", thesis_url.text))
        box = soup.findAll(True, {"class": ["DocumentoTituloTexto", "DocumentoTexto"]})
        for i, a in enumerate(box):
            if box[i - 1].text == "Data de Publicação":
                new_thesis.publication_date = a.text
            if box[i - 1].text == "Documento":
                new_thesis.degree = a.text
            if box[i - 1].text == "DOI":
                new_thesis.doi = a.text
            if box[i - 1].text == "Banca examinadora":
                new_thesis.committee = clean_committee(a.text)
            if box[i - 1].text == "Palavras-chave em português":
                new_thesis.topics = clean_topic(a.text)
        list_of_thesis.append(new_thesis)
    print(list_of_thesis)


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


if __name__ == "__main__":
    main()
