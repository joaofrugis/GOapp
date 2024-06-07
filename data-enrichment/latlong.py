import requests
import pandas as pd
import json
import googlemaps

file_to_enrich = '../webscraping/Ortec/Ortec_data.csv'
gmaps = googlemaps.Client(key='AIzaSyArMwSvnOgwWi68S80guZDdk9L5nHztvhQ')

df = pd.read_csv(file_to_enrich, delimiter=';')

lats = []
longs = []
for index, row in df.iterrows():
    address = row['endereco']
    street = ''
    number = ''
    neighboor = address.split('-')[0].strip()
    city = address.split('-')[1].strip()
    state = address.split('-')[2].strip()

    result = gmaps.geocode(neighboor + ',' + city + ',' + state)
    lats.append(result[0]['geometry']['location']['lat'])
    longs.append(result[0]['geometry']['location']['lng'])

print(lats)

df.insert(0,'lat', lats)
df.insert(0,'long', longs)
df.to_csv('./latLong.csv',';',index=False)