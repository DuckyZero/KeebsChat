import requests
from bs4 import BeautifulSoup

# Have to pip install lxml to work properly
# testLink = 'https://www.apexkeyboards.ca/collections/switches/products/alpacas'

baseurl = 'https://www.apexkeyboards.ca/'
productLink = []
switchList = []
tag = ''
output = []

def find_product(tag):
    r = requests.get('https://www.apexkeyboards.ca/collections/{}'.format(tag))
    soup = BeautifulSoup(r.content, 'lxml')
    product_list = soup.find_all('div', class_='grid-product__wrapper')

    for item in product_list:
        for link in item.find_all('a', href=True):
            # if-statement removes duplicate links
            if (baseurl + link['href']) not in productLink:
                productLink.append(baseurl + link['href'])
                # print(link['href'])

    for link in productLink:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'lxml')

        name = soup.find('h1', class_='product-single__title').text.strip()
        price = soup.find('span', class_='product-single__price').text.strip()

        productLink.clear()

        return "{} {} is one of many {} we have! Checkout ApexKeyboards for the full list.".format(name, price, tag)
