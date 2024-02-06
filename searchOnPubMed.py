#!usr/bin/env python3

import requests
import csv
from bs4 import BeautifulSoup
import time

# Read the TSV file
input_file = "dbaasp_mic.tsv"
output_file = "sequences_on_pubmed.tsv"

# List to store rows with Sequence found in HTML
filtered_rows = []
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 5.2; rv:2.0.1) Gecko/20100101 Firefox/4.0.1"}

def get_pmc_id(pubmed_id):
    url = f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        pmc_tag = soup.find(attrs={'data-pmc-id': True})
        if pmc_tag:
            return pmc_tag['data-pmc-id']
    return None

def get_pmc_xml(pmc_id):
    base_url = "https://www.ncbi.nlm.nih.gov/pmc/oai/oai.cgi"
    params = {
        "verb": "GetRecord",
        "metadataPrefix": "pmc",
        "identifier": f"oai:pubmedcentral.nih.gov:{pmc_id}"
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Error retrieving XML for PMC ID {pmc_id}. Status code: {response.status_code}")
        return None
    
def get_pmc_html(pmc_id):
    base_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/"
    url = f"{base_url}{pmc_id}/"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Error retrieving HTML for PMC ID {pmc_id}. Status code: {response.status_code}")
        return None

def check_sequence_in(html, sequence):
    soup = BeautifulSoup(html, 'lxml')
    body = soup.find("body")
    if body:
        return sequence in body.get_text()
    return False

try:
    with open(input_file, "r", newline="", encoding="utf-8") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        pubmed_id = ""
        html = None
        
        for row in reader:

            last_pubmed_id = pubmed_id
            peptide_id = row["PeptideID"]
            sequence = row["Sequence"]
            pubmed_id = row["PubMedID"]

            # Request HTML only if the PubMedID is different
            if last_pubmed_id != pubmed_id:
                time.sleep(1)

                pmc_id = get_pmc_id(pubmed_id)

                if pmc_id:
                    print(f"PMC ID for PubMed ID {pubmed_id}: {pmc_id}")

                    html = get_pmc_html(pmc_id)

            if html:
                if check_sequence_in(html, sequence):

                    row["PMC ID"] = pmc_id
                    filtered_rows.append(row)
                    print(f"Sequence {sequence} found in HTML content.")
                else:
                    print(f"PMC ID {sequence} is not present in the HTML content.")
except KeyboardInterrupt as e:
    print(f"Error: {e}")

# Write the filtered rows to the output file
header = ["PeptideID", "Sequence", "Concentration", "Unit", "Target Species", "PubMedID", "PMC ID"]
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=header, delimiter='\t')
    writer.writeheader()
    writer.writerows(filtered_rows)

print(f"Filtered rows written to {output_file}")