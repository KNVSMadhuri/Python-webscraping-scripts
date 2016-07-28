import re
import urllib2
import urlparse
import lxml.html as etree
import traceback
def get_html_doc(url):
	url=url
	html=etree.parse(url)
	print("HTML")
	print(html)
	return(html)
START_URL = "http://www.imdb.com/search/name?birth_monthday=11-14&refine=birth_monthday&ref_=nv_cel_brn_1"
get_html_doc(START_URL)
html_doc = get_html_doc(START_URL)
print html_doc
i=1
while i:
	get_Serial_No = html_doc.xpath('//td[@class="number"]/text()')
	print get_Serial_No
	get_Image_url = html_doc.xpath('//td[@class="image"]/a//@src')
	print get_Image_url,len(get_Image_url)
	get_Name = html_doc.xpath('//td[@class="name"]/a/text()')
	print get_Name
	Next_Page = html_doc.xpath('.//node()[contains(text(),"Next")]/@href')
	print Next_Page[-1]
	Next_Page = ['http://www.imdb.com' + Next_Page[-1]]
	print Next_Page
	Next_Page = ''.join(Next_Page)
	print Next_Page
	html_doc = get_html_doc(Next_Page)
	if not Next_Page:
		i=0
