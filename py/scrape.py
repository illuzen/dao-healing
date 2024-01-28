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

def clean_text(text):
    return re.sub(r'\s+', ' ', text.replace('\n', ' ')).strip()

def canonical_column(cell):
    clean = clean_text(cell.text)
    column = clean.lower()
    if 'actions' in column:
        return 'Actions & Indications - 主治'
    elif 'antidote' in column:
        return 'Antidote - 急救'
    elif 'biological' in column or 'botanical' in column or 'latin' in column or 'zoological' in column:
        return 'Latin Name - 拉丁名'
    elif 'caution' in column or 'beware' in column or 'contra-' in column or 'oxic' in column or 'warning' in column:
        return 'Contraindications / Toxicity - 毒素與禁忌'
    elif 'channel' in column:
        return 'Meridians Entered - 歸經'
    elif 'chemical' in column:
        return 'Chemical Ingredients - 化學成份'
    elif 'clinical' in column:
        return 'Clinical Application - 臨床應用'
    elif 'common name' in column:
        return 'Common Name - 英文名'
    elif 'commonly' in column:
        return 'Commonly Used Formulae - 常用配方'
    elif 'dosage' in column:
        return 'Daily Dosage - 每日用量'
    elif 'distribution' in column:
        return 'Distribution - 分佈'
    elif 'japanese' in column:
        return 'Japanese Name - 日語'
    elif 'korean' in column:
        return 'Korean Name - 韓語'
    elif 'medical' in column:
        return 'Medical Function - 藥理'
    elif 'modern' in column or 'present day' in column or 'recent' in column or 'today' in column:
        return 'Modern Application - 現代應用'
    elif 'note' in column or 'notice' in column:
        return 'Note - 註'
    elif 'other' in column:
        return 'Other Name - 別名'
    elif 'parts being' in column:
        return 'Parts Being Used - 應用部份'
    elif 'pharmaceutical' in column:
        return 'Pharmaceutical Name - 英文药名'
    elif 'pinyin' in column:
        return 'Pinyin - 拼音'
    elif 'prescription' in column:
        return 'Prescription Names - 處方名'
    elif 'cantonese' in column:
        return 'Cantonese - 粵語發音'
    elif 'characteristic' in column:
        return 'Properties / Characteristics - 性味'
    elif 'sample' in column:
        return 'Samples of Formulae - 處方舉例'
    return clean

def parse_herb_table(url, name, table):
    data = {}
    if name:
        data['Name'] = clean_text(name)
    if url:
        data['Original URL'] = url

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
                key = canonical_column(cells[0])
                if cells[1].find('table'):
                    data[key] = parse_herb_table('', '', cells[1].find('table'))
                else:
                    value = clean_text(cells[1].text)
                    if key and value:
                        data[key] = value
        elif len(cells) == 1:
            cells = cells[0].find_all('td')
            for i in range(0, len(cells), 2):
                key = canonical_column(cells[i])
                value = clean_text(cells[i+1].text)
                if key and value:
                    data[key] = value
        elif len(cells) == 2:
            key = canonical_column(cells[0])
            if cells[1].find('table'):
                data[key] = parse_herb_table('', '', cells[1].find('table'))
            else:
                value = clean_text(cells[1].text)
                if value:
                    data[key] = value
        elif len(cells) == 4:
            if contains_numbers(cells[1].text):
                key = canonical_column(cells[0])
                value = clean_text(cells[1].text)
                if key and value:
                    data[key] = value
                key = canonical_column(cells[2])
                value = clean_text(cells[3].text)
                if key and value:
                    data[key] = value
            else:
                key = '{} {}'.format(clean_text(cells[0].text), clean_text(cells[1].text))
                value = '{} {}'.format(clean_text(cells[2].text), clean_text(cells[3].text))
                if key and value:
                    data[key] = value

#     print(json.dumps(data, indent=4))
    return data

def get_name(url, soup):
    pinyin = url.split('/')[-1].split('.')[0].replace('_', ' ')
    pattern = re.compile(r'{}+\s*[\u4e00-\u9fff\s]+'.format(pinyin))
    # matches = re.findall(pattern, soup.text)
    # print(pinyin, matches)

    tags = soup.find_all(['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'bgcolor'])
    for tag in tags:
        match = pattern.search(tag.text.replace('﹐', ''))
        if match:
            print(url, match.group())
            return match.group()

    return pinyin

def get_herbs():
    no_tables = []
    herbs = []
    # urls = [
    #     'http://alternativehealing.org/cang_zhu.htm'
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
        name = get_name(url, soup)
        tables = soup.find_all('table')
        eligible = []
        for table in tables:
            row = table.find('tr')
            if row:
                cols = row.find_all('td', recursive=False)
                if (len(cols) == 2 and
                        'Complementary and Alternative' not in row.text and
                        'Search this' not in row.text) and len(row.find_all('img')) == 0:
                    eligible.append(table)

        if len(eligible) == 0:
            print("no eligible tables for {}".format(url))
            no_tables.append(url)
        elif len(eligible) == 1:
            herbs.append(parse_herb_table(url, name, eligible[0]))
        else:
            herbs.append(parse_herb_table(url, name, eligible[0]))
            # found = False
            # for table in eligible:
            #     if table.find('table'):
            #         herbs.append(parse_herb_table(url, name, table))
            #         found = True
            #         break
            # if not found:
            #     # just take the first one if they are not nested
            #     herbs.append(parse_herb_table(url, name, eligible[0]))

    with open('./missing_table.json','w') as file:
        json.dump(obj=no_tables, fp=file, indent=4)

    with open('./herbs.json','w') as file:
        json.dump(obj=herbs, fp=file, indent=4)

def to_csv():
    df = pd.read_json('./herbs.json')
    df.fillna('', inplace=True)
    print('{} columns, {} rows'.format(len(df.columns), len(df)))
    df.to_csv('./herbs.csv', index=False)

# get_herbs()
to_csv()