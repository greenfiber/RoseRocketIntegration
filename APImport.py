#!/usr/bin/env python
# coding: utf-8

# In[ ]:
from concurrent.futures import ThreadPoolExecutor
import asyncio
# import xlwings as xw
# import pandas as pd
from integration import RoseRocketIntegration
from backend import RoseRocketIntegrationBackend
import requests
from secretprod import secrets as pw
# import pprint
import records

# In[ ]:



class APImport():
    def __init__(self):
        self.data=[]
        # self.org=org
        self.newbills=[]
        
        self.db=RoseRocketIntegrationBackend()
        # print("AP IMPORT FOR ORG {}".format(org))
        
    def getmanifests(self,headers):
    #     numpages=1
    #     i=0
        # legs=[]
    #     while(i<numpages):
        apiurl="https://platform.sandbox01.roserocket.com/api/v1/manifests?status=bill-created"
        try:
            resp=requests.get(apiurl,headers=headers).json()
        except Exception as e:
            print(e)
        # print(resp)
    #     print(resp)
    #         numpages=resp["total"]
    #     for leg in resp["manifests"]:
    #         print(leg)
    #         legs.append(leg)
        return resp["manifests"]

    def getimportsize(self):
        return len(self.newbills)

    def getcustomerexternalid(self,session,headers,manifestid):
        # print("generating customers for org: {}".format(org))
        # customers=[]
        apiurl="https://platform.sandbox01.roserocket.com/api/v1/manifests/{}/legs".format(manifestid)
        resp=session.get(apiurl,headers=headers).json()
        try:
            orderid=resp["legs"][0]["order_id"]

        except:
            print("error in legs parse")
            print(resp)
        apiurl="https://platform.sandbox01.roserocket.com/api/v1/orders/{}".format(orderid)
        resp=session.get(apiurl,headers=headers).json()
        return resp["order"]["customer"]["external_id"]
        
    def comparedata(self,org,headers):
        #compare both lists and return which data is not in the database
        #for each row of that data not in the DB, use the writeapdata() method to write it
        actualdata=[]
        rrdata=[dat['id'] for dat in self.getmanifests(headers)]
        currentdata=[x.manifestid for x in self.db.getcurrentapdata(org)]
        
        s = set(currentdata)
        actualdata=[x for x in rrdata if x not in s]
        self.newbills=actualdata
        # print(len(actualdata))
        return actualdata


    # In[ ]:
    async def generateimport(self):
        orgs=pw.orgs.keys()
        with ThreadPoolExecutor(max_workers=8) as executor:
            with requests.Session() as session:
                loop=asyncio.get_event_loop()
                tasks=[loop.run_in_executor(executor,self.startimport,org,session) for org in orgs]
                for resp in await asyncio.gather(*tasks):
                    print("AP Import done!")
                    self.data.append(resp)
    def startimport(self,org,session):
        self.data.clear()
        rr = RoseRocketIntegration(org)
        # db = RoseRocketIntegrationBackend()
        auth= rr.authorg(org)
        headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(auth)


            }
        # customers=self.gencustomers(org,session,headers)
        data={
            "whcode":org,
            "SCAC":"",
            "vendorno":"",
            "invoiceno":"",
            
            
            "actualcost":"",
            
            "currency":"",
            "invoicedate":"",
            "duedate":"",
            "manifestid":""
            
            
            }
        pddata=[]
        ids=self.comparedata(org,headers)
        counter=0
        for manifestid in ids:
            # manifestid=manifestid.manifestid
            # print(manifestid)
            if(manifestid!=None):
                
                data["manifestid"]=manifestid
                data["vendorno"]=self.getcustomerexternalid(session,headers,manifestid)
                apiurl="https://platform.sandbox01.roserocket.com/api/v1/bills?in_manifest_ids={}".format(manifestid)
                resp=session.get(apiurl,headers=headers).json()
                if(len(resp["bills"]) ==0):
                    print("manifest invalid for import: {}".format(manifestid))
                    continue
                else:
                    counter+=1
        #             print(resp)
                    billid=resp["bills"][0]["id"]
                    apiurl="https://platform.sandbox01.roserocket.com/api/v1/bills/{}".format(billid)
                    # print(billid)
                    resp=session.get(apiurl,headers=headers).json()
        #             print(resp)
        #             data["actualcost"]=resp["total_amount"]
                    data["invoiceno"]=resp["bill"]["reference_number"]

                    data["invoicedate"]=resp["bill"]["bill_date"]
                    data["duedate"]=resp["bill"]["due_date"]
                    # data["vendorno"]=self.getcustomerexternalid(session,headers,resp["bill"]["bill_to"]["company_name"])
                    extra=0
                    freightcost=0
                    items=resp["items"]
                    for item in items:
                        if(item["bill_item_type"]["name"]!="Partner Freight"):
                            extra+=item["total_amount"]
                        elif(item["bill_item_type"]["name"]=="Partner Freight"):
                            freightcost+=item["total_amount"]
                        else:
                            print("item: {} is weird".format(item["bill_item_type"]["name"]))
                    data["total5000"]=extra
                    data["total6000"]=freightcost
                    customername=resp["bill"]["bill_to"]["company_name"]
        #             print(resp["manifest_full_id"])
                    try:
                        if(resp["partner_carrier"]["standard_carrier_alpha_code"]!="null"):

                            data["SCAC"]=resp["partner_carrier"]["standard_carrier_alpha_code"]
                        else:
                            
                            data["SCAC"]=str(resp["partner_carrier"]["name"])[:10]
                    except:
                        data["SCAC"]="NULL"
        #                 data["carriername"]="CPU"
             
                    
                    # for customer in customers:
                    #     if customer==customername:
                    #         data["vendorno"]=customer["external_id"]
                    #         print(data["vendorno"])
                    # print("end of bill logic")
        #         print(data.copy())
                self.db.writeapdata(data.copy())
                print("Bills processed for whcode {}: {}".format(data["whcode"],counter))
                pddata.append(data.copy())
            else:
                print("Manifest ID None")
        return pddata
    
    
if __name__ == "__main__":
    ap=APImport()
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop=asyncio.get_event_loop()
    future=asyncio.ensure_future(ap.generateimport())
    loop.run_until_complete(future)    
    print("Finished")
    print("Size of import: {}".format(ap.getimportsize()))
    


# In[ ]:




