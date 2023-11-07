import pandas as pd
import googlemaps
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

cards = []

url = 'https://www.rrsuacasa.com.br/imovel/?finalidade=venda&tipo=&cid=Leme&bairro=0&sui=&ban=&gar=&dor=&pag='
pages = 11
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

for i in range(1,pages + 1):    
    print(">>>>>Loading Page ",i,".....")

    req = Request(
        url=url + str(i), 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    response = urlopen(req)

    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.findAll('div', {"class": "imovelcard"})
    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        if (anuncio.get('style')):
            continue
    
        card = {}
        
        card['tipo'] = anuncio.find('p', {'class': 'imovelcard__info__ref'}).get_text().split('-')[1].strip()
        
        card['endereco'] = anuncio.find('h2', {'class': 'imovelcard__info__local'}).get_text().replace('/', '-').replace(',',' -')

        result = gmaps.geocode(card['endereco'].split('-')[0] + ',Leme,SP')
        card['lat'] = result[0]['geometry']['location']['lat']
        card['long'] = result[0]['geometry']['location']['lng']

        extra_infos = anuncio.findAll('div', {'class', 'imovelcard__info__feature'})
        card['area'] = '0'
        card['dormitorios'] = '0'
        card['banheiros'] = '0'
        card['vagas'] = '0'
        for element in extra_infos:
            #Area
            if element.find('i', {'class': 'fa fa-arrows-h'}):
                card['area'] = element.find('b').get_text().split(' ')[0].replace('.','').replace(',','.')

            #Dormitórios
            if element.find('i', {'class': 'fa fa-bed'}):
                card['dormitorios'] = element.find('b').get_text().strip()

            #Banheiros
            if element.find('i', {'class': 'fa fa-shower'}):
                card['banheiros'] = element.find('b').get_text()
                        
            #Vagas
            if element.find('i', {'class': 'fa fa-car'}):
                card['vagas'] = element.find('b').get_text()

        
        card['valor'] = anuncio.find('div', {'class': 'col imovelcard__valor'}).find('p', {'class' , 'imovelcard__valor__valor'}).get_text().split(' ')[1].replace('.','').replace(',','.')
        
        card['url_anuncio'] = 'https://www.rrsuacasa.com.br' + anuncio.find('a')['href']
        count += 1
        cards.append(card)

df = pd.DataFrame(cards)
df.to_csv('./RR_data.csv', ';',index=False)