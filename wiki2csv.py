import argparse
from bs4 import BeautifulSoup
import requests
import  re
import os
import csv


def cleanHTML(s):
    s1 = re.sub(r'<(?!sup|/sup).*?>', '', s)
    s2 = re.sub('\n', ' ', s1)
    #s3 = re.sub(r'\[[0-9]+\]', '', s2)
    s3 = re.sub(r'<.*?>\[.*?\]<.*?>', '', s2)
    s4 = re.sub(r'^&#160;','', s3 )
    s5 = re.sub(r'\\x[0-9a-f]{2}', '', s4)
    s6 = re.sub(u'\xa0', ' ', s5)

    return s6

def transformTable(t):
    data = {}
    data['headers'] = [ th.text.strip() for th in t.select("tr th") ]
    data['content'] = []
    for row in t.find_all('tr'):
        r_ = []
        for td in row.find_all('td'):
            line = cleanHTML(td.text).strip()
            r_.append(line)
        if len(r_) > 0:
            data['content'].append(r_)
    return data

parser = argparse.ArgumentParser()

parser.add_argument(dest='wikiurl', help='URL containing Wikipedia links')

parser.add_argument('-n',
        type=str,
        dest='tabname',
        help='Table prefix')

parser.add_argument('-d',
        type=str,
        dest='directory',
        help='Directory to save CSV files')

args = parser.parse_args()
wikiurl = args.wikiurl

try:
    html_doc = requests.get(wikiurl).content
except (NewConnectionError, MissingSchema):
    print(f"Can't conect to {wikiurl}, check your connection and try again")
    exit(-1)

soup = BeautifulSoup(html_doc, 'html.parser')


if args.tabname:
    prefix = args.tabname
else:
    cbody = soup.find('body').get('class')
    for i in cbody:
        if i.startswith('page-'):
            prefix = re.sub(r'^page-', '', i)

if args.directory:
    directory = args.directory
else:
    directory = os.path.dirname(os.path.realpath(__file__))
if  os.path.isdir(directory) == False:
    #print('Directory doesn't exist, exiting)
    exit(5)
elif os.access(directory, os.W_OK) == False:
    #print(Can't write on directory, exiting)
    exit(6)

tables = soup.find_all('table', {'class': 'wikitable sortable'})
if len(tables) == 0:
    exit(7)

if __name__ == '__main__':
    count = 1
    for table in tables:
        filename = prefix+str(count)+'.csv'
        with open(directory+ '/' + filename, 'w') as f:
            wr = csv.writer(f)
            wr.writerow(transformTable(table)['headers'])
            for l in transformTable(table)['content']:
                wr.writerow(l)
        count = count + 1
