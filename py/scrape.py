import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import re

headers = {'Accept': '*/*', 'User-Agent': 'request'}

def get_herb_links():
    links = set([])
    missing_links = []
    min_strokes = 2
    max_strokes = 29


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

def contains_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def clean_text(cell):
    return re.sub(r'\s+', ' ', cell.text.replace('\n', ' ')).strip()

def parse_herb_table(table):
    data = {}
    # remove the irrelevant bgcolor tags
    for tag in table.find_all('bgcolor'):
        tag.unwrap()
    rows = table.find_all('tr', recursive=False)
    for row in rows:
        cells = row.find_all('td', recursive=False)
        if len(cells) == 0:
            # try non-recursive
            cells = row.find_all('td', recursive=True)
            if len(cells) == 0:
                print('bad row: {}'.format(row))
            else:
                key = clean_text(cells[0])
                if cells[1].find('table'):
                    data[key] = parse_herb_table(cells[1].find('table'))
                else:
                    value = clean_text(cells[1])
                    if value:
                        data[key] = value
        elif len(cells) == 1:
            cells = cells[0].find_all('td')
            for i in range(0, len(cells), 2):
                key = clean_text(cells[i])
                value = clean_text(cells[i+1])
                if value:
                    data[key] = value
        elif len(cells) == 2:
            key = clean_text(cells[0])
            if cells[1].find('table'):
                data[key] = parse_herb_table(cells[1].find('table'))
            else:
                value = clean_text(cells[1])
                if value:
                    data[key] = value
        elif len(cells) == 4:
            if contains_numbers(cells[1].text):
                key = clean_text(cells[0])
                value = clean_text(cells[1])
                if value:
                    data[key] = value
                key = clean_text(cells[2])
                value = clean_text(cells[3])
                if value:
                    data[key] = value
            else:
                key = '{} {}'.format(clean_text(cells[0]), clean_text(cells[1]))
                value = '{} {}'.format(clean_text(cells[2]), clean_text(cells[3]))
                if value:
                    data[key] = value

#     print(json.dumps(data, indent=4))
    return data


def get_herbs():
    no_tables = []
    herbs = []
    # urls = [
    #     'http://alternativehealing.org/gan_cao.htm'
    # ]
    urls = [
        'http://alternativehealing.org/{}'.format(path)
        for path in json.load(open('./herb_links.json', 'r'))
    ]
    print(urls)

    for url in urls:
        response = requests.get(url, headers=headers)
        print(url)

        if response.status_code != 200:
            print("bad url: {}".format(url))
            continue

        html = response.text
        html = html[:-20].replace("</html>", "", 1) + html[-20:]
        soup = BeautifulSoup(html, 'lxml')
        tables = soup.find_all('table')
        eligible = []
        for table in tables:
            row = table.find('tr')
            if row:
                cols = row.find_all('td', recursive=False)
                if (len(cols) == 2 and
                        'Complementary and Alternative' not in row.text and
                        'Search this site' not in row.text) and len(row.find_all('img')) == 0:
                    eligible.append(table)

        if len(eligible) == 0:
            print("no eligible tables for {}".format(url))
            no_tables.append(url)
        elif len(eligible) == 1:
            herbs.append(parse_herb_table(eligible[0]))
        else:
            found = False
            for table in eligible:
                if table.find('table'):
                    herbs.append(parse_herb_table(table))
                    found = True
                    break
            if not found:
                # just take the first one if they are not nested
                herbs.append(parse_herb_table(eligible[0]))

    with open('./missing_table.json','w') as file:
        json.dump(obj=no_tables, fp=file, indent=4)

    with open('./herbs.json','w') as file:
        json.dump(obj=herbs, fp=file, indent=4)


get_herbs()