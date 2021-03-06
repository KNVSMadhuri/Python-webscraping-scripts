import re
import urllib2
import urlparse
import lxml.html as etree
import traceback
import pandas as pd
def clean_data(var):
	var=var.replace('&amp;','&').replace('quot;','"').replace('&gt;','>').replace('\t','').strip()
	return var
def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')
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
			for table in categories:
				header = [text(th) for th in table.xpath('//th')]        
				data = [[text(td) for td in tr.xpath('td')]  
				for tr in table.xpath('//tr')]                   
					data = [row for row in data if len(row)==len(header)]    
					data = pd.DataFrame(data, columns=header)                
					print(data)
						
							
							
						
							
						
get_year_listings(START_URL)

