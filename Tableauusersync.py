import tableauserverclient as TSC
import re
import requests
from requests.auth import HTTPBasicAuth
import datetime
import pathlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyodbc
def sendEmail(send_to_email,ntlogin,fullname):
    email = "abc@corp.abc.com"
    CC = ["abc@corp.abc.com"] 
    subject = ntlogin+" is added to tableau server"
    message = "Hi "+fullname+",\n\t\t Your account is added to tableau server.Please login to https://tableau.corp.abc.com and verify.If there is any issue create ticket in http://go/tableausupport"
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = send_to_email
    msg['Subject'] = subject
    msg['Cc'] = ', '.join( CC )
    recipients = [send_to_email] + CC
    msg.attach(MIMEText(message, 'plain'))
    mserver = smtplib.SMTP('ax.vip.abc.com', 25)
    #server.starttls()
    #server.login(email, password)
    text = msg.as_string()
    mserver.sendmail(email,recipients, text)
    mserver.quit()


def createNewUser(user_name):
    print (user_name+' doesnt exists on the server')
    newU = TSC.UserItem(user_name, 'Interactor')
    newU = server.users.add(newU)
    print (user_name+' added to server')
    if user_name in clsfdusers:
        email=user_name+"@abcd.com"
    elif user_name in clsfdDKusers:
        email=user_name+"@abcd.com"
    else:
        email=user_name+"@abc.com"
    newU.email=email
    newU=server.users.update(newU)
    sendEmail(email,user_name,user_name)
    return newU

def main(logfilename):
    print ("Inside main function")
    fname = pathlib.Path(logfilename) #Input log file

    if fname.exists():
        fh = open(fname,encoding="utf8") #create file handle
        lst=list() #initiate list object
        missingnames=list() #Define another list object for storing failed logins
        count = 0
        #Below for loop scan thru the log file and get all the username who has failed login attempts
        for line in fh:
            if not line.find('com.tableausoftware.domain.exceptions.LoginFailedException: Failed to find the system user {UserIdentity[idProvider=, domain=local')!=-1:continue
            lst=line.split()
            print (lst)
            start='='
            end='@'
            s=re.findall(re.escape(start)+"(.*)"+re.escape(end),lst[9])[0]
            if s in missingnames:continue
            count+=1
            missingnames.append(re.findall(re.escape(start)+"(.*)"+re.escape(end),lst[9])[0])
            #    print (names)
            #names=list(set(names))
            #print (names)
            #print("There were", count, "failed user logins on the server")

            # Below for loop take users from missingnames list object one by one and add to the server if it doesnt exist
        for user in missingnames:
            if user in clsfdusers:
                with server.auth.sign_in(tableau_auth_clsfd):
                    req_option=TSC.RequestOptions()
                    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals,user))
                    name,pagination_item=server.users.get(req_option)
                    #print(pagination_item.total_available)
                    if pagination_item.total_available == 0:
                        usrItem=createNewUser(user)
                        print (usrItem.id)
                        print ("User creation is done on Classifieds")
                        #updateNewUser(usrItem,user)
                        #print ("Update is done")
            elif user in clsfdDKusers:
                with server.auth.sign_in(tableau_auth_clsfdDK):
                    req_option=TSC.RequestOptions()
                    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals,user))
                    name,pagination_item=server.users.get(req_option)
                    #print(pagination_item.total_available)
                    if pagination_item.total_available == 0:
                        usrItem=createNewUser(user)
                        print (usrItem.id)
                        print ("User creation is done on Classifieds DK")
                        #updateNewUser(usrItem,user)
                        #print ("Update is done")
            else:
                with server.auth.sign_in(tableau_auth):
                    req_option=TSC.RequestOptions()
                    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals,user))
                    name,pagination_item=server.users.get(req_option)
                    if pagination_item.total_available == 0:
                        usrItem=createNewUser(user)
                        print (usrItem.id)
                        print ("User creation is done Default site")
                        #updateNewUser(usrItem,user)
                        #print ("Update is done")


clsfdusers=[]
clsfdDKusers=[]


conn = pyodbc.connect("DSN=EmpDSN;", autocommit = True)
cursor = conn.cursor()


cursor.execute("SELECT uid FROM ACCESS_VS.LDAP_EMPLY where companyCode in ('0054','0057','0058','0116','0445','0450','0451','0452','0454','0458','0465','0475','0476','0477','0478','0479','0481','0482','0483','0484','9025') and RCRD_END_DT='9999-12-31'")
for row in cursor.fetchall():
    empname=str(row).replace("(","")
    empname=empname.replace(")","")
    empname=empname.replace(",","")
    empname=empname.replace("'","")
    empname=empname.replace("'","")
    clsfdusers.append(empname.strip())
print (clsfdusers)
cursor.execute("SELECT uid FROM ACCESS_VS.LDAP_EMPLY where companyCode in ('0465','0915')  and RCRD_END_DT='9999-12-31'")
for row in cursor.fetchall():
    empname=str(row).replace("(","")
    empname=empname.replace(")","")
    empname=empname.replace(",","")
    empname=empname.replace("'","")
    empname=empname.replace("'","")
    clsfdDKusers.append(empname.strip())
print (clsfdDKusers)

# create an auth object for default site
tableau_auth = TSC.TableauAuth('tableau_admin', ' ')
# Create an auth for classifieds
tableau_auth_clsfd = TSC.TableauAuth('tableau_admin',' ',site_id='site1')
tableau_auth_clsfdDK = TSC.TableauAuth('tableau_admin',' ',site_id='site2')
# create an instance for your server
server = TSC.Server('http://tableau.corp.abc.com')
server.use_server_version()
from datetime import date
today = str(date.today())
print (today)
previousday=str(date.today()--datetime.timedelta(-1))
main("/TableauServer/data/tabsvc/logs/vizportal/vizportal_node1-0.log")
main("/TableauServer/data/tabsvc/logs/vizportal/vizportal_node1-0.log."+previousday)
main("/TableauServer/data/tabsvc/logs/vizportal/vizportal_node1-0.log."+today)


server.auth.sign_out()
