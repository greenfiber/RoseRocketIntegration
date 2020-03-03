#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import xlwings as xw
import pandas as pd
from integration import RoseRocketIntegration
from backend import RoseRocketIntegrationBackend
import requests
from secretprod import secrets as pw
import pprint
import records
db = records.Database("sqlite:///test.db")
# In[ ]:


org='161'
rr = RoseRocketIntegration(org)
# db = RoseRocketIntegrationBackend()
auth= rr.authorg(org)
headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(auth)


    }


# In[ ]:





# In[ ]:


def getmanifests():
#     numpages=1
#     i=0
    # legs=[]
#     while(i<numpages):
    apiurl="https://platform.roserocket.com/api/v1/manifests?status=bill-created"
    resp=requests.get(apiurl,headers=headers).json()
    
#     print(resp)
#         numpages=resp["total"]
#     for leg in resp["manifests"]:
#         print(leg)
#         legs.append(leg)
    return resp["manifests"]


# In[ ]:


def writedata(data):
    
    
    db = records.Database("sqlite:///test.db")
    try:
        db.query("create table apimport(importkey varchar(50),whcode int, SCAC varchar(10), invoiceno varchar(15),  total5000 varchar(15),total6000 varchar(15), invoicedate date, duedate date, manifestid text)")
    except Exception as e:
        pass
        # print(e)
        # print("db already created?")
        
    query="""
    insert into apimport
        values(:importkey,:whcode,:SCAC, :invoiceno, :total5000, :total6000, :invoicedate, :duedate, :manifestid)
    """
    db.query(query,importkey=str(data["invoiceno"])+str(data["manifestid"])[:8],whcode=data["whcode"],SCAC=data["SCAC"],invoiceno=data['invoiceno'],total5000=data["total5000"],total6000=data["total6000"],invoicedate=data["invoicedate"],duedate=data["duedate"],manifestid=data["manifestid"])
    
    print("data logged! {}".format(data["invoiceno"]))
    
def getcurrentdata():

    db = records.Database("sqlite:///test.db")
    query="select manifestid from apimport"
    return db.query(query).all()
# In[ ]:


def comparedata():
    #compare both lists and return which data is not in the database
    #for each row of that data not in the DB, use the writedata() method to write it
    actualdata=[]
    rrdata=[dat['id'] for dat in getmanifests()]
    currentdata=[x.manifestid for x in getcurrentdata()]
    
    s = set(currentdata)
    actualdata=[x for x in rrdata if x not in s]
    print(len(actualdata))
    return actualdata


# In[ ]:


data={
    "whcode":org,
    "SCAC":"",
    "invoiceno":"",
    
    
    "actualcost":"",
    
    "currency":"",
    "invoicedate":"",
    "duedate":"",
    "manifestid":""
    
    
    }
pddata=[]
ids=comparedata()
for manifestid in ids:
    # manifestid=manifestid.manifestid
    print(manifestid)
    if(manifestid!=None):
        data["manifestid"]=manifestid
#        
        apiurl="https://platform.roserocket.com/api/v1/bills?in_manifest_ids={}".format(manifestid)
        resp=requests.get(apiurl,headers=headers).json()
        if(len(resp["bills"])==0):
            continue
        else:
#             print(resp)
            billid=resp["bills"][0]["id"]
            apiurl="https://platform.roserocket.com/api/v1/bills/{}".format(billid)
            print(billid)
            resp=requests.get(apiurl,headers=headers).json()
#             print(resp)
#             data["actualcost"]=resp["total_amount"]
            data["invoiceno"]=resp["bill"]["reference_number"]

            data["invoicedate"]=resp["bill"]["bill_date"]
            data["duedate"]=resp["bill"]["due_date"]
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
#             print(resp["manifest_full_id"])
            try:
                if(resp["partner_carrier"]["standard_carrier_alpha_code"]!="null"):

                    data["SCAC"]=resp["partner_carrier"]["standard_carrier_alpha_code"]
                else:
                    
                    data["SCAC"]=str(resp["partner_carrier"]["name"])[:10]
            except:
                data["SCAC"]="NULL"
#                 data["carriername"]="CPU"
            print("end of bill logic")
#         print(data.copy())
        writedata(data.copy())
        pddata.append(data.copy())
    
print(pddata)
    
    
        


# In[ ]:




