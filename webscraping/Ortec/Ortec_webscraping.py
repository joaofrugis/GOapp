import pandas as pd
import googlemaps
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

cards = []

url = 'https://www.ortec-imoveis.com.br/comprar/sp/leme/valor-min_0/area-min_0/ordem-valor/resultado-crescente/quantidade-48/pagina/pagina-'
pages = 5
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

for i in range(1, pages + 1):
    print(">>>>>Loading Page ",i,".....")

    response = urlopen(url + str(i))

    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.find('div', {'class', 'imoveis'}).find_all('div', id=re.compile(r'\bitem'))

    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))

        id_anuncio = anuncio['id'].split('_')[-1]

        card = {}

        card['tipo'] = anuncio.find('h3', {'class':'tipo'}).get_text()

        card['endereco'] = anuncio.find('h4', {'class':'bairro'}).get_text() + ' - ' + anuncio.find('h4', {'class':'cidade'}).get_text()

        result = gmaps.geocode(card['endereco'].split('-')[0] + ',Leme,SP')
        card['lat'] = result[0]['geometry']['location']['lat']
        card['long'] = result[0]['geometry']['location']['lng']
        
        card['dormitorios'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Dormitórios'}).get_text().replace('-','0')

        card['banheiros'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Banheiros'}).get_text().replace('-','0')

        card['vagas'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Vagas'}).get_text().replace('-','0')

        card['area'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Área'}).get_text().replace('m²','')

        card['valor'] = anuncio.find('div', {'class':'valor'}).find('h5').get_text().replace('R$ ','').replace('.','').replace(',','.')

        card['url_anuncio'] = 'https://www.ortec-imoveis.com.br' + soup.find('div', {'id': 'lista'}).find('div', {'id': id_anuncio}).find('a')['href']

        count += 1
        cards.append(card)

df = pd.DataFrame(cards)
df.to_csv('./Ortec_data.csv', ';',index=False)