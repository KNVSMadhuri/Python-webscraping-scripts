from bs4 import BeautifulSoup
import urllib2
import traceback
import logging
import sys
import csv
import time
import random
from time import strftime
import constructMailUtil

__copyright__ = "Copyright 2016, Affine Analytics"
__version__ = "2.0"

def AddSleepTime():
    delay = float("{0:.2f}".format(random.uniform(1, 6)))
    logger.info("applying " + str(delay) + " seconds delay")
    time.sleep(delay)


if __name__ == '__main__':
    outputpathBasic = sys.argv[1]
    programStartTime = strftime("%Y%m%d- %H:%M:%S")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    handler = logging.FileHandler(outputpathBasic + '/log/CompressionSale-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    outputFileName = outputpathBasic + "/output/CompressionSale_Product_Details" + strftime("%Y%m%d-%H-%M-%S") + ".csv"
    fileWriter = csv.writer(open(outputFileName, 'wb'))
    fileWriter.writerow(["Brand", "Category", "Product Description", 'Color',
                                                                     "Price", "MSRP", "Product Link", "Scraped from URL"])

    allBrands = ['jobst', 'sigvaris', 'truform', 'juzo', 'therafirm', 'mediven-alternatives', 'activa', 'dr-scholls-socks', 'rejuvahealth', 'futuro-support-hose', 'farrow-medical', 'csx-sport',
                 'mcdavid', 'sockwell', 'zensah', 'lymphedivas', 'second-skin-stockings', 'new-balance', 'powerstep-orthotic-foot-supports']
    brands = ['jobst', 'sigvaris', 'truform', 'juzo', 'therafirm', 'mediven-alternatives', 'activa', 'dr-scholls-socks', 'rejuvahealth', 'futuro-support-hose', 'farrow-medical', 'csx-sport',
              'mcdavid', 'sockwell', 'zensah', 'lymphedivas', 'second-skin-stockings', 'new-balance', 'powerstep-orthotic-foot-supports']
    mainURL = 'http://www.compressionsale.com/__BRAND__/'
    productCounts = dict()
    try:
        for brand in brands:
            productCounts[brand] = 0
        for brand in brands:
            logger.info("BRAND name: " + brand)
            brandURL = mainURL.replace('__BRAND__', brand)
            request = urllib2.Request(brandURL)
            request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
            logger.info("Visiting brand page " + brandURL)
            content = urllib2.urlopen(request).read()
            soup = BeautifulSoup(content, "html.parser")
            categoryDivs = soup.findAll('span', {'class': 'subcategories'})
            categories = {}
            for categoryDiv in categoryDivs:
                categoryName = categoryDiv.find_all('a')[1].get_text().replace('\n', '').strip()
                categoryLink = categoryDiv.find_all('a')[1].get('href').strip()
                categories[categoryName] = categoryLink
            if not categoryDivs:
                categoryName = ''
                categoryLink = request.get_full_url()
                categories[''] = categoryLink
            logger.info("Total  number of categories found: " + str(len(categories)))
            for category, categoryLink in categories.items():
                AddSleepTime()
                logger.info("category: " + category + " category link: " + categoryLink)
                requestCat = urllib2.Request(categoryLink)
                requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                contentCat = urllib2.urlopen(requestCat).read()
                soupCat = BeautifulSoup(contentCat, "html.parser")
                numberOfPages = 1
                if soupCat.find('div', {'class': 'nav-pages'}):
                    numberOfPages = len(soupCat.find('div', {'class': 'nav-pages'}).findAll('a', {'class': "nav-page"})) + 1
                logger.info("Number Of pages found "+str(numberOfPages))
                try:
                    for pageCounter in range(numberOfPages):
                        totalNumberOfProductsPerPage=0
                        productTable = soupCat.find('table', {'class': 'products'})
                        productRowStart = False
                        NumberOfProducts = 0
                        color, productDesc, msrp, price, productLink = [], [], [], [], []
                        for rowCounter, row in enumerate(productTable.findAll('tr')):
                            if row.has_attr('class') and ('product-name-row' in row['class']):
                                productRowStart = True
                                if NumberOfProducts:
                                    totalNumberOfProductsPerPage += NumberOfProducts
                                    for i in range(NumberOfProducts):
                                        try:
                                            fileWriter.writerow([brand, category, productDesc[i], color[i], price[i], msrp[i], productLink[i], requestCat.get_full_url()])
                                            productCounts[brand] = productCounts.get(brand, 0) + 1
                                        except UnicodeEncodeError:
                                            fileWriter.writerow([brand, category, productDesc[i].encode('utf-8'), color[i].encode('utf-8'), price[i], msrp[i], productLink[i], requestCat.get_full_url()])
                                            productCounts[brand] = productCounts.get(brand, 0) + 1
                                    NumberOfProducts = 0
                                color, productDesc, msrp, price, productLink = [], [], [], [], []
                            else:
                                productRowStart = False
                            if not productRowStart:
                                if row.find('div', {'class': "swatches-box"}):
                                    for tds in row.findAll("td"):
                                        color.append(",".join([i['title'] for i in tds.findAll('img')]))
                                if row.findAll('a', {'class': 'product-title'}):
                                    productDesc = ([i.get_text() for i in row.findAll('a', {'class': 'product-title'})])
                                    productLink = ([i['href'] for i in row.findAll('a', {'class': 'product-title'})])
                                    NumberOfProducts = len(productDesc)
                                if row.find('td', {'class': 'product-cell-price'}):
                                    for tds in row.findAll('td'):
                                        if tds.find('div', {'class': "market-price"}):
                                            msrp.append(tds.find('span', {'class': "market-price-value"}).get_text().strip())
                                        else:
                                            msrp.append('NA')
                                        if tds.find('div', {'class': "price-row"}):
                                            price.append(tds.find('div', {'class': "price-row"}).find('span', {'class': "currency"}).get_text().strip())
                                        else:
                                            price.append('NA')
                        if NumberOfProducts:
                            totalNumberOfProductsPerPage+=NumberOfProducts
                            for i in range(NumberOfProducts):
                                try:
                                    fileWriter.writerow([brand, category, productDesc[i], color[i], price[i], msrp[i], productLink[i], requestCat.get_full_url()])
                                    productCounts[brand] = productCounts.get(brand, 0) + 1
                                except UnicodeEncodeError:
                                    fileWriter.writerow([brand, category, productDesc[i].encode('utf-8'), color[i].encode('utf-8'), price[i], msrp[i], productLink[i], requestCat.get_full_url()])
                                    productCounts[brand] = productCounts.get(brand, 0) + 1
                            NumberOfProducts = 0
                        logger.info("products found in this page are : "+str(totalNumberOfProductsPerPage))
                        if numberOfPages > 1 and pageCounter < (numberOfPages - 1):
                            AddSleepTime()
                            requestCat = urllib2.Request(categoryLink + '?page=' + str(pageCounter + 2))
                            logger.info("visiting pagination link " + categoryLink + '?page=' + str(pageCounter + 2))
                            requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                            contentCat = urllib2.urlopen(requestCat).read()
                            soupCat = BeautifulSoup(contentCat, "html.parser")
                except:
                    logger.error("unexpected ERROR, in "+requestCat.get_full_url(), exc_info=True)
                    traceback.print_exc()

    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    # sendMailUtil.sendMail("Bright Life Direct ",outputFileName,productCounts,programStartTime,", ".join(brands))
    constructMailUtil.constructAndCreateMailFile("Compression Sale", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brands), outputpathBasic + "\MAIL")
    logger.info("finished")
