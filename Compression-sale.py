from __future__ import division
#from bs4 import BeautifulSoup
import math
import urllib3
import traceback
import logging
import sys
import csv
import re
import time
import random
from time import strftime
from lxml.html import parse
import lxml.etree as etree
import urllib.request

__author__ = "Madhuri.K"
__copyright__ = "Copyright 2016, Affine Analytics"
__credits__ = [""]
__version__ = "1.0"
__maintainer__ = "YOU, IF you opened this file ;)"
__email__ = "munukutla.madhuri@affineanalytics.com"
__status__ = "still in development"



if __name__ == '__main__':
    outputpathBasic= sys.argv[1]
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    handler = logging.FileHandler(outputpathBasic + '/logs/ForYourLegs-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")

    fileWriter = csv.writer(open(outputpathBasic + "/csv_files/CompressionSale.csv", 'w', newline='',encoding='utf-8'))
    fileWriter.writerow(['Brand', 'Category', 'Product Description', 'compression class (derived)',
                         'Price', 'MSRP', 'Product Link', 'Scraped from URL'])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/Exceptions/ExceptionUrls.csv", 'w', newline=''))
    exceptionFileWriter.writerow(["Brand", "Category", "Exception URL", 'Note'])

    startURL = 'http://www.compressionsale.com'


    def get_html_doc(url):
        request= urllib.request.Request(url=url)
        request.add_header('User-Agent',
                           "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:34.0) Gecko/20100101 Firefox/34.0.1 Waterfox/34.0")
        f = urllib.request.urlopen(request)

        # page = f.read()
        p = parse(f)
        return (p)



    def sleepForSomeTime():
        delay = float("{0:.2f}".format(random.uniform(2, 6)))
        # print("applying "+str(delay)+" seconds delay")
        logger.info("applying " + str(delay) + " seconds delay")
        return time.sleep(delay)


    #brand_nodes = etree.XPath('//div[@class="content"]//ul[@class = "fancycat-icons-level-0"]/li/a[contains(text(),"JOBST") or contains(text(),"Activa") '
                                 # 'or contains(text(),"Sigvaris") or contains(text(),"Medi") or contains(text(),"JUZO") or contains(text(),"Truform") or contains(text(),"Futuro")]')
    category_nodes = etree.XPath('//span[@class="subcategories"]//a[2]')
    #subcategory_nodes = etree.XPath('//tr//script[@type="text/javascript"]/following-sibling::a')
    subcategory_nodes = etree.XPath('//td[contains(@class,"product-cell")]/script[@type="text/javascript"]')
    nextPage = etree.XPath('//img[contains(@alt , "Next page")]/ancestor::a/@href')

    try:
        sleepForSomeTime()
        xmlTree = get_html_doc(startURL)
    except:
        exceptionFileWriter.writerow('start url not found')
        logger.error("Not able to fetch start url , ", exc_info=True)

    brands = brand_nodes(xmlTree)

    for brand in brands:
        brandurl = ''.join(brand.xpath('./@href'))
        logger.info("Brand_Url: " + brandurl)
        brandName = ''.join(brand.xpath('./text()')).upper()
        logger.info("BrandName: " + brandName)

        try:
            sleepForSomeTime()
            categoriesTree = get_html_doc(brandurl)
        except:
            exceptionFileWriter.writerow('brandurl not found')
            logger.error("Not able to fetch brandurl , ", exc_info=True)

        categories = category_nodes(categoriesTree)


        for category in categories:
            categoryurl = ''.join(category.xpath('./@href'))
            print("categoryurl:",categoryurl)
            logger.info("Category_Url " + categoryurl)
            categoryName = ''.join(category.xpath('./text()'))
            logger.info("CategoryName " + categoryName)
            i = 1
            flag = 0
            while i:
                sleepForSomeTime()
                try:
                    subCategoryTree = get_html_doc(categoryurl)

                except:
                    exceptionFileWriter.writerow('subcategoryurl not found')
                    logger.error("subcategory , ", exc_info=True)
                try:

                    next_page = nextPage(subCategoryTree)[1]

                except:
                    try:
                        subCategoryTree = get_html_doc(categoryurl)
                        flag = 1
                    except:
                        exceptionFileWriter.writerow('subcategoryurl not found')
                        logger.error("subcategory , ", exc_info=True)
                items = subcategory_nodes(subCategoryTree)
                print(len(items))
                i=0
                for item in items:
                    itemurl = ''.join(item.xpath('.//following-sibling::a/@href'))
                    logger.info("Source_Url " + itemurl)
                    itemText = ''.join(item.xpath('.//following-sibling::a/text()'))
                    logger.info("Title of the Source_Url " + itemText)
                    compression = ''.join(re.findall(r'\d+-\d+ |\d+ mmHg |\d+mmHg|\d+-\d+mmHg', itemText))
                    if len(compression) > 2:
                        compression = compression + '' + 'mmHg'
                    else:
                        compression = compression

                    productPrice = item.xpath('//td[contains(@class,"product-cell-price")]//div[@class="price-row"]//span[@class = "currency"]/text()')[i]
                    i = i + 1
                    
                    retailPrice = None
                    fileWriter.writerow([brandName.strip(), categoryName.strip(), itemText.strip(), compression.strip()
                            , productPrice.strip(), retailPrice, itemurl.strip(), categoryurl.strip()])

                if next_page:
                    # category_url = startURL + '/' + next_page
                    categoryurl = next_page
                    print(categoryurl)
                    # logger.info('Next_Page_Url ' + categoryurl)
                else:
                    i = 0
                if flag:
                    break

    logger.info("Finished")





