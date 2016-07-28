#  ---------------------------------------------------------------------
#   KNOWLEDGE MOSAIC CONFIDENTIAL
#   
#   [2009] - [2013] LexisNexis, a division of Reed Elsevier Inc. All Rights Reserved.
#   All Rights Reserved.
#   
#   NOTICE:  All information contained herein is, and remains
#   the property of LexisNexis, a division of Reed Elsevier Inc., and its suppliers,
#   if any.  The intellectual and technical concepts contained
#   herein are proprietary to LexisNexis, a division of Reed Elsevier Inc.,
#   and its suppliers and may be covered by U.S. and Foreign Patents,
#   patents in process, and are protected by trade secret or copyright law.
#   Dissemination of this information or reproduction of this material
#   is strictly forbidden unless prior written permission is obtained
#   from LexisNexis, a division of Reed Elsevier Inc.
#  ---------------------------------------------------------------------
'''
Created on Feb 25, 2016

@author: Prabhakar Moka

'''

from speedfeed.sfscript import ParseScriptBase, ScriptDisabled
from speedfeed.sfdocument import DocumentBase
import speedfeed.sfconfig as sfconfig
import sqlalchemy as sa
import sqlalchemy.orm as saorm
from datetime import datetime
import mx.DateTime as mx
import re
import lxml.etree as etree
import traceback
import urllib2
import urlparse
import urllib
import os


BASE_URL = "http://www.nhtsa.gov/"
START_URL = "http://www.nhtsa.gov/Testimony"
class Testimony(DocumentBase):
    
    def __init__(self, ps):
        super(Testimony, self).__init__(ps) 
        self.LNDocumentTitle = None  
        self.LNDate = None
        self.LNOtherSpeaker = None
        self.LNOtherSites = None
        
    
        
class PS_DOT_NHSTA_TestimonyScript (ParseScriptBase):

    printDebug = False #keep set to False
    
    def __url2Pathname(self, url):
        p = urlparse.urlparse(url)
        return urllib.url2pathname(p.path)

    def clean_data(self, data):
    
        if isinstance(data, list):
            text = ''
            for item in data:
                text = text + '%s'%item
            text = text.strip()
        elif isinstance(data, basestring):
            text = data
            
        text = self.convertToAscii(text.strip())
        text = text.replace('&#160;', ' ').replace('\n', ' ').replace('&#8211;', '-').replace('&#8217;', '\'').replace('\r', ' ').replace('&#8220;', '"').replace('&#8221;', '"').replace('&#8212;', '-').replace('&#8209;', '-').replace('&#8216;', "'").replace('&#8226;', ".").strip()
        text = re.sub(r"\s{2,}", r" ", text)
        text = re.sub(r"&#160;?", " ", text).rstrip()
        return text
    
    
        
        
    def runScript(self, context):
        # Map the above class to database table using SqlAlchemy
        files_table = sa.Table('DT_DOT_NHSTA_Testimony', self.dbms_metadata, autoload=True, schema=sfconfig.KMDB_SCHEMA)
        saorm.mapper(Testimony, files_table, version_id_col=files_table.c['versionId'])
        #Set XPaths and Regex
        Year_Nodes = etree.XPath('//select[@id="presentationYear"]//option//text()')
        #Document_Nodes = etree.XPath('//ul[@class="divided"]//li')
        Document_Nodes = etree.XPath('//div[@class="vgn-acpd-portlet"]/h3[@class="presentations"]')
        Next_Page = etree.XPath('//a[contains(text(), "Next")]/@href')

        
        try:
            xmlTree = self.cleanHTML(START_URL)
        except:
            self.sendErrorMsg("Could not connect to website '%s'"%START_URL)
            self.completeHarvest(context)
            return

        
        all_years = Year_Nodes(xmlTree)
        
        print 'all_years', all_years
        listing_urls = ["http://www.nhtsa.gov/Testimony?presentationYear="+yr for yr in all_years]
        #print 'listing_urls', listing_urls
        for listing in listing_urls:
            #listing = "http://www.nhtsa.gov/Testimony?presentationYear=2015"
            year = listing.split('=')[-1].strip()
            #break
            i = 1
            while i:
                self.stillAlive()
                try:
                    subTree = self.cleanHTML(listing)
                except:
                    self.sendErrorMsg("Could not connect to website '%s'"%listing)
                    self.completeHarvest(context)
                    return
                
                next_page = Next_Page(subTree)
                
                documents = Document_Nodes(subTree)
                if not documents:
                    i = 0
                for doc in documents:
                    try:
                        self.stillAlive()
                        pr = Testimony(self)
                        str_date = self.clean_data(doc.xpath('./following-sibling::div[1]/div[6]//text()'))
                        year_info = re.findall('\d{4}', str_date)
                        str_date = str_date if year_info else str_date+', '+year
                        pr.SourceUrl = self.makeUrl(doc.xpath('./following-sibling::ul[1]//a/@href')[0], listing)
                        try:
                            raw_data = urllib2.urlopen(pr.SourceUrl).read()
                        except:
                            continue
                        pr.UniqueId = pr.SourceUrl.split('/')[-1].strip().replace('+', '').replace('$', '').replace(',', '').replace(':', '').replace('.pdf', '').strip()
                        print 'UniqueId', pr.UniqueId
                        
                        pr.LNDocumentTitle = pr.Title = self.clean_data(doc.xpath('.//text()'))
                        pr.Date = pr.getDateFromString(str_date)
                        pr.LNDate = pr.Date.strftime('%m/%d/%Y')
                        pr.LNOtherSpeaker = self.clean_data(doc.xpath('./following-sibling::div[1]/div[2]//text()'))
                        pr.LNOtherSites = self.clean_data(doc.xpath('./following-sibling::div[1]/div[4]//text()'))
                        if self.printDebug == True: debug_info(pr)
                        gui = pr.checkForExisting()
                        if gui is not None:
                            continue
                        #print 'SourceUrl', pr.SourceUrl
                        if pr.parseDocData(bodyWrap='//div[@id="content"]/div[@class="vgn-acpd-portlet"][2]', junkTags="//img[contains(@src, 'images') and contains(@src, 'star')] | .//img[contains(@src, 'images') and contains(@src, 'check')]") == None:
                            continue
                                            
                        pr.commitData()
                    except ScriptDisabled:
                        self.sendInfoMsg("Script has been disabled. Raising error.")
                        raise ScriptDisabled
                    except urllib2.URLError: # Try again another time.
                        self.sendInfoMsg("Exception while opening page \n%s"%(traceback.format_exc()))
                        continue
                    except:
                        self.sendWarningMsg("Problem processing release %s, %s" % (pr.Title, traceback.format_exc()))
                        self.gotException = True
                        continue
                if next_page:
                    listing = self.makeUrl(next_page[0], listing)
                    print 'next_page', listing
                else:
                    i = 0
            
        self.completeHarvest(context)
        
                               
def debug_info(doc):
    pass
    print "\tTitle:\t\t%s" % doc.Title
    print "\tDate:\t\t%s" % doc.Date
    print "\tSourceUrl:\t%s" % doc.SourceUrl
    print "\tUniqueId:\t%s" % doc.UniqueId
    print "\n"
    
if __name__ == '__main__':
    import speedfeed.sfconfig as sfconfig

    PARSESCRIPTID = "PS_DOT_NHSTA_Testimony"
           
    script = PS_DOT_NHSTA_TestimonyScript(PARSESCRIPTID)
    script.noServer = True
    script.useCache = True
    script.printDebug = False
    script._runScript({sfconfig.CTX_FILESTOREPATH: "c:\\tmp\\webs\\www\\gateway\\DOT_NHTSA\\testimony\\",
                       sfconfig.CTX_RAWFILEPATH: "c:\\tmp\\webs\\www\\gateway\\DOT_NHTSA\\testimony\\raw\\",
                       sfconfig.CTX_FILEBASEURL: "file://c:/tmp/webs/www/gateway/DOT_NHTSA/testimony/"})

    print "DONE"
