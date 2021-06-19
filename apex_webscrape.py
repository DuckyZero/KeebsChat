import requests
from bs4 import BeautifulSoup
import pandas as pd
# Have to pip install lxml to work properly

baseurl = 'https://www.apexkeyboards.ca/'
productLink = []
switchList = []

# for loop for multiple product pages
#for x in range(1,6):

r = requests.get('https://www.apexkeyboards.ca/collections/switches')
soup = BeautifulSoup(r.content, 'lxml')

productList = soup.find_all('div', class_='grid-product__wrapper')
#print(productList)

for item in productList:
    for link in item.find_all('a', href=True):
        # if-statement removes duplicate links
        if (baseurl + link['href']) not in productLink:
            productLink.append(baseurl + link['href'])
            #print(link['href'])


#testLink = 'https://www.apexkeyboards.ca/collections/switches/products/alpacas'


for link in productLink:
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'lxml')

    name = soup.find('h1', class_='product-single__title').text.strip()
    price = soup.find('span', class_='product-single__price').text.strip()

    switch = {
        'name': name,
        'price': price
    }
    #print(switch)
    switchList.append(switch)
    print('Saving: ', switch['name'])

# Transform our switch dictionary into a data frame
df = pd.DataFrame(switchList)
print(df.head(15))