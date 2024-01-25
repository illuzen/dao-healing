import requests
import pandas as pd
from bs4 import BeautifulSoup
import json

min_strokes = 2
max_strokes = 29

links = set([])
missing_links = []

headers = {'Accept': '*/*', 'User-Agent': 'request'}

for strokes in range(min_strokes, max_strokes + 1):
    url = 'http://alternativehealing.org/{}_strokes_of_first_characters.htm'.format(strokes)
    html = requests.get(url, headers=headers).text
    # html.parser doesnt handle nested tables well, so we use lxml
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find('table', id='GenTable')
    if not table:
        tables = soup.find_all('table')
        filtered = [
            table for table in tables
            if table.find('tr') is not None and
            len(table.find('tr').find_all('th')) == 4
        ]

        if len(filtered) > 1:
            print('found {} strange tables for {}'.format(len(filtered), url))
            table = filtered[1]
        else:
            print('table not found for {}'.format(url))
            continue

    rows = table.find_all('tr')

    for row in rows:
        link = row.find('a')
        if link:
            href = link.get('href')
            if href:
                links.add(href.split('/')[-1])
            else:
                missing_links.append(row.text)
        else:
            missing_links.append(row.text)


print(links)

with open('./herb_links.json','w') as file:
    json.dump(obj=list(links), fp=file, indent=4)

with open('./missing_links.json','w') as file:
    json.dump(obj=missing_links, fp=file, indent=4)


#     print(url, table)

#     tables = soup.find_all('table')
#     table = tables[6]
#     row = table.find('tr')
#     if row:
#         print(len(row.find_all('th')))
#
#

#     filtered = [
#         table for table in tables
#         if table.find('tr') and
#         len(table.find('tr').find_all('th')) == 4
#     ]
#     print(url, len(filtered))


    # Extract rows from the table
#     rows = table.find_all('tr')

#     # Create a list to hold all the rows
#     data = []
#     for row in rows:
#         cols = row.find_all('td')
#         cols = [ele.text.strip() for ele in cols]
#         data.append([ele for ele in cols if ele])  # Get rid of empty values
#
#     df = pd.DataFrame(data)
#
#     print(df)

