import pandas as pd
import numpy as np
import googlemaps
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from unidecode import unidecode
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

cards = []
pages = 2

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

for i in range(1,pages+1):
    driver = webdriver.Chrome(options=chrome_options)

    driver.get('https://www.zapimoveis.com.br/venda/imoveis/sp+leme/?__ab=exp-aa-test:control,new-discover-zap:alert,vas-officialstore-social:enabled,deduplication:select&transacao=venda&onde=,S%C3%A3o%20Paulo,Leme,,,,,city,BR%3ESao%20Paulo%3ENULL%3ELeme,-22.188945,-47.39678,&pagina=' + str(i))

    time.sleep(3)
    for _ in range(68):
        time.sleep(0.8)
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    html = driver.page_source

    driver.quit()

    soup = BeautifulSoup(html, 'html.parser')

    print(">>>>>Loading Page ",i,".....")
    
    anuncios = soup.findAll('div', {"data-position": True,'data-type': True})
    print('Encontrados ' + str(len(anuncios)) + ' anúncios na página ' + str(i)) 
    
    count = 0
    for anuncio in anuncios:
        time.sleep(1)
        print('Anuncio ' + str(count))
        if anuncio.find('a'): 
            url_anuncio = anuncio.find('a', href=True)['href']
            
            request = Request(
                url= url_anuncio,
                headers={'User-Agent': 'Mozilla/5.0'}
            )

            try: 
                html_content = urlopen(request).read().decode('utf-8')    
            except:
                continue

            html_content = urlopen(request).read().decode('utf-8')
            content = BeautifulSoup(html_content, 'html.parser')
            
            card = {}

            card['tipo'] = content.find('span', {"class": "info__business-type color-dark text-regular"}).get_text().split('para')[0].strip()

            card['endereco'] = content.find('span', {"class": "link"}).get_text().strip()

            result = gmaps.geocode(card['endereco'] + ',Leme,SP')
            card['lat'] = result[0]['geometry']['location']['lat']
            card['long'] = result[0]['geometry']['location']['lng']

            card['dormitorios'] = 0
            if content.find('span', {"itemprop": "numberOfRooms"}):
                card['dormitorios'] = content.find('span', {"itemprop": "numberOfRooms"}).get_text().strip().split(' ')[0]

            card['banheiros'] = 0
            if content.find('span', {"itemprop": "numberOfBathroomsTotal"}):
                card['banheiros'] = content.find('span', {"itemprop": "numberOfBathroomsTotal"}).get_text().strip().split(' ')[0]

            card['vagas'] = 0
            if content.find('li', {"class": "feature__item text-regular js-parking-spaces"}): 
                card['vagas'] = content.find('li', {"class": "feature__item text-regular js-parking-spaces"}).findAll('span')[1].get_text().strip().split(' ')[0]            

            card['area'] = 0
            if content.find('span', {"itemprop": "floorSize"}):
                card['area'] = content.find('span', {"itemprop": "floorSize"}).get_text().strip().split(' ')[0]
            
            card['valor'] = content.find('li', {'class': 'price__item--main text-regular text-regular__bolder'}).find('strong').get_text().split('R$')[1].strip().replace('.','').replace(',','.')

            card['url_anuncio'] = url_anuncio
            cards.append(card)
            count += 1
        else:
            id_anuncio = anuncio['data-position']
            driver = webdriver.Chrome(options=chrome_options)

            driver.get('https://www.zapimoveis.com.br/venda/imoveis/sp+leme/?__ab=exp-aa-test:control,new-discover-zap:alert,vas-officialstore-social:enabled,deduplication:select&transacao=venda&onde=,S%C3%A3o%20Paulo,Leme,,,,,city,BR%3ESao%20Paulo%3ENULL%3ELeme,-22.188945,-47.39678,&pagina=' + str(i))
            
            time.sleep(1)
            for _ in range(75):
                time.sleep(0.5)
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
                time.sleep(1)
            
            anuncio_multiplo = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-position="' + anuncio['data-position'] + '"]'))
            )
            anuncio_multiplo.click()

            time.sleep(2)
            soup_anuncio_multiplo = BeautifulSoup(driver.page_source, 'html.parser')

            links = soup_anuncio_multiplo.findAll('a', {'class': 'deduplication-card__anchor'})
            valores_imoveis = []
            for link in links:
                url_anuncio = link['href']
                id_card = link['data-id']
                valores_imoveis.append({id_card: float(link.find('div' , {"class", "listing-price"}).find('p').get_text().split(' ')[1].replace('.','').replace(',','.'))})

            menor_valor = float('inf')
            chave_valor = None

            for item in valores_imoveis:
                chave, valor = list(item.items())[0]

                if valor < menor_valor:
                    menor_valor = valor
                    chave_valor = chave
            
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'a[data-id="' + chave_valor + '"]'))
                )
            except:
                continue

            element.click()

            time.sleep(2)

            windows = driver.window_handles
            driver.switch_to.window(windows[-1])

            html_anuncio = driver.page_source

            driver.quit()

            content = BeautifulSoup(html_anuncio, 'html.parser')

            card = {}
            content.find('span', {"class": "info__business-type color-dark text-regular"})
            card['tipo'] = content.find('span', {"class": "info__business-type color-dark text-regular"}).get_text().split('para')[0].strip()

            card['endereco'] = content.find('span', {"class": "link"}).get_text().strip()

            card['dormitorios'] = 0
            if content.find('span', {"itemprop": "numberOfRooms"}):
                card['dormitorios'] = content.find('span', {"itemprop": "numberOfRooms"}).get_text().strip().split(' ')[0]

            card['banheiros'] = 0
            if content.find('span', {"itemprop": "numberOfBathroomsTotal"}):
                card['banheiros'] = content.find('span', {"itemprop": "numberOfBathroomsTotal"}).get_text().strip().split(' ')[0]

            card['vagas'] = 0
            if content.find('li', {"class": "feature__item text-regular js-parking-spaces"}): 
                card['vagas'] = content.find('li', {"class": "feature__item text-regular js-parking-spaces"}).findAll('span')[1].get_text().strip().split(' ')[0]            

            card['area'] = 0
            if content.find('span', {"itemprop": "floorSize"}):
                card['area'] = content.find('span', {"itemprop": "floorSize"}).get_text().strip().split(' ')[0]
            
            card['valor'] = content.find('li', {'class': 'price__item--main text-regular text-regular__bolder'}).find('strong').get_text().split('R$')[1].strip().replace('.','')

            card['url_anuncio'] = url_anuncio
            
            cards.append(card)
            count += 1
        
        df = pd.DataFrame(cards)    
        df.to_csv('./Zap_data.csv', ';',index=False)
    
        
df = pd.DataFrame(cards)
df.to_csv('./Zap_data.csv', ';',index=False)