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
# import sendMailUtil
import constructMailUtil

__author__ = "Apoorva Kumar G"
__copyright__ = "Copyright 2016, Affine Analytics"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "YOU, IF you opened this file ;)"
__email__ = "apoorva.kumar@affineanalytics.com"
__status__ = "still in development"


def AddSleepTime(short=False):
    if short:
        delay = float("{0:.2f}".format(random.uniform(0.2, 4)))
    else:
        delay = float("{0:.2f}".format(random.uniform(2, 6)))
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
    handler = logging.FileHandler(outputpathBasic + '/log/CompressionStock-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    outputFileName = outputpathBasic + "/output/CompressionStockings_Product_Details" + strftime("%Y%m%d-%H-%M-%S") + ".csv"
    fileWriter = csv.writer(open(outputFileName, 'wb'))
    fileWriter.writerow(["Brand", "Category", "Product Description", "Color" , "Length", "Size", "Toe",'Compression class (derived)', "Style (derived)",
                         "Band (derived)","Price", "MSRP", "Product Link", "Category URL"])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'wb'))
    exceptionFileWriter.writerow(["Brand", "Category","product URL", "category URL", 'Note'])
    allBrands = ['jobst', 'sigvaris', 'juzo', 'medi', 'therafirm', 'cep', 'smoothtoe', 'vo2fx', 'zensah', 'powerstep', 'lymphedivas']
    brands = ['jobst', 'sigvaris', 'juzo', 'medi']
    styleList = ['knee high', 'thigh high', 'maternity pantyhose', 'waist attachments', 'waist', 'maternity', 'chaps', 'capri', 'bermuda',
                 'armsleeve', 'glove', 'gauntlet', 'footcap', 'mini crew', 'crew', 'sleeveless vest', 'body breif with sleeves',
                 'abdominal pelvic garment', 'one-leg pantyhose', 'two-leg pantyhose', 'pantyhose', 'no zipper', 'zipper', 'liner',
                 'knee', 'thigh', 'ankle', 'chap']
    mainURL = 'http://www.compressionstockings.com/__BRAND__.php'
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
                        '''if not product.find('span', {'class': 'productSpecialPrice'}):
                            MSRP = ''
                            price = links[0].parent.text.replace(productDesc, '').replace(u'\xa0', u' ').strip()
                        else:
                            price = product.find('span', {'class': 'productSpecialPrice'}).text.strip()
                            MSRP = product.find('span').text.strip()
                        '''
                        # compClass = ''.join(re.findall('\d+[-]\d+\s+mmHg', productDesc,re.I))
                        compClass = ''.join(re.findall("|".join([r'\d+[-]\d+\s?mmhg', r'-\s?\d+mmhg', r'\d+\s?mmhg',r'\d+[-]\d+']), productDesc, re.I))
                        logger.info('visiting product url: ' + productLink)
                        delay = float("{0:.2f}".format(random.uniform(0.2, 3)))
                        logger.info("applying " + str(delay) + " seconds delay before product ")
                        time.sleep(delay)
                        try:
                            requestProduct = urllib2.Request(productLink)
                            requestProduct.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                            contentProduct = urllib2.urlopen(requestProduct).read()
                            soupProduct = BeautifulSoup(contentProduct, "html.parser")
                            msrp=soupProduct.find('td',{'class':'PriceListBIG'}).get_text().split('MSRP:')[1].replace(u'\xa0','').strip()
                            try:
                                price=soupProduct.find('td',{'class':'pricenowBIG'}).get_text().split('Price:')[1].replace(u'\xa0','').strip()
                            except IndexError:
                                soupProduct.find('td',{'class':'pricenowBIG'}).get_text().lower().split('now:')[1].replace(u'\xa0','').strip()

                            reviewCount,ratings='',''
                            if soupProduct.find('a',{'class':'nounderline'}) and soupProduct.findAll('a',{'class':'nounderline'})[0].find('img'):
                                reviewCount=soupProduct.findAll('a',{'class':'nounderline'})[0].get_text().strip().split('Revie')[0][1:].strip()
                                ratings=soupProduct.findAll('a',{'class':'nounderline'})[0].find('img')['src'].split('_')[1].split('.gif')[0].strip()
                            allOptions=soupProduct.find('div',{'id':'attrib_box'}).find('table').findAll('tr')[1:]
                            optionsDict=dict()
                            for dropdown in allOptions:
                                if len(dropdown.findAll('td'))==2:
                                    key=dropdown.findAll('td')[0].find(text=True,recursive=False).strip()[:-1].replace(u'\xa0','').lower()
                                    value=",".join([i.get_text().strip() for i in dropdown.findAll('td')[1].findAll('option')[1:]])
                                    optionsDict[key]=value

                            color=optionsDict.get('color','')
                            length=optionsDict.get('length','')
                            toe=optionsDict.get('toe type','')
                            size=optionsDict.get('size','')
                            style = ''
                            for styles in styleList:
                                if re.sub(' ', '', styles.lower()) in re.sub(' ', '', productDesc.lower()):
                                    style = styles
                                    break
                            if not toe:
                                toe = ','.join(re.findall(r'\b(?:open Toe | closed toe )\b', productDesc, re.I)).strip()
                            band_pattern = r'\b(?:with sil[i]*cone|w/ sil[i]*cone|w/ [a-zA-Z ]+ sil[i]*cone|with [a-zA-Z ]+ sil[i]*cone)\b'
                            band = ''.join(re.findall(band_pattern, productDesc,re.I)).strip()
                            if not band and 'silicone' in productDesc.lower():
                                band = 'Silicone'
                            productCounts[brand] = productCounts.get(brand, 0) + 1
                            fileWriter.writerow([brand.upper(), category, productDesc,color,length,size,toe, compClass, style,band, price, msrp, productLink, requestCat.get_full_url()])
                        except Exception as e:
                            logger.error("product fetch ERROR, in " + productLink, exc_info=True)
                            exceptionFileWriter.writerow([brand, category, productLink, requestCat.get_full_url(), str(e)])
                    if numberOfPages > 1 and i < (numberOfPages - 1):
                        requestCat = urllib2.Request(categoryLink + '?page=' + str(i + 2) + '&sort=2a')
                        requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                        contentCat = urllib2.urlopen(requestCat).read()
                        soupCat = BeautifulSoup(contentCat, "html.parser")
                        logger.info("visiting pagination link " + categoryLink + '?page=' + str(i + 2) + '&sort=2a')
    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    # sendMailUtil.sendMail("Compression Stockings ",outputFileName,productCounts,programStartTime,", ".join(brands))
    constructMailUtil.constructAndCreateMailFile("Compression Stockings ", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brands), outputpathBasic + "\MAIL")
    logger.info("finished")





