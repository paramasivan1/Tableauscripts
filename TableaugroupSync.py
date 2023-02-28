import tableauserverclient as TSC
import json
import requests
from requests.auth import HTTPBasicAuth
from xml.etree import ElementTree as ET
# create an auth object
tableau_auth = TSC.TableauAuth('tableau_admin', ' ')
# create an instance for your server
server = TSC.Server('http://tableau.corp.abc.com')
dl_api_auth_user = "bi_dev"
dl_api_auth_passwd = "312E3FAsdf8B513dfdfs19A6"
dl_api_auth_values = HTTPBasicAuth(dl_api_auth_user, dl_api_auth_passwd)
def getDL(dlname):
    url = "	https://dlmanager.corp.abc.com/API/DL/members/recursive/"+dlname
    # Make a request to the endpoint using the correct auth values
    response = requests.get(url, auth=dl_api_auth_values,verify=False)
    #print ("response text")
    #print (response.text)
    return response.text
def isDLexists(dlname):
    url = "https://dlmanager.corp.abc.com/API/DL/exist/"+dlname
    # Make a request to the endpoint using the correct auth values
    response = requests.get(url, auth=dl_api_auth_values,verify=False)
    #print (response.text)
    #print ("response text")
    #print (response.text)
    return response.text
def getUserDetails(user_name):
    url = "https://dlmanager.corp.abc.com/API/User/properties/"+user_name
    # Make a request to the endpoint using the correct auth values
    response = requests.get(url, auth=dl_api_auth_values,verify=False)
    return response
def signin():
    # call the sign-in method with the auth object
    server.auth.sign_in(tableau_auth)
def signout():
    server.auth.sign_out()
def isTableauGroupExists(dlname):
    for group in TSC.Pager(server.groups):
        if group.name == dlname:
            return 'true'
            break
    return 'false'
def getTableauGroupItem(dlname):
    for group in TSC.Pager(server.groups):
        if group.name == dlname:
            return group
def gettableauGroupMembers(dlname):
    Usr_List=[]
    #print (type(Usr_List))
    for group in TSC.Pager(server.groups):
        if group.name == dlname:
            #print (group.name)
            #print ("users in the group...")
            #print(dir(group))
            #print(type(group))
            server.groups.populate_users(group)
            for user in group.users:
                Usr_List.append(user.name)
    return Usr_List
def isUserExistsonTableau(username):
    req_option=TSC.RequestOptions()
    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals,username))
    all_users,pagination_item=server.users.get(req_option)
    if pagination_item.total_available !=0:
        return 'true'
    else:
        return 'false'
def createNewUser(user_name):
    #print (user_name+' doesnt exists on the server')
    try:
        newU = TSC.UserItem(user_name, 'Interactor')
        newU = server.users.add(newU)
        #print (user_name+' added to server')
        email=user_name+"@abc.com"
        newU.email=email
        #newU.fullname=user_name
        newU=server.users.update(newU)
        #sendEmail(email,user_name,user_name)
        return newU
    except:
        print ("user already exists and return User Item object")
        E_user=getUserItem(user_name)
        print(user_name+"exists")
        return E_user
def createnewTableauGroup(dlname): #This function creates new group on tableau server
    newgroup = TSC.GroupItem(dlname)
    newgroup = server.groups.create(newgroup)
    return newgroup

def addUserToExistinGroup(TabGroup,User_Item):
    if server.groups.populate_users(TabGroup) is not None:
        server.groups.populate_users(TabGroup)
        for user in TabGroup.users:
            #print ("user")
            try:
                server.groups.add_user(TabGroup,User_Item.id)
                print ("User added"+User_Item.name)
            except:
                continue
    else:
        server.groups.add_user(TabGroup,User_Item.id)
def addUserNewGroup(TabGroup,User_Item):
        server.groups.add_user(TabGroup,User_Item.id)
def deleteUsersFromGroup(TabGroup,User_Item):
        server.groups.remove_user(TabGroup,User_Item.id)
def getUserItem(username):
    req_option=TSC.RequestOptions()
    req_option.filter.add(TSC.Filter(TSC.RequestOptions.Field.Name, TSC.RequestOptions.Operator.Equals,username))
    for usr in TSC.Pager(server.users,req_option):
        return usr
signin()
print ('signedin')

DLlist=['DL-abc-AML-Global-Leader-Report','DL-abc-AML-US-Leader-Report','DL-abc-AML-EU-Leader-Report','DL-abc-AML-UK-Leader-Report','DL-abc-AML-AU-Leader-Report','DL-abc-AML-ROW-Leader-Report','DL-abc-DL-abc-DE-Category-Leads','DL-abc-DL-AM-All-Vertical','DL-abc-ADI-BIPL-TEAM','DL-abc-HS-Core','DL-abc-DL-abc-LoyaltyExperience-ScrumTeam','DL-abc-GCX-Tableau-User','DL-abc-GPBR-RISK-DecisionScience','DL-abc-Business-Rules','DL-abc-SellerInsights-Daml','DL-abc-Comp-Viz','DL-abc-Comp-Viz-People-Team','DL-abc-Ads-Product-Analytics','DL-abc-ITSS-TABLEAU-TECH','DL-abc-KO-Active-Buyer-monthly-report','DL-abc-Smile-card-weekly-report','DL-abc-Smile-club-weekly-NewSubscribersBySource-report','DL-abc-Strategy','DL-abc-PerformanceMarketing_All','DL-abc-DL-abc-GG-WBR','DL-SEL-POD','DL-abc-NorthAmerica-Verticals','DL-abc-IRIS-Tableau-PL','DL-abc-ITSS-DataServices','DL-abc-Smile-club-weekly-report','DL-abc-KO-BA','DL-abc-CBT-CMMnTraining','DL-abc-ITSS-CIODB-Users','ITSSLeaders','DL-abc-GET-EF-DHUB-TECH','DL-abc-UCP-Topseller-CN','DL-abc-UCP-Topseller-HKTW','DL-abc-UCP-Topseller-SEA','DL-abc-DL-abc-UCP-Topseller-HiPo','DL-abc-DL-abc-UCP-Topseller-IN','DL-abc-DL_Top_Seller_Policy_Violations_US_Report','DL-abc-HelpDesk-Reports-Access','DL-abc-Custodian_Superusers','DL-abc-Comp-Viz-Comp-Team','DL-abc-ITSS-Automation','DL-abc-PLN_Dashboard','DL-abc-GCA-Tableau-Users','DL-abc-OCIO-DevOps','DL-abc-ITSS-GNS-Tableau-Access','dl-mgr-acutright-directors-above','DL-abc-GPBR-Analytics','DL-abc-SD-Configuration-Ops','DL-abc-CSTech-EntData-BI','DL-abc-CSTech-EntData-DEV-AWF-OffShore','DL-abc-Product-Analytics-ALL','DL-abc-ADI-BIPL-TEAM','DL-abc-Custodian_LimitedAccess','DL-abc-GCX-Tableau-User','DL-abc-Trust-Neo-Scrum','DL-abc-MSB-Reports-Access','DL-abc-Resolutions-ScrumTeam','DL-abc-IRIS-Tableau-PL']
for dl in DLlist:
        DLUserList=[]
        dlexist=isDLexists(dl)
        if dlexist == 'true':
            print ("DL exists on DL Manager..Checking if the group exists on tableau server")
            tabDLexist=isTableauGroupExists(dl)
            print ("Tableau Group Exists or not"+tabDLexist)
            responsestr=getDL(dl)
            json_data=json.loads(responsestr)
            if tabDLexist == 'true':
                i=0
                while i < len(json_data):
                    DLUserList.append(json_data[i]['samAccountName'])
                    i=i+1
                TabGroupUsers=gettableauGroupMembers(dl)
                AddList=list(set(DLUserList)-set(TabGroupUsers)) #All users in the DL which doesnt exists on Tableau group
                RemoveList=list(set(TabGroupUsers)-set(DLUserList)) #All users in Tableau group which doesnt exists on DL
                j=0
                print("Length of remove List")
                print (len(RemoveList))
                print (RemoveList)
                print ("Length of AddList")
                print (len(AddList))
                print (AddList)
                while j < len(AddList):
                    if  AddList[j].lower().find('dl-',0) != -1:
                        AddList.pop(j)
                        continue #Needed this statement otherwise the index problem occurs
                    j=j+1
                tabGroupItem=getTableauGroupItem(dl)
                if RemoveList:
                    print ("Start removal process on DL"+dl+" ...")
                    count=0
                    for Dname in RemoveList:
                        D_User_Item=getUserItem(Dname)
                        deleteUsersFromGroup(tabGroupItem,D_User_Item)
                        count=count+1
                    print("Removal of users from DL "+dl+" completed Number of users removed : "+str(count))
                if not AddList:
                    print ("emptylist There is no new user to add on DL:"+dl)
                else:
                    print ("Not empty list")
                    print ("Started adding users to existing group: "+dl+" ..." )
                    for addUsername in AddList:
                        try:
                            User_Item=createNewUser(addUsername)
                            #print (User_Item.name)
                            addUserToExistinGroup(tabGroupItem,User_Item)
                        except:
                            continue
                    print ("User creation and addition to existing group "+dl+" completed")
            else:
                print ("DL doesnt exists on tableau server Creating new DL "+dl+"...")
                tabGroupItem=createnewTableauGroup(dl)
                AddNewList=[]
                k=0
                while k < len(json_data):
                    AddNewList.append(json_data[k]['samAccountName'])
                    k=k+1
                l=0
                while l < len(AddNewList):
                    if  AddNewList[l].lower().find('dl-',0) != -1:
                        AddNewList.pop(l)
                        continue #Needed this statement otherwise the index problem occurs
                    l=l+1
                print ("Started adding users to new group: "+dl+" ..." )
                for addUsername in AddNewList:
                    try:
                        User_Item=createNewUser(addUsername)
                        #print (User_Item.name)
                        addUserToExistinGroup(tabGroupItem,User_Item)
                    except:
                        continue
                print ("User creation and addition to new group "+dl+" completed")
        else:
            print (dl+" is invalid DL")
signout()
