import pandas as pd
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup

cards = []

url = 'https://www.fenixleme.com.br/imovel/?&finalidade=venda&tipo=&cid=Leme&bairro=0&sui=&ban=&gar=&dor=&pag='
pages = 8

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

    anuncios = soup.findAll('div', {"class": "item-lista"})
    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        if anuncio.find('li').get_text() == 'Consulte':
            continue
        card = {}
        
        tipo = anuncio.find('small').get_text()
        if 'Ref' in tipo:
            tipo = tipo.replace(u'\xa0','-').split('---')[1].split(' ')[0]
        else:
            tipo = tipo.split(' ')[0]

        card['tipo'] = tipo

        card['endereco'] = anuncio.find('h3', {'class': 'cor2'}).get_text().replace('/', '-').replace(',',' -')
        
        extra_infos = anuncio.find('table').findAll('td')
        card['area'] = '0'
        card['dormitorios'] = '0'
        card['banheiros'] = '0'
        card['vagas'] = '0'
        for element in extra_infos:
            #Area
            if element.find('a', {'data-tooltip': 'Área'}):
                card['area'] = element.find('a', {'data-tooltip': 'Área'}).get_text().split(' ')[1].replace('.','').replace(',','.')

            #Dormitórios
            if element.find('a', {'data-tooltip': 'Dormitórios'}):
                card['dormitorios'] = element.find('a', {'data-tooltip': 'Dormitórios'}).get_text().strip()

            #Banheiros
            if element.find('a', {'data-tooltip': 'Banheiros'}):
                card['banheiros'] = element.find('a', {'data-tooltip': 'Banheiros'}).get_text().strip()
                        
            #Vagas
            if element.find('a', {'data-tooltip': 'Vagas'}):
                card['vagas'] = element.find('a', {'data-tooltip': 'Vagas'}).get_text().strip()


        card['valor'] = anuncio.find('li').get_text().split(' ')[1].replace('.','').replace(',','.')
        count += 1
        cards.append(card)
    
df = pd.DataFrame(cards)
df.to_csv('./Fenix_data.csv', ';',index=False)