import re
import urllib2
import urlparse
import lxml.html as etree
import traceback
def clean_data(var):
	var=var.replace('&amp;','&').replace('quot;','"').replace('&gt;','>').replace('\t','').strip()
	return var
def X(data):
	try:
		return ''.join([chr(ord(x)) for x in data]).decode('utf8','ignore').encode('utf8')
	except ValueError:
		return data.encode('utf8')

def get_html_doc(url):
		url=url
		html=etree.parse(url)
		#print("HTML")
		#print(html)
		return(html)
START_URL="http://www.occ.gov/topics/licensing/interpretations-and-actions/index-interpretations-and-actions.html"
get_html_doc(START_URL)

def get_year_listings(START_URL):
	html=get_html_doc(START_URL)
	#print html
	links=html.xpath('//ul[3]//li//a/@href')
	print links
	for link in links:
		href=urlparse.urljoin(START_URL,link)
		#print href
		href_html=get_html_doc(href)
		#print href_html
		mnth_over_year=href_html.xpath('//table//td[2]//p//a/@href')
		#print mnth_over_year
		for mnth in mnth_over_year:
			mnth=urlparse.urljoin(START_URL,mnth)
			#print mnth
			mnth_html=get_html_doc(mnth)
			#print mnth_html
			categories=mnth_html.xpath('//table[@class="table_brdr"]')
			for category in categories:
				category_name=category.xpath('//table[@class="table_brdr"]//preceding-sibling::tr//text()')
				#print category_name
				rows=category.xpath('.//tr[not(@class)]')
				for row in rows:
					letter_number=''.join([X(clean_data(r)) for r in row.xpath('.//td[1]//a/text()')])
					#print letter_number
					if letter_number:
						letter_href=row.xpath('.//td[1]/a/@href')[0]
						#print letter_href
						topic=''.join([X(clean_data(r)) for r in row.xpath('.//td[2]//text()')])
						#print topic
						date=re.findall('\d+/\d+/\d+',topic)
						print date
						if date:
							#print("HI")
							date=date[0]
							#print date
						else:
							date=''
							#print date
						letter_href=urlparse.urljoin(mnth,letter_href)
						print letter_href
						
							
							
						
							
						
get_year_listings(START_URL)

