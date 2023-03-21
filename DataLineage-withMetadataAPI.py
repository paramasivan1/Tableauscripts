####
# This script demonstrates how to query the Metadata API using the Tableau
# Server Client.
#
# To run the script, you must have installed Python 2.7.9 or later.
####

import getpass
import requests
import os
from datetime import time
import json
import tableauserverclient as TSC


def main():
    #Set the query https://help.tableau.com/current/api/metadata_api/en-us/docs/meta_api_examples.html
    Metadata_File= open("MD_File1_DefaultSite.json","w")
    data={}
    endCursor="null"
    query = """
    query databasetables{
  databaseTablesConnection {
      nodes{
          Table_Name:name
          connectionType
          columns{Column_Name:name}
          downstreamWorkbooks{Workbook_Name:name
          projectName
          owner {Workbook_Owner:username}
          embeddedDatasources {
      Embedded_DataSource_Name: name
    }}
          downstreamDatasources{Downstream_DataSource_Name:name}

          upstreamDatasources{Upstream_DataSource_Name:name}
          }

        pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
}
}
    """
    pxuser = input("ProxyUsername: ")
    pxpass = getpass.getpass("Password (Bin + Yubikey): ")
    env_px = f"http://{pxuser}:{pxpass}@c2sproxy.vip.abc.com:8080/"
    os.environ['http_proxy']=env_px

    username = "tableau_admin"
    password = "abcd"
    servername = "http://tableau.corp.abc.com"
    tableau_auth = TSC.TableauAuth(username, password)
    server = TSC.Server(servername)
    server.version = '3.14'
    with server.auth.sign_in(tableau_auth):
        #Query the Metadata API and store the response in resp
        resp = server.metadata.query(query)
        datasources = resp['data']
    json.dump(datasources['databaseTablesConnection']['nodes'],Metadata_File)
    #print (datasources)

    HasNextPage=datasources['databaseTablesConnection']['pageInfo']['hasNextPage']
    end_cursor=datasources['databaseTablesConnection']['pageInfo']['endCursor']
    print (HasNextPage,end_cursor)
    while HasNextPage:
        print ("Inside While")
        query = '''
            query databasetables{
          databaseTablesConnection(after: "%s"){
              nodes{
                  Table_Name:name
                  connectionType
                  columns{Column_Name:name}
                  downstreamWorkbooks{Workbook_Name:name
                  projectName
                  owner{Workbook_Owner:username}
                  embeddedDatasources {
      Embedded_DataSource_Name: name
    }}
                  downstreamDatasources{Downstream_DataSource_Name:name}
                  upstreamDatasources{Upstream_DataSource_Name:name}
                  }

                pageInfo {
              hasNextPage
              endCursor
            }
            totalCount
        }
        }
            '''%(end_cursor)
        print (query)
        with server.auth.sign_in(tableau_auth):
            resp = server.metadata.query(query)
            datasources = resp['data']
            json.dump(resp['data']['databaseTablesConnection']['nodes'],Metadata_File)
        print (datasources['databaseTablesConnection']['nodes'])
        print(datasources['databaseTablesConnection']['pageInfo']['hasNextPage'])
        HasNextPage=datasources['databaseTablesConnection']['pageInfo']['hasNextPage']
        end_cursor=datasources['databaseTablesConnection']['pageInfo']['endCursor']
        print (HasNextPage,end_cursor)
    Metadata_File.close()
    MDFile=open("MD_File1_DefaultSite.json","r")
    MDFile_Final=open("MD_File_Final_DefaultSite.json","w")
    for line in MDFile:
        MDFile_Final.write(line.replace('][',','))

if __name__ == '__main__':
    main()
