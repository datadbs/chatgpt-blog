
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
        pgrr.append(title.get_text().replace('\r\n','').rstrip())
else : 
    print(response.status_code)

print(pgrr)
df = pd.DataFrame(pgrr, columns=['keyword'])
df['topic'] = '<<KEYWORD>>'
df['category'] = 'Stock'
df.to_csv('term.csv', index=False, encoding='utf-8-sig')