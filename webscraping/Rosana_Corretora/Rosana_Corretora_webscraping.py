import pandas as pd
import googlemaps
import time
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

cards = []

url = 'https://rosanamoreiracorretora.com.br/imoveis/Tipo-de-negocio/Tipo-de-imovel/Leme/Bairro/Minimo/Maximo/Codigo/Quartos_Garagem'
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

next_button_enabled = soup.find('a',{'class': 'btn btn-block btn-theme next'})
next_button = driver.find_element(By.ID, 'proximo')
stop_condition = True
count_page = 1
while stop_condition:
    time.sleep(4)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    print(">>>>>Loading Page ",count_page,".....")
    if (count_page == 1):
        anuncios = soup.findAll('div', {"class": "property2 property-list hoverflash"})
    else:
        anuncios = soup.findAll('div', {"class": "property2 property-list"})

    count = 1
    for anuncio in anuncios:
        print('Anuncio ' + str(count))
        
        card = {}
        
        card['tipo'] = anuncio.find('span', {'class': 'property-title'}).get_text().split('/')[1].strip()

        card['endereco'] = anuncio.find('div', {'class', 'property-location'}).get_text().replace(u'\n','').strip()

        result = gmaps.geocode(card['endereco'].split('/')[0].replace('Leme','') + ',Leme,SP')
        card['lat'] = result[0]['geometry']['location']['lat']
        card['long'] = result[0]['geometry']['location']['lng']

        extra_infos = anuncio.findAll('div', {'class', 'col-xs-3 col-lg-3 col-sm-3 col-md-3'})

        card['area'] = '0'
        card['dormitorios'] = '0'
        card['banheiros'] = '0'
        card['vagas'] = '0'
        for element in extra_infos:
            if element.find('div', {'class': 'property-more-info-title'}).get_text() == 'Área':
                card['area'] = element.find('div', {'class': 'property-more-info-data'}).get_text().replace(u'\n','').replace('.','').replace(',','.').replace('--','0').strip()
            
            if element.find('div', {'class': 'property-more-info-title'}).get_text() == 'Quartos':
                card['dormitorios'] = element.find('div', {'class', 'property-more-info-data'}).get_text().replace('--','0')
            
            if element.find('div', {'class': 'property-more-info-title'}).get_text() == 'Banheiros':
                card['banheiros'] = element.find('div', {'class', 'property-more-info-data'}).get_text().replace('--','0')

            if element.find('div', {'class': 'property-more-info-title'}).get_text() == 'Vagas':
                card['vagas'] = element.find('div', {'class', 'property-more-info-data'}).get_text().replace('--','0')

        card['valor'] = anuncio.find('div', {'class', 'property-price'}).get_text().replace(u'\n','').split('C')[0].replace('R$ ','').replace('.','').replace(',','.').strip()
        
        card['url_anuncio'] = anuncio.find('a')['href']
        count += 1
        cards.append(card)
    if count_page == 31:
        stop_condition = False
    else:
        count_page += 1
        next_button.click()
    
driver.quit()
df = pd.DataFrame(cards)
df.to_csv('./Rosana_Corretora_data.csv', ';',index=False)
