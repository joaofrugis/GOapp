import pandas as pd
import googlemaps
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

cards = []

url = 'https://www.biamoraesimoveis.com.br/imoveis/a-venda/leme'
pages = 5
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

for i in range(1,pages + 1):    
    print(">>>>>Loading Page ",i,".....")

    if i > 0:
        req = Request(
            url=url + '?pagina=' + str(i), 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
    
    response = urlopen(req)

    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.findAll('div', {"class": "card-with-buttons__footer"})
    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        card = {}

        card['tipo'] = anuncio.find('p', {'class':'card-with-buttons__title'}).get_text()

        card['endereco'] = anuncio.find('h2').get_text()

        result = gmaps.geocode(anuncio.find('h2').get_text().split('-')[0] + ',Leme,SP')
        card['lat'] = result[0]['geometry']['location']['lat']
        card['long'] = result[0]['geometry']['location']['lng']

        extra_infos = anuncio.findAll('li')

        #Dormitórios
        for element in extra_infos:
            if "Quartos" in str(element):
                card['dormitorios'] = element.get_text().split(' ')[0]
                break
            
        #Banheiros
        for element in extra_infos:
            if "Banheiros" in str(element):
                card['banheiros'] = element.get_text().split(' ')[0]
                break

        #Vaga
        for element in extra_infos:
            if "Vaga" in str(element):
                card['vagas'] = element.get_text().split(' ')[0]
                break

        #Area
        for element in extra_infos:
            if "m²" in str(element):
                card['area'] = element.get_text().replace(" ","").replace('m²','')
                break

        card['valor'] = anuncio.find('p', {'class':'card-with-buttons__value'}).get_text().split(' ')[1].replace('.','').replace(',','.')

        count += 1
        cards.append(card)

df = pd.DataFrame(cards)
df.to_csv('./Bia_Moraes_data.csv', ';',index=False)