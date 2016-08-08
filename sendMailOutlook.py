import win32com.client
import configparser
import sys

def sendMail():
    config = configparser.RawConfigParser()
    config.read(outputpathBasic+"\mail.config")
    olMailItem = 0x0
    obj = win32com.client.Dispatch("Outlook.Application")
    newMail = obj.CreateItem(olMailItem)
    newMail.Subject = config.get('mailConfigs', 'subject')
    f=open(config.get('mailConfigs', 'mailFile'))
    newMail.HTMLBody  = f.read()
    #newMail.Body = "body text"
    newMail.To = "anish.reddy@affineanalytics.com;apoorva.kumar@affineanalytics.com;ashish.kumar@affineanalytics.com;bhawna.jain@affineanalytics.com;chavi.bhaskar@affineanalytics.com;kavitha.kh@affineanalytics.com;munukutla.madhuri@affineanalytics.com;siddharth.jindal@affineanalytics.com"
    attachment1 = config.get('mailConfigs', 'outputFile')
    newMail.Attachments.Add(attachment1)
    newMail.Send()

if __name__ == '__main__':
    outputpathBasic = sys.argv[1]
    sendMail()