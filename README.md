# thesis2wikidata

Parsing academic thesis repositories into Wikidata.

The USP folder contains code for reconciling the thesis of the bioinformatics program of the University of São Paulo to Wikidata. 

The workflow runs like this: 
* Metadata for the thesis are extracted from a source repository and saved in Python dataclasses. 
* Strings for committee members and thesis authors are uploaded to a Google Spreadsheet, where they are manually reconciled to Wikidata.
* Strings for topics are also added to a Google Spreadsheet and manually reconciled. 
* Via Quickstatements, the theses are created on Wikidata, containting the reconciled people and topics.


