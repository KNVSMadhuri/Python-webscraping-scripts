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
import re

__author__ = "Apoorva Kumar G"
__copyright__ = "Copyright 2016, Affine Analytics"
__credits__ = [""]
__version__ = "2.0"
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
    handler = logging.FileHandler(outputpathBasic + '/log/DiscountSurgical-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    outputFileName = outputpathBasic + "/output/Discount_surgical_Product_Details" + strftime("%Y%m%d-%H-%M-%S") + ".csv"
    fileWriter = csv.writer(open(outputFileName, 'wb'))
    fileWriter.writerow(["Brand", "Category", "Product Description", "Number of reviews", 'Product ratings',
                         'features', 'style', 'color', "length", 'size', 'toe', 'compression class',
                         "Price", "MSRP", "Band (derived)", "Product URL", "Category URL"])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'wb'))
    exceptionFileWriter.writerow(["Brand", "Category", "product URL", "category URL", 'Note'])
    # exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'wb'))
    # exceptionFileWriter.writerow(["Brand", "Category", "Exception URL", 'Note'])
    allBrands = ['jobst', 'sigvaris', 'juzo', 'medi', 'therafirm', 'mojo', 'drschools']
    brands = ['jobst', 'sigvaris', 'juzo', 'medi']
    styleList = ['knee high', 'thigh high', 'maternity pantyhose', 'waist attachments', 'waist', 'maternity', 'chaps', 'capri', 'bermuda',
                 'armsleeve', 'glove', 'gauntlet', 'footcap', 'mini crew', 'crew', 'sleeveless vest', 'body breif with sleeves',
                 'abdominal pelvic garment', 'one-leg pantyhose', 'two-leg pantyhose', 'pantyhose', 'no zipper', 'zipper', 'liner',
                 'knee', 'thigh', 'ankle', 'chap']
    brandURLS = dict()
    brandURLS['jobst'] = 'http://www.discountsurgical.com/shop/jobst-18.cfm'
    brandURLS['juzo'] = 'http://www.discountsurgical.com/shop/juzo-19.cfm'
    brandURLS['sigvaris'] = 'http://www.discountsurgical.com/shop/sigvaris-17.cfm'
    brandURLS['medi'] = 'http://www.discountsurgical.com/shop/medi-20.cfm'
    brandURLS['mojo'] = 'http://www.discountsurgical.com/shop/mojo-489.cfm'
    brandURLS['therafirm'] = 'http://www.discountsurgical.com/shop/therafirm-596.cfm'
    brandURLS['drschools'] = 'http://www.discountsurgical.com/shop/dr-scholls-594.cfm'
    productCounts = dict()
    try:
        for brand in brands:
            productCounts[brand] = 0
        for brand in brands:
            brandURL = brandURLS.get(brand)
            request = urllib2.Request(brandURL)
            request.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
            logger.info("Visiting brand page " + brandURL)
            content = urllib2.urlopen(request).read()
            soup = BeautifulSoup(content, "html.parser")
            categoryLinks = ['http://www.discountsurgical.com/' + i['href'] for i in soup.find('div', text='Product Type').findNext().findAll('a')]
            for categoryLink in categoryLinks:
                delay = float("{0:.2f}".format(random.uniform(1, 4)))
                logger.info("applying " + str(delay) + " seconds delay before category link " + categoryLink + '?result=all&sort=bestseller')
                time.sleep(delay)
                linkTOVisit = categoryLink + '?result=all&sort=bestseller'
                requestCat = urllib2.Request(linkTOVisit)
                requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                contentCat = urllib2.urlopen(requestCat).read()
                soupCat = BeautifulSoup(contentCat, "html.parser")
                productFound = soupCat.find('div', {'class': 'resultCount'}).strong.get_text()
                productDivs = soupCat.find('div', {'class': 'products'}).findAll('div', {'class': 'product'})
                logger.info('total product divs found ' + str(len(productDivs)))
                category = soupCat.find('', text='Product Type').findNext().get_text()
                for product in productDivs:
                    productURL = product.find('div', {'class': 'title'}).find('a')['href'].strip()
                    try:
                        productDesc = product.find('div', {'class': 'title'}).find('a').get_text().strip()
                        # compClass = ''.join(re.findall('\d+[-]\d+mmHg', productDesc))
                        # price = product.find('div', {'class': 'price'}).get_text()
                        features = ''
                        if product.find('div', {'class': 'features'}):
                            features = product.find('div', {'class': 'features'}).get_text().strip().replace('\n', ',')
                        style = ''
                        if product.find('div', {'class': 'style'}):
                            try:
                                style = product.find('div', {'class': 'style'}).find('img')['src'].split('/icon/')[1].split('.jpg')[0].strip()
                            except TypeError:
                                style = product.find('div', {'class': 'style'}).get_text().strip()
                        if not style:
                            for styles in styleList:
                                if re.sub(' ', '', styles.lower()) in re.sub(' ', '', productDesc.lower()):
                                    style = styles
                                    break
                        '''
                        rating = 'NA'
                        reviewCount = "NA"
                        if product.find('div', {'class': 'rating'}):
                            reviewCount = product.find('div', {'class': 'rating'}).get_text().strip().split('review')[0].strip()
                            rating = product.find('div', {'class': 'rating'}).find('img')['src'].split('stars-')[1].split('.png')[0].strip()

                        color = []
                        if product.find('div', {'class': 'color'}):
                            color = [i.find('img')['src'].split('/icon/')[1].split('.jpg')[0].strip() if i.find('img') else i.get_text() for i in product.find('div', {'class': 'color'}).findAll('li')]
                        '''
                        requestProduct = urllib2.Request(productURL.replace(' ', '%20'))
                        requestProduct.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                        delay = float("{0:.2f}".format(random.uniform(0.2, 3)))
                        logger.info("applying " + str(delay) + " seconds delay before product " + productURL)
                        time.sleep(delay)
                        contentProduct = urllib2.urlopen(requestProduct).read()
                        soupProduct = BeautifulSoup(contentProduct, "html.parser")
                        compressionClass = ''
                        if soupProduct.find('span', {'class': "currentCompressionText"}):
                            compressionClass = soupProduct.find('span', {'class': "currentCompressionText"}).get_text().strip()
                        dropDowns = soupProduct.findAll('select', {'class': 'multiOptions'})
                        optionDict = dict()
                        for options in dropDowns:
                            key = options.findAll('option')[0].get_text().lower().split("choose")[1].replace(':', '').strip()
                            value = ",".join([i.get_text().strip() for i in options.findAll('option')[1:]])
                            optionDict[key] = value
                        rating = '0'
                        reviewCount = "0"
                        try:
                            if soupProduct.find('div', {'class': 'pricing'}).find('div', {'class': 'rating'}).find('img'):
                                reviewCount = soupProduct.find('div', {'class': 'pricing'}).find('div', {'class': 'rating'}).get_text().strip().split(' ')[0].strip()
                                rating = soupProduct.find('div', {'class': 'pricing'}).find('div', {'class': 'rating'}).find('img')['src'].split('stars_')[1].split('.png')[0].strip()
                        except AttributeError:
                            r = soupProduct.find('div', {'itemprop': 'aggregateRating'})
                            if r:
                                try:
                                    rating = r.find_next()['src'].split('stars_')[1].split('.png')[0].strip()
                                    reviewCount = r.find_next('', {'itemprop': 'reviewCount'}).get_text().strip()
                                except:
                                    logger.info("rating error")
                        price = soupProduct.find('span', {'itemprop': 'price', 'class': 'liveprice'}).get_text()
                        MSRP = ''
                        if soupProduct.find('span', {'itemprop': 'price', 'class': 'liveprice'}).find_next('span').has_attr('style'):
                            MSRP = soupProduct.find('span', {'itemprop': 'price', 'class': 'liveprice'}).find_next('span').get_text().strip()
                        band = ''
                        if "w/silicone" in productDesc.lower():
                            band = 'w/Silicone'
                        elif "with silicone" in productDesc.lower():
                            band = 'with Silicone'
                        if not band and 'silicone' in features.lower():
                            band = 'Silicone'
                        productCounts[brand] = productCounts.get(brand, 0) + 1
                        toe = optionDict.get('toe', '')
                        if not toe:
                            toe = ','.join(re.findall("|".join([r'open toe', r'closed toe']), productDesc, re.I)).strip()
                        if not compressionClass:
                            compressionClass = ''.join(re.findall("|".join([r'\d+[-]\d+\s?mmhg', r'-\s?\d+mmhg', r'\d+\s?mmhg',r'\d+[-]\d+']), productDesc, re.I))
                        color = optionDict.get('color', '')
                        try:
                            if not color and soupProduct.find('div', {'id': 'colorChartContainer'}):
                                color = [i['src'].split('olor')[1].split('.jpg')[0].strip() for i in soupProduct.find('div', {'id': 'colorChartContainer'}).findAll('img')]
                        except:
                            logger.info('color exception')
                        fileWriter.writerow([brand, category, productDesc, reviewCount, rating,
                                             features, style, color, optionDict.get('length', ''),
                                             optionDict.get('size', ''), toe, compressionClass,
                                             price, MSRP, band, productURL, requestCat.get_full_url()])
                    except Exception as e:
                        logger.error("product scraping ERROR, ", exc_info=True)
                        exceptionFileWriter.writerow([brand, category, productURL, requestCat.get_full_url(), str(e)])
                        traceback.print_exc()

    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    # sendMailUtil.sendMail("Compression Stockings ",outputFileName,productCounts,programStartTime,", ".join(brands))
    constructMailUtil.constructAndCreateMailFile("Discount Surgical (v2)", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brands), outputpathBasic + "\MAIL")
    logger.info("finished")
