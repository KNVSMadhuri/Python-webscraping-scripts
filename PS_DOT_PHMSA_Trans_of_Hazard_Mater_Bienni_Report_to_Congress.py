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
Created on Mar 29, 2016

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


BASE_URL = "http://www.phmsa.dot.gov/"
START_URL = "http://www.phmsa.dot.gov/portal/site/PHMSA/menuitem.6f23687cf7b00b0f22e4c6962d9c8789/?vgnextoid=a43975811928d110VgnVCM1000009ed07898RCRD&vgnextchannel=a89f28973677d110VgnVCM1000009ed07898RCRD&vgnextfmt=print"

class StateHighwaySafetyPlans(DocumentBase):
    
    def __init__(self, ps):
        super(StateHighwaySafetyPlans, self).__init__(ps) 
        self.LNDocumentTitle = None  
        self.LNDate = None
        self.LNDocumentNumber = None
        
    
        
class PS_DOT_PHMSA_Trans_of_Hazard_Mater_Bienni_Report_to_CongressScript (ParseScriptBase):

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
        files_table = sa.Table('DT_DOT_PHMSA_Trans_of_Hazard_Mater_Bienni_Report_to_Congress', self.dbms_metadata, autoload=True, schema=sfconfig.KMDB_SCHEMA)
        saorm.mapper(StateHighwaySafetyPlans, files_table, version_id_col=files_table.c['versionId'])
        #Set XPaths and Regex
        doc_nodes = etree.XPath('//div[@id="related_downloads"]/ol/li/a')
    
        
        try:
            xmlTree = self.cleanHTML(START_URL)
        except:
            self.sendErrorMsg("Could not connect to website '%s'"%START_URL)
            self.completeHarvest(context)
            return

        docnodes = doc_nodes(xmlTree)
        print 'len', len(docnodes)
        for docnode in docnodes:
            try:
                self.stillAlive()
                shsp = StateHighwaySafetyPlans(self)
                shsp.SourceUrl = self.makeUrl(docnode.xpath('./td[5]/a/@href')[0], START_URL)
                shsp.UniqueId = shsp.SourceUrl.split('/')[-1].lower().replace('.pdf', '').strip()
                shsp.LNDocumentTitle = shsp.Title = 'Special Permit - '+self.clean_data(docnode.xpath('./td[3]//text()'))
                print 'uniqueId', shsp.UniqueId    
                shsp.Date = shsp.LNDate = self.clean_data(docnode.xpath('./td[4]//text()'))
                shsp.LNDocumentNumber = shsp.DocumentNumber = self.clean_data(docnode.xpath('./td[3]//text()'))       
                gui = shsp.checkForExisting()
                
                if gui is not None:
                    continue
                
                if shsp.parseDocData() == None:
                    continue
                               
                if self.printDebug == True: debug_info(shsp)              
                shsp.commitData()
                
            except ScriptDisabled:
                self.sendInfoMsg("Script has been disabled. Raising error.")
                raise ScriptDisabled
            except urllib2.URLError: # Try again another time.
                self.sendInfoMsg("Exception while opening page \n%s"%(traceback.format_exc()))
                continue
            except:
                self.sendWarningMsg("Problem processing release %s, %s" % (shsp.Title, traceback.format_exc()))
                self.gotException = True
                continue

            
                           
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

    PARSESCRIPTID = "PS_DOT_PHMSA_Trans_of_Hazard_Mater_Bienni_Report_to_Congress"
           
    script = PS_DOT_PHMSA_Trans_of_Hazard_Mater_Bienni_Report_to_CongressScript(PARSESCRIPTID)
    script.noServer = True
    script.useCache = True
    script.printDebug = False
    script._runScript({sfconfig.CTX_FILESTOREPATH: "c:\\tmp\\webs\\www\\gateway\\DOT_PHMSA\\trans_of_hazard_mater_bienni_report_to_congress\\",
                       sfconfig.CTX_RAWFILEPATH: "c:\\tmp\\webs\\www\\gateway\\DOT_PHMSA\\trans_of_hazard_mater_bienni_report_to_congress\\raw\\",
                       sfconfig.CTX_FILEBASEURL: "file://c:/tmp/webs/www/gateway/DOT_PHMSA/trans_of_hazard_mater_bienni_report_to_congress/"})

    print "DONE"
