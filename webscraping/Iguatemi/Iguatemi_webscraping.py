import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup

cards = []

url = 'https://www.iguatemiimoveisleme.com.br/comprar/sp/leme/ordem-valor/resultado-crescente/quantidade-48/pagina'
pages = 10

for i in range(1, pages + 1):
    print(">>>>>Loading Page ",i,".....")

    response = urlopen(url + str(i))

    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    anuncios = soup.find('div', {"class": "imoveis"}).findAll('div', class_="info_imoveis")
    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        card = {}

        card['tipo'] = anuncio.find('h3', {'class':'tipo'}).get_text()

        card['endereco'] = anuncio.find('h4', {'class':'bairro'}).get_text() + ' - ' + anuncio.find('h4', {'class':'cidade'}).get_text()

        card['dormitorios'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Dormitórios'}).get_text().replace('-','0')

        card['banheiros'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Banheiros'}).get_text().replace('-','0')

        card['vagas'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Vagas'}).get_text().replace('-','0')

        card['area'] = anuncio.find('div', {'class':'detalhes'}).\
                                    find('div',{'title':'Área'}).get_text().replace('m²','')

        card['valor'] = anuncio.find('div', {'class':'valor'}).find('h5').get_text().replace('R$ ','').replace('.','').replace(',','.')

        count += 1  
        cards.append(card)


df = pd.DataFrame(cards)
df.to_csv('./Iguatemi_data.csv', ';',index=False)