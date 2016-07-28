import re
import urllib2
import traceback
from urllib2 import urlopen
from lxml.html import parse
def get_html_doc(url):
	page = urlopen(url)
	p = parse(page)
	#print p
	return p
START_URL = "https://www.doi.gov/pressreleases"
get_html_doc(START_URL)
html_doc = get_html_doc(START_URL)
#print html_doc
title_urls = html_doc.xpath('//div[@class="node-title"]/a/@href')
#print 'title_urls',title_urls,len(title_urls)
title_urls = ['https://www.doi.gov'+i for i in title_urls]
#print 'title_urls',title_urls,len(title_urls)
#Result = open('output.txt','w')

for url in title_urls[:1]:
	html_doc1 = get_html_doc(url)
	get_title = html_doc1.xpath('//h1[@id="page-title"]/text()')
	#print get_title
	str1 = ''.join(get_title)
	asciistring = str1.encode("utf-8")
	print asciistring
	
for url in title_urls[:1]:
	html_doc1 = get_html_doc(url)
	get_date = html_doc1.xpath('//div[@class="publication-date"]/text()')
	#print get_date
	date_string1= ''.join(get_date)
	print date_string1
