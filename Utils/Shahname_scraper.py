# Copyright 2024 alireza
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from bs4 import BeautifulSoup
import bs4
import requests
import time
import csv
import pandas as pd
import sys

BASE_URL = 'https://ganjoor.net/ferdousi/shahname/'


def main():
    shahname = get_shahname(BASE_URL)
    file_name = 'shahname.csv'
    print('\nDOWNLOAD COMPLETED\nWriting to file...\n')
    save_as_csv(shahname, file_name=file_name)
    df = pd.read_csv(file_name)
    print(df.head(10))
    print('COMPLETE')



def get_chapters(base_url):
    try:
        response = requests.get(base_url)
    except:
        return None
    if not response.ok:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    chapters = []
    for a in soup.find_all('a'):
        href = a.get('href')
        if href is None: continue
        if '/ferdousi/shahname/' not in a.get('href'): continue
        chapters.append(href.split('/')[-1])
    return chapters



def get_chapter_parts(chapter, base_url):
    try:
        response = requests.get(base_url + chapter)
    except:
        return None
    if not response.ok:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    parts = []
    for p in soup.find_all('p'):
        class_ = p.get('class')
        if class_ is None or 'poem-excerpt' not in class_: continue
        a = list(p.children)[0]
        a = a.get('href').split('/')[-1]
        parts.append(chapter + '/' + a)
    return parts


def get_poem(part, base_url):
    try:
        response = requests.get(base_url + part)
    except:
        return None
    if not response.ok:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    baits = []
    soup = soup.article
    for div in soup.find_all('div'):
        class_ = div.get('class')
        if class_ is None: continue
        if 'b' not in class_: continue
        mesra = [None, None]
        for c_div in list(div.children):
            if isinstance(c_div, bs4.element.NavigableString): 
                continue
            class_ = c_div.get('class')[0]
            if class_ is None: continue
            if class_ == 'm1': mesra[0] = list(c_div.children)[0].text
            elif class_ == 'm2': mesra[1] = list(c_div.children)[0].text
        baits.append(mesra)
    return baits



def get_shahname(base_url=BASE_URL):
    tries = 0
    while True:
        chapters = get_chapters(base_url)
        tries += 1
        if chapters is None:
            if tries == 1:
                print(f'\nConnection is not OK, trying again')
            time.sleep(3)
            continue
        break
    shahname = []
    ci = 0
    while ci < len(chapters):
        print(f'\nChapter {ci+1:>3} out of {len(chapters):>3}')
        tries = 0
        while True:
            parts = get_chapter_parts(chapters[ci], base_url)
            tries += 1
            if parts is None:
                if tries == 1:
                    print(f'\nConnection is not OK, trying again')
                time.sleep(3)
                continue
            break
            
        ch = []
        pi = 0
        while pi < len(parts):
            tries = 0
            while True:
                baits = get_poem(parts[pi], base_url)
                tries += 1
                if baits is None:
                    if tries == 1:
                        print(f'\n\t\tcould not download part {pi+1:>3}, trying again')
                    time.sleep(3)
                    continue
                break
            ch.append(baits)
            print(f'\r\t\tPart {pi+1:>3} out of {len(parts):>3} Completed{" ":>20}', end='')
            pi += 1
        ci += 1
        shahname.append(ch)
    return shahname


def save_as_csv(shahname, file_name='shahname.csv'):
    with open('shahname.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Chapter', 'Part', 'Bait', 'Mesra', 'Text'])
        for chapter in range(len(shahname)):
            for part in range(len(shahname[chapter])):
                for bait in range(len(shahname[chapter][part])):
                    m1, m2 = shahname[chapter][part][bait]
                    writer.writerow([chapter + 1, part + 1, bait + 1, 1, m1])
                    writer.writerow([chapter + 1, part + 1, bait + 1, 2, m2])



if __name__ == '__main__':
    main()