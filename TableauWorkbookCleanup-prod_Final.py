import requests # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET # Contains methods used to build and parse XML
import json
from getpass import getpass
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

# The namespace for the REST API is 'http://tableausoftware.com/api' for Tableau Server 9.0
# or 'http://tableau.com/api' for Tableau Server 9.1 or later
xmlns = {'t': 'http://tableau.com/api'}

#This function sign in to tableau server and return auth token, site id and user id
def signin():
    print ("inside signin")
    url = "https://tableau.corp.abcd.com/api/3.14/auth/signin"

    payload = json.dumps({
  "credentials": {
    "personalAccessTokenName": "pp",
    "personalAccessTokenSecret": "baNWLsfhRwy3Vyydton8xg==:ezI1qKhRRHWmVr5wKdvI0T0dpemh2Oit",
    "site": {
      "contentUrl": ""
    }
  }
})
    headers = {'Content-Type': 'application/json'}
    server_response = requests.request("POST", url, data=payload, headers=headers,verify=False)
    print (server_response.text)
    # Reads and parses the response
    parsed_response=ET.fromstring(server_response.text)
    # Gets the auth token and site ID
    token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
    print ("token:",token)
    site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')
    user_id = parsed_response.find('.//t:user', namespaces=xmlns).get('id')
    return token,site_id,user_id

#This function close the active connection and invalidates authentication token
def sign_out(auth_token):
    url = "https://tableau-qa.corp.abcd.com/api/3.3/auth/signout"
    server_response = requests.post(url, headers={'x-tableau-auth': auth_token},verify=False)
def move_workbook(auth_token,site_id,workbookid):
    url="https://tableau.corp.abcd.com/api/3.14/sites/{}/workbooks/{}".format(site_id,workbookid)
    payload = "<tsRequest>\n  <workbook>\n\t    <project id=\"be102cd4-677a-4e4f-9355-0a197ebf8e8e\" />\n </workbook>\n</tsRequest>"
    server_response = requests.put(url, headers={'x-tableau-auth': auth_token},data=payload,verify=False)

def getworkbookid(auth_token,site_id,workbookname):
    url="https://tableau.corp.abcd.com/api/3.14/sites/{}/workbooks?filter=name:eq:{}".format(site_id,workbookname)
    print (url)
    server_response = requests.get(url, headers={'x-tableau-auth': auth_token},verify=False)
    xml_response = ET.fromstring(server_response.text)
    try:
        total_available = xml_response.find('.//t:pagination', namespaces=xmlns).attrib['totalAvailable']
        total_available=int(total_available)
        print ("Total workbooks",total_available)
        if total_available == 1:
            workbookid=xml_response.find('.//t:workbook', namespaces=xmlns).attrib['id']
            print ("Workbook id ",workbookid)
            workbookurl=xml_response.find('.//t:workbook', namespaces=xmlns).attrib['webpageUrl']
            print (workbookurl)
            workbookurl=workbookurl.replace('http://rna05z-7cw1.stratus.rno.abcd.com','https://tableau.corp.abcd.com')
            workbookurl=workbookurl.replace('http://lvc04x-2vd1.stratus.lvs.abcd.com','https://tableau.corp.abcd.com')
            print ("Workbook url : ",workbookurl)
            ownername=xml_response.find('.//t:owner', namespaces=xmlns).attrib['name']
            print ("Workbook Owner : ",ownername)
            projectname=xml_response.find('.//t:project', namespaces=xmlns).attrib['name']
            print ("project name : ",projectname)
            message = "Hi "+ownername+",\nThis workbook has not been viewed by anyone in the past 180 days. We have moved your workbooks temporarily to the folder \"Not Viewed for 180 days \"  and they will be permanently deleted on "+finaldate+"\n If you want to have coopy of this workbook then you can download and keep it on your computer\n Workbook URL : "+workbookurl
            print (message)

            subject= 'Unused Tableau Workbooks Scheduled for Deletion'
            #Move the workbook to Not viewed for 180 days folder
            move_workbook(auth_token,site_id,workbookid)


            html_table = ""
            html_table += "<p>Hi,</p>"
            html_table += "<p>We have identified you as the publisher of the this workbook on Tableau server and it has not been viewed by anyone in the past 180 days. In order to delete stale contents from tableau server, we have moved your workbook temporarily to the folder <b>\"Not Viewed for 180 days \"</b>  and they will be permanently deleted on "
            html_table += "<b>"+finaldate+"</b>"
            html_table += "<p><font color=\"red\"> If you still need the workbooks on the server then please follow the <a href=\"https://wiki.vip.corp.abcd.com/pages/viewpage.action?pageId=454006854\">instructions</a > and move it back to your original folder by end of </font>" + "<font color=\"red\">" + finaldate + "</font>"
            html_table += "<p>We therefore recommend that you download and save a copy of these workbooks for your reference. See <a href=\"https://help.tableau.com/current/pro/desktop/en-us/export.htm\">instructions</a> for downloading workbooks on Tableau Server.</p>"
            html_table += "<table id='cr_tbl' class='sofT' cellspacing='0'>"
            html_table += "<tr class='lightGreyTitle'><td width='30%'>Workbook Name</td><td width='20%'>Previous Project Name</td><td width='10%'>Owner Name</td><td width='20%'><b><font color=\"red\">Workbook Deletion Date </font></b></td></tr>"
            html_table += "<tr>"
            html_table += "<td><a href=\""+ workbookurl +"\">"+ workbookname + "</a></td>"
            html_table += "<td>"+ projectname + "</td>"
            html_table += "<td>"+ ownername + "</td>"
            html_table += "<td><b><font color=\"red\">"+ finaldate + "</font></b></td>"
            html_table += "</tr>"
            From = "DL-abcd-apd-tableau-admin@corp.abcd.com"
            To=ownername+"@abcd.com"
            CC = ["DL-abcd-apd-tableau-admin@abcd.com"]
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = From
            msg['To'] = To
            msg['Cc'] = ', '.join( CC )
            recipients = [To] + CC
            html_message = ""
            for line in open('template.html'):
                html_message += line.replace('{html_table}', html_table)
            msg.attach(MIMEText(html_message, 'html'))
            mserver.sendmail(msg['From'], recipients, msg.as_string())
    except:
        pass






#This function return total number of users for the give site
'''def get_usercount(auth_token,site_id):
    url = "https://tableau-qa.corp.abcd.com/api/3.3/sites/{}/users".format(site_id)
    #print("url:",url)
    server_response = requests.get(url, headers={'x-tableau-auth': auth_token},verify=False)
    #print(server_response.text)
    xml_response = ET.fromstring(server_response.text)
    total_available = xml_response.find('.//t:pagination', namespaces=xmlns).attrib['totalAvailable']
    total_available=int(total_available)
    return total_available

#This function get user name and user id and stores it in InvaildUsers list as dictionary object
def get_user(auth_token,site_id,pagesize,pagenumber):
    url = "https://tableau-qa.corp.abcd.com/api/3.3/sites/{}/users?pageSize={}&pageNumber={}".format(site_id,pagesize,pagenumber)
    server_response = requests.get(url, headers={'x-tableau-auth': auth_token},verify=False)
    xml_response = ET.fromstring(server_response.text)
    users=xml_response.findall('.//t:user', namespaces=xmlns)
    for user in users:
        InvalidUsers.append({'name':user.get('name'),'id':user.get('id')})'''


pxuser = input("Username: ")
pxpass = getpass("Password (Pin + Yubikey): ")
env_px = f"http://{pxuser}:{pxpass}@c2sproxy.vip.abcd.com:8080/"
os.environ['http_proxy']=env_px
os.environ['https_proxy']=env_px
source_auth_token,source_site_id,source_user_id=signin()
print (source_auth_token,source_site_id,source_user_id)

mserver = smtplib.SMTP('atom.corp.abcd.com', 25)
ttoday=datetime.datetime.now()
newtime=ttoday + datetime.timedelta(days=14)
finaldate=newtime.strftime("%m/%d/%y")
print (finaldate)

# This can be replaced by running query against postgres and fetch the unused workbooks and stored it on workbooklist list variable
workbooklist=['Opportunity Sizing Dashboard',
'AIT Report for Splunk',
'Customer Call and Chat Metrics',
'GCX Reports',
'HR Onboarding',
'MSB',
'CGP, Brand, & Marketing Jira Projects',
'GCX Jira Projects',
'Product Engineering Jira Projects',
'Regional Dev & Charity Jira Projects',
'SX List Jira Projects',
'US Recurring Campaigns',
'CPS 1 deep dive - aspect fill rate- all population, adoption- temporary location ',
'CPS 1 deep dive - aspect fill rate- all population- temporary location ',
'M0 Tech Infra - Release Calendar ']
for workbook in workbooklist:
    getworkbookid(source_auth_token,source_site_id,workbook)
