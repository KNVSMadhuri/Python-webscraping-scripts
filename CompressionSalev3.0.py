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

__copyright__ = "Copyright 2016, Affine Analytics"
__version__ = "3.0"


def AddSleepTime(short=False):
    if short:
        delay = float("{0:.2f}".format(random.uniform(0.2, 4)))
    else:
        delay = float("{0:.2f}".format(random.uniform(2, 6)))
    logger.info("applying " + str(delay) + " seconds delay")
    time.sleep(delay)


def fetchDetails(productDescription, productLinkTovisit):
    logger.info("visiting product link " + productLinkTovisit)
    AddSleepTime(True)

    requestProduct = urllib2.Request(productLinkTovisit)
    requestProduct.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
    contentProduct = urllib2.urlopen(requestProduct).read()
    soupProduct = BeautifulSoup(contentProduct, "html.parser")
    itemNumber = soupProduct.find('span', {'id': 'product_code'}).get_text()
    size = ''
    if soupProduct.find('td', {'class': 'size-enable'}):
        size = ",".join([i.get_text().strip() for i in soupProduct.find('td', {'class': 'size-enable'}).findAll('option')])
    color = ''
    if soupProduct.find('td', {'class': 'color-enable'}):
        color = ",".join([i.get_text().strip() for i in soupProduct.find('td', {'class': 'color-enable'}).findAll('option')])
    if soupProduct.find('td', {'class': 'size-color-enable'}):
        colorSizeRaw = [i.get_text().strip() for i in soupProduct.find('td', {'class': 'size-color-enable'}).findAll('option')]
        if len(colorSizeRaw[0].split(',')) > 1:
            color = ",".join(list(set([i.split('-')[0].split(',')[0] for i in colorSizeRaw])))
            size = ",".join(list(set([i.split('-')[0].split(',')[1].strip() for i in colorSizeRaw])))
        elif 'size' in colorSizeRaw[0].lower():
            color = ",".join(list(set([i.lower().split('-')[0].split('size')[0] for i in colorSizeRaw])))
            size = ",".join(list(set([i.upper().split('-')[0].split('SIZE')[1].strip() for i in colorSizeRaw])))
        else:
            color = ",".join(list(set([i.split('-')[0].split(' ')[0] for i in colorSizeRaw])))
            size = ",".join(list(set([i.split('-')[0].split(' ')[1].strip() for i in colorSizeRaw])))
    '''sizeAndColorSelectOption = ''
    if soupProduct.find('td', {'class': 'size-color-enable'}):
        sizeAndColorSelectOption = ",".join([i.text.strip() for i in soupProduct.find('td', {'class': 'size-color-enable'}).find_all('option')])
    '''
    allTypes = soupProduct.find('ul', {'class': 'ef-property-list'}).findAll('li')
    optionsDict = dict()
    for optionType in allTypes:
        key = optionType.find('b').get_text()[:-1].strip().lower()
        value = optionType.find(text=True, recursive=False).replace(u'\xa0', '').strip()
        optionsDict[key] = value
    age = optionsDict.get('age group', '')
    style = optionsDict.get('style/length', '')
    compression = optionsDict.get('compression', '')
    if not color:
        color = optionsDict.get('color', '')
    series = optionsDict.get('series', '')
    # optionsDict.get('brand','')
    toe = optionsDict.get('toe type', '')
    gender = optionsDict.get('gender', '')
    if not size:
        size = optionsDict.get('size', '')
    condition = optionsDict.get('condition', '')
    fabric = optionsDict.get('fabric', '')

    try:
        reviewCount = ''.join(re.findall('[0-9]+', soupProduct.find('div', {'class': 'review-container'}).find('a').get_text()))
    except:
        reviewCount = '0'
    try:
        rating = soupProduct.find('div', {'class': 'review-container'}).find('div', {'class': 'creviews-vote-bar'})['title'].split(';')[0].split(' ')[-1].strip()
    except:
        rating = '0'
    rating = rating.replace('yet.', '')
    price = soupProduct.find('tr', {'class': "product-price-row"}).findAll('span', {'id': 'product_price'})[0].get_text().strip()
    try:
        # if soupProduct.find('tr', {'class': "product-price-row"}).findAll('span', {'class': 'currency'})[-1].parent.has_attr('style'):
        MSRP = soupProduct.find('tr', {'class': "product-price-row"}).findAll('span', {'id': 'product_price'})[0].find_next('span', {'class': 'currency'}).get_text()
        # MSRP = soupProduct.find('tr', {'class': "product-price-row"}).findAll('span', {'class': 'currency'})[-1].get_text()
    except:
        MSRP = ''
    if not style:
        style = ''
        for styles in styleList:
            if re.sub(' ', '', styles.lower()) in re.sub(' ', '', productDescription.lower()):
                style = styles
                break
    toe_pattern = r'\b(?:open Toe | closed toe )\b'
    if not toe:
        toe = ','.join(re.findall(toe_pattern, productDescription, re.I)).strip()
    # print(toe)
    band_pattern = r'\b(?:with sil[i]*cone|w/ sil[i]*cone|w/ [a-zA-Z ]+ sil[i]*cone|with [a-zA-Z ]+ sil[i]*cone)\b'
    band = ''.join(re.findall(band_pattern, productDescription, re.I)).strip()
    if not band and 'silicone' in productDescription.lower():
        band = 'Silicone'
    if not compression:
        compression = ''.join(re.findall("|".join([r'\d+[-]\d+\s?mmhg', r'-\s?\d+mmhg', r'\d+\s?mmhg', r'\d+[-]\d+']), productDescription, re.I))
    fileWriter.writerow([brand, category, productDescription.encode('utf-8'), color, style, age,
                         series, compression, toe, gender, size, condition, fabric, reviewCount, rating, "$"+price, MSRP, band, itemNumber, productLinkTovisit, requestCat.get_full_url()])


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
    fileWriter.writerow(["Brand", "Category", "Product Description", 'Color', 'style/length', 'Age Group',
                         'Series', 'Compression class', 'Toe', 'Gender', 'Size', 'Condition', 'Fabric', 'Review Count', 'Rating',
                         'Price', 'MSRP', 'Band', "Item Number", "Product URL", "Category URL"])
    allBrands = ['jobst', 'sigvaris', 'truform', 'juzo', 'therafirm', 'mediven-alternatives', 'activa', 'dr-scholls-socks', 'rejuvahealth', 'futuro-support-hose', 'farrow-medical', 'csx-sport',
                 'mcdavid', 'sockwell', 'zensah', 'lymphedivas', 'second-skin-stockings', 'new-balance', 'powerstep-orthotic-foot-supports']
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'wb'))
    exceptionFileWriter.writerow(["Brand", "Category", "product URL", "category URL", 'Note'])
    brands = ['jobst', 'sigvaris', 'truform', 'juzo', 'mediven-alternatives', 'activa', 'futuro-support-hose']
    styleList = ['knee high', 'thigh high', 'maternity pantyhose', 'waist attachments', 'waist', 'maternity', 'chaps', 'capri', 'bermuda',
                 'armsleeve', 'glove', 'gauntlet', 'footcap', 'mini crew', 'crew', 'sleeveless vest', 'body breif with sleeves',
                 'abdominal pelvic garment', 'one-leg pantyhose', 'two-leg pantyhose', 'pantyhose', 'no zipper', 'zipper', 'liner',
                 'knee', 'thigh', 'ankle', 'chap', 'athletic']
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
                logger.info("Number Of pages found " + str(numberOfPages))
                try:
                    for pageCounter in range(numberOfPages):
                        totalNumberOfProductsPerPage = 0
                        productTable = soupCat.find('table', {'class': 'products'})
                        productRowStart = False
                        NumberOfProducts = 0
                        colorList, productDesc, msrpList, priceList, productLinkList = [], [], [], [], []
                        for rowCounter, row in enumerate(productTable.findAll('tr')):
                            if row.has_attr('class') and ('product-name-row' in row['class']):
                                productRowStart = True
                                if NumberOfProducts:
                                    totalNumberOfProductsPerPage += NumberOfProducts
                                    for ij in range(NumberOfProducts):
                                        try:
                                            fetchDetails(productDesc[ij], productLinkList[ij])
                                            productCounts[brand] = productCounts.get(brand, 0) + 1
                                        except Exception as e:
                                            logger.error("product fetch ERROR, in " + productLinkList[ik], exc_info=True)
                                            exceptionFileWriter.writerow([brand, category, productLinkList[ik], requestCat.get_full_url(), str(e)])
                                    NumberOfProducts = 0
                                colorList, productDesc, msrpList, priceList, productLinkList = [], [], [], [], []
                            else:
                                productRowStart = False
                            if not productRowStart:
                                if row.find('div', {'class': "swatches-box"}):
                                    for tds in row.findAll("td"):
                                        colorList.append(",".join([i['title'] for i in tds.findAll('img')]))
                                if row.findAll('a', {'class': 'product-title'}):
                                    productDesc = ([i.get_text() for i in row.findAll('a', {'class': 'product-title'})])
                                    productLinkList = ([i['href'] for i in row.findAll('a', {'class': 'product-title'})])
                                    NumberOfProducts = len(productDesc)
                                if row.find('td', {'class': 'product-cell-price'}):
                                    for tds in row.findAll('td'):
                                        if tds.find('div', {'class': "market-price"}):
                                            msrpList.append(tds.find('span', {'class': "market-price-value"}).get_text().strip())
                                        else:
                                            msrpList.append('NA')
                                        if tds.find('div', {'class': "price-row"}):
                                            priceList.append(tds.find('div', {'class': "price-row"}).find('span', {'class': "currency"}).get_text().strip())
                                        else:
                                            priceList.append('NA')
                        if NumberOfProducts:
                            totalNumberOfProductsPerPage += NumberOfProducts
                            for ik in range(NumberOfProducts):
                                try:
                                    fetchDetails(productDesc[ik], productLinkList[ik])
                                    productCounts[brand] = productCounts.get(brand, 0) + 1
                                except Exception as e:
                                    logger.error("product fetch ERROR, in " + productLinkList[ik], exc_info=True)
                                    exceptionFileWriter.writerow([brand, category, productLinkList[ik], requestCat.get_full_url(), str(e)])
                            NumberOfProducts = 0
                        logger.info("products found in this page are : " + str(totalNumberOfProductsPerPage))
                        if numberOfPages > 1 and pageCounter < (numberOfPages - 1):
                            AddSleepTime()
                            requestCat = urllib2.Request(categoryLink + '?page=' + str(pageCounter + 2))
                            logger.info("visiting pagination link " + categoryLink + '?page=' + str(pageCounter + 2))
                            requestCat.add_header('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
                            contentCat = urllib2.urlopen(requestCat).read()
                            soupCat = BeautifulSoup(contentCat, "html.parser")
                except:
                    logger.error("unexpected ERROR, in " + requestCat.get_full_url(), exc_info=True)
                    traceback.print_exc()

    except:
        logger.error("critical ERROR, ", exc_info=True)
        traceback.print_exc()
    # sendMailUtil.sendMail("Bright Life Direct ",outputFileName,productCounts,programStartTime,", ".join(brands))
    constructMailUtil.constructAndCreateMailFile("Compression Sale", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brands), outputpathBasic + "\MAIL")
    logger.info("finished")

productLinkList = 'http://www.compressionsale.com/jobst-ultrasheer-8-15-mmhg-pantyhose.html'
