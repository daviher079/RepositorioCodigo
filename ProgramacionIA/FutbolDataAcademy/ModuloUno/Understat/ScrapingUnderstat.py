import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

baseUrl = 'https://understat.com/match/'
#match = str(input('Introduce el id del partido. '))
match = '22514'
#'22514'

url = baseUrl + match 

print('Url partido ' + url)

res = requests.get(url)
soup = BeautifulSoup(res.content, 'lxml')
scripts = soup.find_all('script')

goles = scripts[1].string

#Eliminar simbolos para solo tener datos
ind_start = goles.index("('")+2
ind_end = goles.index("')")

json_data = goles[ind_start:ind_end]
json_data = json_data.encode('utf8').decode('unicode_escape')

#convertir goles a formato JSON
data = json.loads(json_data)

x = []
y = []
xg = []
team = []
data_away = data['a']
data_home = data['h']

for index in range(len(data_home)):
    for key in data_home[index]:
        if key == 'x':
            x.append(data_home[index][key])
        if key == 'y':
            x.append(data_home[index][key])
        if key == 'xG':
            x.append(data_home[index][key])
        if key == 'h_team':
            x.append(data_home[index][key])
            

colName = ['x', 'y', 'xg', 'team']
df = pd.DataFrame ([x,y, xg, team], index = colName)
df = df.T

print(df)



