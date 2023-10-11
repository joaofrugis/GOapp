import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

cards = []

url = 'https://www.bethpivaimoveis.com.br/imoveis/a-venda/leme?pagina='
pages = 26

for i in range(1,pages + 1):    
    print(">>>>>Loading Page ",i,".....")

    req = Request(
        url=url + str(i), 
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    
    response = urlopen(req)

    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.findAll('div', {"class": "col-sm-12 col-lg-6 box-align"})
    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        card = {}
        
        card['tipo'] = anuncio.find('h3', {'class','card-text'}).get_text().split(' ')[0]

        card['endereco'] = anuncio.find('h2', {'class': 'card-title'}).get_text() + ' - Leme - SP'
        
        extra_infos = anuncio.findAll('div', {'class', 'value'})
        
        card['area'] = '0'
        card['dormitorios'] = '0'
        card['banheiros'] = '0'
        card['vagas'] = '0'
        for element in extra_infos:
            #Area
            if 'm²' in element.find('p').get_text():
                card['area'] = element.find('p').get_text().replace('.','').replace(',','.').replace('m²', '')

            #Dormitórios
            if 'quartos' in element.find('p').get_text():
                card['dormitorios'] = element.find('p').get_text().replace('quartos', '')
            
            #Banheiros
            if 'banheiros' in element.find('p').get_text():
                card['banheiros'] = element.find('p').get_text().replace('banheiros', '')
        
        card['valor'] = anuncio.find('span',{'class','h-money location'}).get_text().replace('R$ ','').replace('.','').replace(',','.')

        count += 1
        cards.append(card)
    
df = pd.DataFrame(cards)
df.to_csv('./Beth_Piva_data.csv', ';',index=False)
