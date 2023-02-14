
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np

url = 'https://securities.miraeasset.com/hki/hki3028/r01.do'

response = requests.get(url)

if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html)
    ul = soup.select_one('ul.result')
    titles = ul.select('li')
    pgrr=[]
    for title in titles:
        pgr=[]
        pgr.append(title.get_text().replace('\r\n','').rstrip())
        pgrr.append(pgr)
else : 
    print(response.status_code)

print(pgrr)
df = pd.DataFrame.from_records(pgrr)
df.to_excel('term.xlsx')