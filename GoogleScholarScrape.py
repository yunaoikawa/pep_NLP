#!usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import time

output_file = "google_scholar_links.txt"
urls = []
"""
synonyms = ["unnatural", "uncanonical", "non+natural", "non+canonical", "non+standard", "non+proteinogenic"]
for synonym in synonyms:
    urls.append(f"https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q={synonym}+antimicrob+%22amino+acid%22+MIC&btnG=")

    try:
        for i in range(10, 6000, 10):
            urls.append(f"https://scholar.google.com/scholar?start={i}&q=non+natural+antimicrob+%22amino+acid%22&hl=en&as_sdt=0,5")

    except (Exception, KeyboardInterrupt) as e:
        print(f"An error occurred while fetching the URL: {e}")

urls = list(set(urls))
"""
urls.append("https://scholar.google.com/scholar?&q=antimicrob+D-amino+acid+MIC&btnG=")
for i in range(10, 6000, 10):
    urls.append(f"https://scholar.google.com/scholar?start={i}&q=antimicrob+D-amino+acid+MIC&btnG=")

papers = []
# Fetch the HTML content from the URL
for url in urls:
    print(f"Fetching URL: {url}")
    try:
        response = requests.get(url)
        print("response: ", response)
        html_content = response.text

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        href_list = [element.find('a')['href'] for element in soup.find_all('h3', class_='gs_rt') if element.find('a').has_attr('href')]

        print(f"Found {len(href_list)} papers")
        # Insert the href_list into the papers list
        papers.extend(href_list)

        time.sleep(3)

    except (Exception, KeyboardInterrupt) as e:
        print(f"An error occurred while fetching the URL: {e}")

links = list(set(papers))

# Print the list of (id, href) pairs
with open(output_file, 'w') as file_out:
    for link in links:
        file_out.write(f"{link}\n")