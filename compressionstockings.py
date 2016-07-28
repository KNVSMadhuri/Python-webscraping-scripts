from __future__ import division
from bs4 import BeautifulSoup
import math
import urllib2
import traceback
import logging
import sys
import csv
import re
import time
import random
from time import strftime

__author__ = "Apoorva Kumar G"
__copyright__ = "Copyright 2016, Affine Analytics"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "YOU, IF you opened this file ;)"
__email__ = "apoorva.kumar@affineanalytics.com"
__status__ = "still in development"

if __name__ == '__main__':
    outputpathBasic = sys.argv[1]
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    handler = logging.FileHandler(outputpathBasic + '/CompressionStock-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    fileWriter = csv.writer(open(outputpathBasic + "/CompressionStockings_Product_Details1.csv", 'wb'))
    fileWriter.writerow(["Brand", "Category", "Product Description", 'compression class (derived)',
                         "Price", "MSRP", "Product Link", "Scraped from URL"])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/ExceptionUrls1.csv", 'wb'))
    exceptionFileWriter.writerow(["Brand", "Category", "Exception URL", 'Note'])
    brands = ['jobst', 'sigvaris', 'juzo', 'medi', 'therafirm', 'cep']
    mainURL = 'http://www.compressionstockings.com/__BRAND__.php'
    try:
        for brand in brands:
            logger.info("BRAND name: " + brand)
            brandURL = mainURL.replace('__BRAND__', brand)
            request = urllib2.Request(brandURL)
            request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
            logger.info("Visiting brand page " + brandURL)
            content = urllib2.urlopen(request).read()
            soup = BeautifulSoup(content, "html.parser")
            contentTable = soup.find('div', {"id": 'tcontent1'})
            categories = {}
            for elem in contentTable.find_all('td'):
                if elem.find('a'):
                    category = elem.find('a').text.strip()
                    categoryLink = elem.find('a').get('href').strip()
                    categories[category] = categoryLink
            logger.info("Total  number of categories found: " + str(len(categories)))
            count = 0
            for category, categoryLink in categories.items():
                delay = float("{0:.2f}".format(random.uniform(2, 6)))
                logger.info("applying " + str(delay) + " seconds delay")
                time.sleep(delay)
                count += 1
                logger.info("category: " + category + " category link: " + categoryLink)
                requestCat = urllib2.Request(categoryLink)
                requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                contentCat = urllib2.urlopen(requestCat).read()
                soupCat = BeautifulSoup(contentCat, "html.parser")
                displayCheck = soupCat.find_all('td', {'class': 'smallText'})
                numberOfProducts = 0
                for i in displayCheck:
                    if "Displaying" in i.text:
                        numberOfProducts = i.text.split('of')[1].strip().split(' ')[0]
                        break
                numberOfPages = int(math.ceil(int(numberOfProducts) / 20))
                logger.info("Number of pages " + str(numberOfPages))
                logger.info("Number of products " + str(numberOfProducts))
                for i in range(numberOfPages):
                    productTable = soupCat.find('table', {'class': 'productListing'})
                    for product in productTable.find_all('td'):
                        if len(product.text) < 2:
                            # logger.info("No info found here")
                            continue
                        try:
                            product.find('div').clear()
                        except AttributeError:
                            logger.error("Not able to fetch details , ", exc_info=True)
                            exceptionFileWriter.writerow([brand, category, requestCat.get_full_url(), ' page Atttrib'])
                            break
                        links = product.find_all('a')
                        try:
                            productDesc = links[0].text.strip()
                        except IndexError:
                            logger.error("Something is wrong  with source page ", exc_info=True)
                            exceptionFileWriter.writerow([brand, category, requestCat.get_full_url(), ' source Index'])
                            break
                        productLink = links[-1].get('href')
                        if not product.find('span', {'class': 'productSpecialPrice'}):
                            MSRP = ''
                            price = links[0].parent.text.replace(productDesc, '').replace(u'\xa0', u' ').strip()
                        else:
                            price = product.find('span', {'class': 'productSpecialPrice'}).text.strip()
                            MSRP = product.find('span').text.strip()
                        compClass = ''.join(re.findall('\d+[-]\d+\s+mmHg', productDesc))
                        fileWriter.writerow([brand.upper(), category, productDesc, compClass, price, MSRP, productLink, requestCat.get_full_url()])

                    if numberOfPages > 1 and i < (numberOfPages - 1):
                        requestCat = urllib2.Request(categoryLink + '?page=' + str(i + 2) + '&sort=2a')
                        requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                        contentCat = urllib2.urlopen(requestCat).read()
                        soupCat = BeautifulSoup(contentCat, "html.parser")
                        logger.info("visiting pagination link " + categoryLink + '?page=' + str(i + 2) + '&sort=2a')
    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    logger.info("finished")
