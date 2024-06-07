import pandas as pd
import googlemaps
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

cards = []

url = 'https://www.olx.com.br/imoveis/venda/estado-sp/grande-campinas/leme'
pages = 3
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

req = Request(
    url=url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

for i in range(1,pages + 1):    
    print(">>>>>Loading Page ",i,".....")

    if i > 0:
        req = Request(
            url=url + '?o=' + str(i), 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
    
    response = urlopen(req)

    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.findAll('section', {"class": "olx-ad-card olx-ad-card--horizontal"})
    print(len(anuncios))

    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        
        new_url = soup.find('a' , {"class": "olx-ad-card__title-link"})['href']
        
        req = Request(
            url=new_url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )

        pagina_anuncio = urlopen(req)

        content = pagina_anuncio.read().decode('utf-8')
        new_soup = BeautifulSoup(content, 'html.parser')

        details = new_soup.findAll('div', {"class": "ad__sc-2h9gkk-0 uAcYO olx-container olx-container--outlined olx-d-flex"})
        
        card = {}

        tipo = soup.find('h2', {"class": "olx-text olx-text--title-small olx-text--block olx-ad-card__title olx-ad-card__title--horizontal"}).text.lower().split(' ')

        if 'apartamento' in tipo: 
            card['tipo'] = 'apartamento'
        
        if 'casa' in tipo or 'sobrado' in tipo:
            card['tipo'] = 'casa'

        if 'terreno' in tipo:
            card['tipo'] = 'terreno'
    
        card['endereco'] = new_soup.find('div', {"class": "olx-d-flex olx-fd-column"}).findAll('span')[0].text + ' ' + new_soup.find('div', {"class": "olx-d-flex olx-fd-column"}).findAll('span')[1].text

        for detail in details:
            span = detail.findAll('span')
            
            if 'Área' in span[0].text:
                card['area'] = span[1].text.replace(" ","").replace('m²','')

            if 'Quartos' in span[0].text:
                room = detail.find('a')
                card['dormitorios'] = room.text
            
            if 'Banheiros' in span[0].text:
                card['banheiros'] = span[1].text
            
            if 'Vagas' in span[0].text:
                card['vagas'] = span[1].text

        result = gmaps.geocode(new_soup.find('div', {"class": "olx-d-flex olx-fd-column"}).findAll('span')[0].text + ',Leme,SP')
        card['lat'] = result[0]['geometry']['location']['lat']
        card['long'] = result[0]['geometry']['location']['lng']

        card['valor'] = new_soup.find('span', {"class": "olx-text olx-text--title-large olx-text--block"}).text.replace('R$','').replace('.','').replace(',','.')

        card['url_anuncio'] = new_url
        count += 1
        cards.append(card)
        print(card)

df = pd.DataFrame(cards)
df.to_csv('./Olx_data.csv', ';',index=False)