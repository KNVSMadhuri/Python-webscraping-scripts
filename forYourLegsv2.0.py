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
import constructMailUtil

__author__ = "Madhuri.K"
__copyright__ = "Copyright 2016, Affine Analytics"
__credits__ = [""]
__version__ = "2.0"
__maintainer__ = "YOU, IF you opened this file ;)"
__email__ = "munukutla.madhuri@affineanalytics.com"
__status__ = "still in development"


def get_html_doc(url):
    f = urllib.request.urlopen(url)
    # page = f.read()
    p = parse(f)
    return (p)


def sleepForSomeTime(short=False):
    if short:
        delay = float("{0:.2f}".format(random.uniform(0.1, 3)))
    else:
        delay = float("{0:.2f}".format(random.uniform(2, 6)))
    # print("applying "+str(delay)+" seconds delay")
    logger.info("applying " + str(delay) + " seconds delay")
    return time.sleep(delay)


if __name__ == '__main__':
    outputpathBasic = sys.argv[1]
    programStartTime = strftime("%Y%m%d- %H:%M:%S")
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    handler = logging.FileHandler(outputpathBasic + '/log/ForYourLegs-' + strftime("%Y%m%d-%H-%M-%S") + '.log')
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.info("Program started")
    outputFileName = outputpathBasic + "/output/ForYourLegs_Product_Details" + strftime("%Y%m%d-%H-%M-%S") + ".csv"
    fileWriter = csv.writer(open(outputFileName, 'w', newline='', encoding='utf-8'))
    fileWriter.writerow(['Brand', 'Category', 'Product Description', 'compression class (derived)',
                         'Price', 'MSRP', 'size', 'color', 'style(derived)', 'toe(derived)', 'band(derived)', 'Product URL', 'category URL'])
    exceptionFileWriter = csv.writer(open(outputpathBasic + "/output/ExceptionUrls" + strftime("%Y%m%d-%H-%M-%S") + ".csv", 'w', newline=''))
    exceptionFileWriter.writerow(["Brand", "Category", "Exception URL", 'Note'])
    startURL = 'http://www.foryourlegs.com'
    allBrandList = ['Activa', 'CEP', 'Circaid', 'Jobst', 'Juzo', 'Mediven', 'Sigvaris', 'Therafirm', 'Truform', 'Venosan']
    brandList = ['Activa', 'CEP', 'Jobst', 'Juzo', 'Mediven', 'Sigvaris', 'Truform']
    styleList = ['knee high', 'thigh high', 'maternity pantyhose', 'waist attachments', 'waist', 'maternity', 'chaps', 'capri', 'bermuda',
                 'armsleeve', 'glove', 'gauntlet', 'footcap', 'mini crew', 'crew', 'sleeveless vest', 'body breif with sleeves',
                 'abdominal pelvic garment', 'one-leg pantyhose', 'two-leg pantyhose', 'pantyhose', 'no zipper', 'zipper', 'liner',
                 'knee', 'thigh', 'ankle','chap','athletic']
    brandXpath = '//ul[@id="vnavmenu"]/li/a['
    for brandXpathElement in brandList:
        brandXpath += 'contains(text(),"' + brandXpathElement + '") or '
    brand_nodes = etree.XPath(brandXpath[:-4] + "]")
    '''brand_nodes = etree.XPath('//ul[@id="vnavmenu"]/li/a[contains(text(),"Jobst") or contains(text(),"Activa") '
                              'or contains(text(),"Sigvaris") or contains(text(),"Mediven") or contains(text(),"Cep")'
                              'or contains(text(),"Juzo") or contains(text(),"Truform")]')
    '''
    category_nodes = etree.XPath('//td[@class = "ColumnTitles"]/a')
    subcategory_nodes = etree.XPath('//td[@class="DialogBox"]')
    # nextPage = etree.XPath('//td[@align = "center"]//a[contains(@href,"page")]//@href')
    nextPage = etree.XPath('//img[contains(@alt , "Next page")]/ancestor::a/@href')
    item_nodes = etree.XPath('//div[@itemtype="http://schema.org/Product"]')
    try:
        sleepForSomeTime()
        xmlTree = get_html_doc(startURL)
    except:
        exceptionFileWriter.writerow('start url not found')
        logger.error("Not able to fetch start url , ", exc_info=True)

    brands = brand_nodes(xmlTree)
    productCounts = dict()
    for brand in brandList:
        productCounts[brand.upper()] = 0
    for brand in brands:
        brandurl = ''.join(brand.xpath('./@href'))
        brand_url = startURL + '/' + brandurl
        logger.info("Brand_Url: " + brand_url)
        brandName = ''.join(brand.xpath('./@title')).upper()
        logger.info("BrandName: " + brandName)
        try:
            sleepForSomeTime()
            categoriesTree = get_html_doc(brand_url)
        except:
            exceptionFileWriter.writerow([brandName.strip(), '', brand_url, 'brandurl not found'])
            logger.error("Not able to fetch brandurl , ", exc_info=True)
        categories = category_nodes(categoriesTree)
        for category in categories:
            categoryurl = ''.join(category.xpath('./@href'))
            category_url = startURL + '/' + categoryurl
            logger.info("Category_Url " + category_url)
            categoryName = ''.join(category.xpath('./strong/text()'))
            logger.info("CategoryName " + categoryName)
            i = 1
            flag = 0
            while i:
                sleepForSomeTime()
                try:
                    subCategoryTree = get_html_doc(category_url)
                except:
                    exceptionFileWriter.writerow([brandName.strip(), '', category_url, 'category_url not found'])
                    logger.error("category_url error , ", exc_info=True)
                try:
                    sleepForSomeTime()
                    next_page = nextPage(subCategoryTree)[1]
                    # logger.info("Next_Page " + next_page)
                except:
                    try:
                        subCategoryTree = get_html_doc(category_url)
                        flag = 1
                    except:
                        exceptionFileWriter.writerow([brandName.strip(), '', category_url, 'subcategoryurl not found'])
                        logger.error("subcategory , ", exc_info=True)
                items = subcategory_nodes(subCategoryTree)
                for item in items:
                    try:
                        itemurl = ''.join(item.xpath('descendant::div[contains(@style,"padding-bottom")]/following-sibling::a//@href'))
                        item_url = startURL + '/' + itemurl
                        logger.info("Product Url " + item_url)
                        sleepForSomeTime(True)

                        try:
                            itemTree = get_html_doc(item_url)
                        except:
                            exceptionFileWriter.writerow('Product url not found')
                            logger.error("itemTree , ", exc_info=True)
                        itemSeries = item_nodes(itemTree)
                        for product in itemSeries:
                            product_Text = ''.join(product.xpath('descendant::div[@class="DialogTitle"]/span/text()'))
                            # print("product_Text",product_Text)

                            compression = ''.join(re.findall("|".join([r'\d+[-]\d+\s?mmhg', r'-\s?\d+mmhg', r'\d+\s?mmhg',r'\d+[-]\d+']), product_Text, re.I))

                            # print(compression1)
                            # sku_Text = ''.join(product.xpath('descendant::div[@class="ProductDetailText"]/span[@id="product_code"]//text()'))
                            # print("sku_Text",sku_Text)
                            retailPrice = ''.join(product.xpath('normalize-space(descendant::div[@class="ProductDetailText"]/span[@class="MarketPrice"]//text())'))
                            # print(retailPrice)
                            productPrice = ''.join(product.xpath('descendant::div[@class ="ProductDetailText"]//span[@id="product_price"]//text()'))
                            # print(productPrice)
                            size = ','.join(product.xpath('//div[@style="padding-bottom: 6px;"][1]//text()')[4:-2:2])
                            # print(size)
                            color = ','.join(product.xpath('//div[@style="padding-bottom: 6px;"][2]//text()')[4:-2:2])
                            # print(color)
                            '''style_pattern = r'\b(?:Knee Highs|Thigh Highs|Knee High|Thigh High|Pantyhose|Maternity Pantyhose|Waist Attachment|Waist|Maternity|Chaps|Capri|Bermuda|Arm Sleeve|Glove| Gauntlet|' \
                                      r'Hip Attachment|Mini Crew | Crew |Sleeveless Vest | Body Breif With Sleeves | Diamond Pattern |Abdominal Pelvic Garment' \
                                      r'One-Leg Pantyhose|Two-Leg Pantyhose | Zipper | Liner | No Zipper | Calf Sleeves | Ankle)\b'
                                      '''
                            # style = ','.join(re.findall(style_pattern, product_Text, re.I))
                            style = ''
                            for styles in styleList:
                                if re.sub(' ', '', styles.lower()) in re.sub(' ', '', product_Text.lower()):
                                    style = styles
                                    break
                            # print(style)
                            toe_pattern = r'\b(?:open Toe | closed toe )\b'
                            toe = ','.join(re.findall(toe_pattern, product_Text,re.I)).strip()
                            # print(toe)
                            band_pattern = r'\b(?:with sil[i]*cone|w/ sil[i]*cone|w/ [a-zA-Z ]+ sil[i]*cone|with [a-zA-Z ]+ sil[i]*cone)\b'
                            band = ''.join(re.findall(band_pattern, product_Text,re.I)).strip()
                            # print(band)
                            productCounts[brandName.strip().upper()] = productCounts.get(brandName.strip().upper(), 0) + 1
                            fileWriter.writerow([brandName.strip(), categoryName.strip(), product_Text.strip(), compression.strip()
                                                    , productPrice.strip(), retailPrice.strip(), size, color, style, toe, band, item_url.strip(), category_url.strip()])
                    except:
                        exceptionFileWriter.writerow([brandName.strip(), '', category_url, 'item_url error'])
                        logger.error("product , ", exc_info=True)
                if next_page:
                    category_url = startURL + '/' + next_page
                    logger.info('Next_Page_Url ' + category_url)
                else:
                    i = 0
                if flag:
                    break
    # sendMailUtil3.sendMail("For Your Legs ", outputFileName, productCounts, programStartTime, ", ".join(brandList))
    constructMailUtil.constructAndCreateMailFile("For Your Legs v2", outputFileName, productCounts,
                                                 programStartTime, ", ".join(brandList), outputpathBasic + "\MAIL")
    logger.info("Finished")
