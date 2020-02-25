import pandas as pd
from integration import RoseRocketIntegration
from secretprod import secrets as pw
import asyncio
import glob
from concurrent.futures import ThreadPoolExecutor
import simplejson
import requests
import pyodbc
from secretprod import secrets as secrets
# import xlwings as xw
import pprint
import os
orgs = pw.orgs.keys()
choice = ''
# while(choice != 'YES'):
#     startdate = input("Enter start date (yyyymmdd):")
#     enddate = input("Enter end date (yyyymmdd):")
#     print("START: {} ||| END: {}".format(startdate, enddate))
#     choice = input("Are these dates correct? (YES/NO):")
#     choice = str(choice).upper()
class NickReport():
    
    pddata = []
    missingorders = []
    csvfiles=[]
    masterfile="uninstantiated.file"
    counter = 0
    columns=[
                    "stationcode",
                    "orderno",
                    "manifestid",
                    "housebill",
                    "sageshipdate",
                    "ofddate",
                    "totalcost",
                    "totalpieces",
                    "routingvendor",
                    "shiptoname",
                    "shiptocode",
                    "shiptoaddress1",
                    "shiptoaddress2",
                    "shiptozipcode",
                    "shiptostate"
                ]
    
    # df=df[columns]
    def __init__(self,startdate,enddate):
        self.startdate=startdate
        self.enddate=enddate
    def getOrderHistory(self,whcode,startdate,enddate):
        cx = pyodbc.connect("DSN=gf32;UID={};PWD={}; MARS_Connection=Yes".format(
        secrets.dbusr, secrets.dbpw))



        query = """
         
        SELECT

        [SALESORDERNO]
        ,[ARDIVISIONNO]
        ,[CUSTOMERNO]
        ,[SHIPTONAME]
      ,[SHIPTOADDRESS1]
      ,[SHIPTOADDRESS2]
      ,[SHIPTOCITY]
      ,[SHIPTOSTATE]
      ,[SHIPTOCODE]
      ,[SHIPTOZIPCODE],
      SHIPTOCOUNTRYCODE,
      BILLTONAME,
      SHIPDATE
      
        ,[WAREHOUSECODE]
       from [MAS_GFC].[dbo].[AR_INVOICEHISTORYHEADER]
       where WAREHOUSECODE = ? and SALESORDERNO <> ''
       and convert(varchar(8),SHIPDATE,112) between ? and ?
         
        UNION 
        SELECT

        [SALESORDERNO]
        ,[ARDIVISIONNO]
        ,[CUSTOMERNO]
        ,[SHIPTONAME]
      ,[SHIPTOADDRESS1]
      ,[SHIPTOADDRESS2]
      ,[SHIPTOCITY]
      ,[SHIPTOSTATE]
      ,[SHIPTOCODE]
      ,[SHIPTOZIPCODE],
      SHIPTOCOUNTRYCODE,
      BILLTONAME,
      SHIPDATE
      
        ,[WAREHOUSECODE]
       from [MAS_CDN].[dbo].[AR_INVOICEHISTORYHEADER]
       where WAREHOUSECODE = ? and SALESORDERNO <> ''
       and convert(varchar(8),SHIPDATE,112) between ? and ?
        order by SHIPDATE 
        """
        cursor = cx.cursor()
        cursor.execute(query, whcode,startdate,enddate, whcode,startdate, enddate)
        rows = cursor.fetchall()
        return rows
    def formatdate(self,date):
        year=date[:4]
        month=date[5:7]
        day=date[8:10]
        # print(date)
        # print(month+'/'+day+'/'+year)
        return month+'/'+day+'/'+year
    def getdata(self,org,session):
        print("getting report data")
        
        results = self.getOrderHistory(org, str(self.startdate), str(self.enddate))
        numorders=len(results)
        rr = RoseRocketIntegration(org)
        auth = rr.authorg(org)

        headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer {}'.format(auth)


        }
        apiurl = 'https://platform.roserocket.com/api/v1/bills'
        bills = session.get(apiurl, headers=headers).json()
        
        for result in results:

            apiurl = 'https://platform.roserocket.com/api/v1/customers/ext:{}/orders/ext:{}'.format(
                result.ARDIVISIONNO+result.CUSTOMERNO, result.SALESORDERNO)

            data = {
                "stationcode": '',
                "orderno": '',
                "housebill": '',
                "Status":"OFD",
                "ofddate": '',
                "manifestid": "",
                "blank":"",
                "totalcost": '',
                "totalweight":'',
                "totalpieces": '',
                "miles":"",
                "blank1":"",
                "shiptocode":'',
                "routingvendor": '',
                "blank2":"",
                "blank3":"",
                "blank4":"",
                "blank5":"",
                "blank6":"",
                "shiptoname":'',
                "shiptoaddress1":'',
                "shiptocity":'',
                "shiptostate":'',
                "shiptozipcode":'',
                "shiptocountrycode":'',
                "billtocode":"",
                "billtoname":"",
                "sageshipdate":'',
                "shiptoaddress2":''
            }
            data['shiptoname']=result.SHIPTONAME
            data['shiptocode']=result.SHIPTOCODE
            data['shiptoaddress1']=result.SHIPTOADDRESS1
            data['shiptoaddress2']=result.SHIPTOADDRESS2
            data['shiptocity']=result.SHIPTOCITY
            data['shiptozipcode']=result.SHIPTOZIPCODE
            data['shiptostate']=result.SHIPTOSTATE
            data['billtocode']=result.CUSTOMERNO
            data['billtoname']=result.BILLTONAME
            data['sageshipdate']=result.SHIPDATE
            data['shiptocountrycode']=result.SHIPTOCOUNTRYCODE
            so = result.SALESORDERNO

            # this gets the order id
            try:
                resp = session.get(apiurl, headers=headers).json()
                # print(resp)
            except Exception as e:
                print("can't find order: {}".format(so))
                print(e)
                # continue
            # print(resp)
            if("error_code" not in resp):
                orderids = []
                data['stationcode'] = org
                data['housebill'] = so

                try:
                    id = resp["order"]['id']

                except:
                    print("\n \n")
                    print(resp)
                    print("\n \n")
                data['orderno'] = id
            else:
                self.missingorders.append(so)
                print(resp)
                print(so)
                print(org)
                continue

            apiurl = 'https://platform.roserocket.com/api/v1/orders/{}/legs'.format(
                id)
            resp = session.get(apiurl, headers=headers).json()
            # print(resp)
            legcount = len(resp['legs'])
            multistoporders = []
            # legs
            
            for leg in resp["legs"]:

                if(leg["manifest_id"] != None and leg["history"]["origin_pickedup_at"] != None):
                    totalweight = 0
                    totalpieces = 0
                    data['ofddate'] = self.formatdate(leg["history"]["origin_pickedup_at"])
                    # print(leg)
                    manifestid = leg["manifest_id"]
                    data["manifestid"]=manifestid
                    # commodities in each leg
                    for comm in leg["commodities"]:
                        # print(comm["weight"])
                        # print(comm["pieces"])
                        # print(comm["quantity"])

                        if(comm["quantity"] == 1):
                            try:
                                totalpieces += comm["pieces"]
                            except:
                                totalpieces=""
                            data['totalpieces'] = totalpieces
                            totalweight = comm["weight"]
                            data['totalweight'] = totalweight

                        elif(comm["pieces"] == 1):
                            try:
                                totalpieces += comm["quantity"]
                            except:
                                totalpieces=""
                            data['totalpieces'] = totalpieces
                            totalweight = comm["weight"]*totalpieces
                            data['totalweight'] = totalweight
                        elif(comm["quantity"] >= 1):
                            try:
                                totalpieces += comm["pieces"]
                            except:
                                totalpieces = ""
                            data['totalpieces'] = totalpieces
                            totalweight = comm["weight"]*comm["quantity"]
                            data['totalweight'] = totalweight

                        # getting manifestid for use to get manifests
                    apiurl = 'https://platform.roserocket.com/api/v1/manifests/{}/payment'.format(
                        manifestid)
                    resp = session.get(apiurl, headers=headers).json()
                    # get estimated cost
                    # if(legcount > 1):
                    #     if(id == leg['order_id']):
                    #         print("Duplicate order {} on manifest {} cost removed!".format(id,manifestid))
                    #         data['totalcost'] =  resp["manifest_payment"]["sub_total_amount"]
                    #     else:
                    #         data['totalcost'] = ''
                    # else:

                    data['totalcost'] = resp["manifest_payment"]["sub_total_amount"]
                    # get partner carrierid
                    apiurl = 'https://platform.roserocket.com/api/v1/manifests/{}/'.format(
                        manifestid)
                    resp = session.get(apiurl, headers=headers).json()

                    carrierid = resp["manifest"]["partner_carrier_id"]
                    # manifest is used to get partner carrier id
                    apiurl = 'https://platform.roserocket.com/api/v1/partner_carriers/{}'.format(
                        carrierid)
                    resp = session.get(apiurl, headers=headers).json()
                    # finally with the partner carrier id you can get the parner carrier name
                    try:

                        data['routingvendor'] = resp["partner_carrier"]["name"]
                    except:
                        data['routingvendor'] = "NULL"

                    self.counter += 1
                    print(data)
                    self.pddata.append(data)
                    # print(self.pddata[0])
                    print("orders processed {}".format(self.counter))
                else:
                    pass
           
        # path = r"C:\Public\Documents\shipmentreport.xlsx"
        # series=pd.Series()
        newdf=pd.DataFrame(self.pddata)
        print(newdf.head())
        filename='shippingreport{}_{}_{}.xlsx'.format(self.startdate,self.enddate,org)
        path=str(os.getcwd()+r"/public/"+filename)
        # print(path)
        newdf.to_excel(path,index=False)
        return filename
        # wb = xw.Book(path)
        # sheet = wb.sheets['Sheet1']
        # sheet.range('A1').value = df
        
    async def generatereport(self):
        print("Generate report async")
        csvfiles=[]
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            with requests.Session() as session:
                loop=asyncio.get_event_loop()
                tasks=[loop.run_in_executor(executor,self.getdata,org,session)
                for org in orgs
                ]
                for resp in await asyncio.gather(*tasks):
                    print(len(self.csvfiles))
                    self.csvfiles.append(resp)
                path=str(os.getcwd()+r"/public/")
                try:
                    df=pd.concat((pd.read_excel(path+f) for f in self.csvfiles),ignore_index=True)
                except ValueError:
                    self.csvfiles.clear()
                    self.pddata.clear()
                    raise ValueError(" Issue with excel file concatenation.")
                filename='shippingreport{}_{}.xlsx'.format(self.startdate,self.enddate)
                df.sort_values("stationcode",inplace=True)

                df.drop_duplicates(subset="housebill").to_excel(str(os.getcwd()+r"/public/"+filename),index=False)
                self.csvfiles.clear()
                self.pddata.clear()
                self.masterfile=filename
                
    def main(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop=asyncio.get_event_loop()
        future=asyncio.ensure_future(self.generatereport())
        loop.run_until_complete(future)
        # self.csvfiles=[]
        return self.masterfile



# print("MISSING ORDERS ON RR {}".format(len(missingorders)))
