from __future__ import division

from urllib2 import HTTPError

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

if __name__ == '__main__':
    outputpathBasic = sys.argv[1]
    programStartTime = strftime("%Y%m%d- %H:%M:%S")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    handler = logging.FileHandler(outputpathBasic + '/log/BrightLife-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    outputFileName = outputpathBasic + "/output/BrightLife_Product_Details" + strftime("%Y%m%d-%H-%M-%S") + ".csv"
    fileWriter = csv.writer(open(outputFileName, 'wb'))
    fileWriter.writerow(["Brand", "Category", "Product Description",
                         "Product Rating", "Price", "MSRP", "Size", "Color", "Length", "Limb",'Toe','Compression class(derived)', "Style(Derived)", "Band(derived)", "Product URL", "Category URL", "scraping comments"])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'wb'))
    exceptionFileWriter.writerow(["Brand", "Category","product URL", "category URL", 'Note'])
    allBrands = ['jobst', 'sigvaris', 'allegro', 'juzo', 'mediven', 'therafirm', 'smartknit', 'travelsox', 'aetrex', 'farrow-medical'
        , 'solaris', 'circaid', 'biacare', 'solidea', 'apex-shoes', 'bauerfeind']
    brands = ['jobst', 'sigvaris', 'juzo', 'mediven']
    styleList = ['knee high', 'thigh high', 'maternity pantyhose', 'waist attachments', 'waist', 'maternity', 'chaps', 'capri', 'bermuda',
                 'armsleeve', 'glove', 'gauntlet', 'footcap','mini crew', 'crew', 'sleeveless vest', 'body breif with sleeves',
                 'abdominal pelvic garment', 'one-leg pantyhose', 'two-leg pantyhose', 'pantyhose', 'no zipper', 'zipper', 'liner',
                 'knee','thigh','ankle','chap']

    mainURL = 'http://www.brightlifedirect.com/brand-__BRAND__.asp'
    try:
        productCounts = dict()
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
            contentTable = soup.find('div', {"class": 'category-desc-div'})
            categoryDivs = contentTable.findAll('div', {"class": ["left-brand", "right-brand"]})
            categories = {}
            if not categoryDivs:
                categoryName = ''
                categoryLink = request.get_full_url() + "?pgID=0"
                categories[''] = categoryLink
            for categoryDiv in categoryDivs:
                categoryName = categoryDiv.find_all('div')[1].p.get_text().replace('\n', '').strip()
                categoryLink = categoryDiv.find_all('div')[1].a.get('href').strip()
                # print categoryName,categoryLink
                categories[categoryName] = categoryLink
            logger.info("Total  number of categories found: " + str(len(categories)))
            count = 0
            for category, categoryLink in categories.items():
                delay = float("{0:.2f}".format(random.uniform(2, 6)))
                logger.info("applying " + str(delay) + " seconds delay")
                time.sleep(delay)
                count += 1
                logger.info("category: " + category + " category link: " + categoryLink)
                requestCat = urllib2.Request(categoryLink + "?pgID=0")
                requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                contentCat = urllib2.urlopen(requestCat).read()
                soupCat = BeautifulSoup(contentCat, "html.parser")
                productList = soupCat.find_all('td', {'class': 'column-cell'})
                for productCounter, product in enumerate(productList):
                    try:
                        productnameDiv = product.find('a', {'class': 'newnav'})
                        productDesc = productnameDiv.get_text().strip()
                        rating = productnameDiv.find_next('img').get('alt').split(":")[1].strip()
                        MSRP = product.find('span', {'class': 'modelheadOurPrice'}).get_text().strip()
                        sellingPrice = product.find('span', {'class': 'modelheadYourPrice'}).get_text().strip()
                        #compClass = ''.join(re.findall('\d+[-]\d+', productDesc))
                        compClass = ''.join(re.findall("|".join([r'\d+[-]\d+\s?mmhg', r'-\s?\d+mmhg', r'\d+\s?mmhg',r'\d+[-]\d+']), productDesc, re.I))
                        band = ''
                        if "w/silicone" in productDesc.lower():
                            band = 'w/Silicone'
                        elif "silicone" in productDesc.lower():
                            band = 'Silicone'
                        style = ''
                        for styles in styleList:
                            if re.sub(' ', '', styles.lower()) in re.sub(' ', '', productDesc.lower()):
                                style = styles
                                break
                        productCounts[brand] = productCounts.get(brand, 0) + 1
                        productLink = productnameDiv.get('href').strip()
                        logger.info('visiting product url:' + productLink)
                        delay = float("{0:.2f}".format(random.uniform(0.2, 3)))
                        logger.info("applying " + str(delay) + " seconds delay before product ")
                        time.sleep(delay)
                        requestProduct = urllib2.Request(productLink)
                        requestProduct.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                        size,color,length, limb, toe='','','','',''
                        try:
                            contentProduct = urllib2.urlopen(requestProduct).read()
                            soupProduct = BeautifulSoup(contentProduct, "html.parser")
                            if soupProduct.find('div', {'id': 'divVariant_Size'}):
                                size = ",".join([i.text for i in soupProduct.find('div', {'id': 'divVariant_Size'}).findAll('option')])
                            if soupProduct.find('div', {'id': 'divVariant_Color'}):
                                color = ",".join([i.text for i in soupProduct.find('div', {'id': 'divVariant_Color'}).findAll('option')])
                            if soupProduct.find('div', {'id': 'divVariant_Length'}):
                                length = ",".join([i.text for i in soupProduct.find('div', {'id': 'divVariant_Length'}).findAll('option')])
                            if soupProduct.find('div', {'id': 'divVariant_Limb'}):
                                limb = ",".join([i.text for i in soupProduct.find('div', {'id': 'divVariant_Limb'}).findAll('option')])
                            if soupProduct.find('div', {'id': 'divVariant_Toe'}):
                                toe = ",".join([i.text for i in soupProduct.find('div', {'id': 'divVariant_Toe'}).findAll('option')])
                            if not toe:
                                toe = ','.join(re.findall(r'\b(?:open Toe | closed toe )\b', productDesc, re.I)).strip()
                            fileWriter.writerow([brand, category, productDesc.encode('utf-8'),
                                                 rating, sellingPrice, MSRP, size, color, length, limb, toe, compClass.strip(), style, band, productLink, requestCat.get_full_url(), ''])
                        except HTTPError:
                            logger.error("product URL error, ", exc_info=True)
                            fileWriter.writerow([brand, category, productDesc.encode('utf-8'),
                                                 rating, sellingPrice, MSRP, '', '', '', '', '',compClass.strip(), style, band, productLink, requestCat.get_full_url(),'product URL not reachable'])

                            delay = float("{0:.2f}".format(random.uniform(30, 60)))
                            logger.info("applying " + str(delay) + " seconds delay after httperror")
                            time.sleep(delay)
                    except Exception as e:
                        logger.error("product scraping ERROR, ", exc_info=True)
                        traceback.print_exc()
                        exceptionFileWriter.writerow([brand, category,productLink, requestCat.get_full_url(), str(e)])
                logger.info("Number of products scraped from this page are " + str(productCounter + 1))
    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    # sendMailUtil.sendMail("Bright Life Direct ",outputFileName,productCounts,programStartTime,", ".join(brands))
    constructMailUtil.constructAndCreateMailFile("Bright Life Direct ", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brands), outputpathBasic + "\MAIL")
    logger.info("finished")
