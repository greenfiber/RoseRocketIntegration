import pandas as pd
from integration import RoseRocketIntegration, RoseRocketIntegrationBackend
from secretprod import secrets as pw
import requests
import xlwings as xw
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
    db = RoseRocketIntegrationBackend()
    pddata = []
    missingorders = []
    
    counter = 0
    def __init__(self,startdate,enddate):
        self.startdate=startdate
        self.enddate=enddate
    def generatereport(self):
        print("generating report...")
        for org in orgs:
            results = self.db.getOrderHistory(org, str(self.startdate), str(self.enddate))
            numorders=len(results)
            rr = RoseRocketIntegration(org)
            auth = rr.authorg(org)

            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(auth)


            }
            apiurl = 'https://platform.roserocket.com/api/v1/bills'
            bills = requests.get(apiurl, headers=headers).json()

            for result in results:

                apiurl = 'https://platform.roserocket.com/api/v1/customers/ext:{}/orders/ext:{}'.format(
                    result.ARDIVISIONNO+result.CUSTOMERNO, result.SALESORDERNO)

                data = {
                    "stationcode": '', "orderno": '',"manifestid":"", "housebill": '', "ofddate": '', "totalcost": '', "totalpieces": '', "routingvendor": ''

                }
                so = result.SALESORDERNO

                # this gets the order id
                try:
                    resp = requests.get(apiurl, headers=headers).json()
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
                resp = requests.get(apiurl, headers=headers).json()
                # print(resp)
                legcount = len(resp['legs'])
                multistoporders = []
                # legs
                
                for leg in resp["legs"]:

                    if(leg["manifest_id"] != None and leg["history"]["origin_pickedup_at"] != None):
                        totalweight = 0
                        totalpieces = 0
                        data['ofddate'] = leg["history"]["origin_pickedup_at"]
                        # print(leg)
                        manifestid = leg["manifest_id"]
                        data["manifestid"]=manifestid
                        # commodities in each leg
                        for comm in leg["commodities"]:
                            # print(comm["weight"])
                            # print(comm["pieces"])
                            # print(comm["quantity"])

                            if(comm["quantity"] == 1):
                                totalpieces += comm["pieces"]
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
                        resp = requests.get(apiurl, headers=headers).json()
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
                        resp = requests.get(apiurl, headers=headers).json()

                        carrierid = resp["manifest"]["partner_carrier_id"]
                        # manifest is used to get partner carrier id
                        apiurl = 'https://platform.roserocket.com/api/v1/partner_carriers/{}'.format(
                            carrierid)
                        resp = requests.get(apiurl, headers=headers).json()
                        # finally with the partner carrier id you can get the parner carrier name
                        try:

                            data['routingvendor'] = resp["partner_carrier"]["name"]
                        except:
                            data['routingvendor'] = "NULL"

                        self.counter += 1
                        self.pddata.append(data)
                        print("orders processed {}".format(self.counter))
                    else:
                        pass
        #                 print(
        #                     "order not added to report because it hasn't shipped yet {}".format(so))
        df=pd.DataFrame(self.pddata)
        # path = r"C:\Public\Documents\shipmentreport.xlsx"
        path=str('shippingreport{}_{}.xlsx'.format(self.startdate,self.enddate))
        print(path)
        df.to_excel(path)
        return path
        # wb = xw.Book(path)
        # sheet = wb.sheets['Sheet1']
        # sheet.range('A1').value = df
        

    



# print("MISSING ORDERS ON RR {}".format(len(missingorders)))
