import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
from datetime import date
import os

today = date.today()

# #Download sitemaps
print('Scrape started')
print('Downloading base sitemap')
sitemap_base = 'https://www.blokker.nl/sitemap_index.xml'
response = requests.get(sitemap_base)
with open('urls/base_xml.xml', 'wb') as file:
     file.write(response.content)

# #Create list product sitemaps
print('Create product list')
product_xml = []
df = pd.read_xml('urls/base_xml.xml')

df =  df[df['loc'].str.contains('product')]
df =  df['loc']

product_xml = df.values.tolist()

# #Download product sitemap
for link in product_xml:
    response = requests.get(link)
    df = pd.read_xml(link)
    df = df['loc']
    df.to_csv('data/product_urls.csv', index=False, mode='a')
    print('Done ' + link)

#Filter product listing
filter = ['mepal', 'rosti']
exclude_filter = ['lamp']

df =  pd.read_csv('data/product_urls.csv')
print(df.info())
df =  df.drop_duplicates()
print(df.info())
df_clean = df[df['loc'].str.contains('|'.join(filter))]
df_clean = df_clean[~df_clean['loc'].str.contains('|'.join(exclude_filter))]
print(df.info())

# Remover column header and index
df_clean.to_csv('data/products_clean.csv',index=False)

print(df_clean.info())

# #Scrape data
df = pd.read_csv('data/products_clean.csv')
links = df['loc'].tolist()

product_results = csv.writer(open(f'data/results_blokker_mepal_products.csv', 'a'))
product_results.writerow(['Date', 'EAN', 'Link', 'Brand', 'Price', 'Stock' ,'Category', 'Seller', 'offerType'])

# links = ['https://www.blokker.nl/mepal-beschuitdoos-stora---wit/1109480.html', 'https://www.blokker.nl/mepal-vleeswarendoos-modula-550%2F3---wit/1182000.html', 'https://www.blokker.nl/mepal-broodtrommel-campus-1-4-liter-lime/1827258.html']

for link in links:
    response = requests.get(link)
    soup = BeautifulSoup(response.content, 'html.parser')
    element = soup.find(id='gtm-tracking')
    #print(element.attrs['data-gtmproducts'])
    jsonData = json.loads(element.attrs['data-gtmproducts'])
    EAN = jsonData['ean']
    print(EAN)
    stock = jsonData['productAvailability']
    print(stock)
    price = jsonData['price']
    print(price)
    brand = jsonData['brand']
    print(brand)
    category = jsonData['categoryChuck']
    print(category)
    offer = jsonData['offerType']
    print(offer)
    seller_data = soup.find(class_='seller__name')
    seller_data = (seller_data.text.strip() if seller_data else "Geen waarde")
    product_results.writerow([today, EAN, link, brand, price, stock, category, seller_data, offer])

print('Scrape done!!')
