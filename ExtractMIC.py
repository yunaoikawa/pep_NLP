import json
import requests

peptide_ids = []

# Read peptide ID from the local file
with open("dbaasp_Monomer_NoMod.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        peptide_ids.append(line.split("\t")[0])

print(peptide_ids[:10])

result = []

for peptide_id in peptide_ids:

    try:
        # Define the URL based on the peptide ID
        url = f"https://dbaasp.org/peptides/{peptide_id}"

        # Make an HTTP request to fetch JSON data
        response = requests.get(url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Load JSON data
            data = response.json()

            # Extract information for activities with activityMeasureValue as "MIC"
            mic_activities = []
            articles = data.get("articles", [])

            for article in articles:
                for activity in data.get("targetActivities", []):
                    if activity.get("activityMeasureValue") == "MIC":
                        mic_info = {
                            "PeptideID": peptide_id,  # Add the peptide ID to the result
                            "Sequence": data.get("sequence"),  # Add the sequence to the result
                            "Concentration": activity.get("concentration"),
                            "Unit": activity["unit"].get("name"),
                            "TargetSpecies": activity["targetSpecies"].get("name"),
                            "PubMedID": article.get("pubmed", {}).get("pubmedId", "")  # Extract PubMed ID
                        }
                        mic_activities.append(mic_info)

            result.extend(mic_activities)
            
    except (Exception, KeyboardInterrupt) as e:
        print(f"An error occurred: {e}")

# Define the output file name
output_file = "dbaasp_mic.tsv"

# Write the entire result to the output file in TSV format
with open(output_file, "w") as outfile:
    # Write header
    outfile.write("PeptideID\tSequence\tConcentration\tUnit\tTarget Species\tPubMedID\n")

    # Write data
    for mic_activity in result:
        outfile.write(f"{mic_activity['PeptideID']}\t{mic_activity['Sequence']}\t{mic_activity['Concentration']}\t{mic_activity['Unit']}\t{mic_activity['TargetSpecies']}\t{mic_activity['PubMedID']}\n")

print(f"Output written to {output_file}")