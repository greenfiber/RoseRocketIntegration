from integration import RoseRocketIntegration, RoseRocketIntegrationBackend
from secretprod import secrets as pw
import requests
import xlwings as xw

orgs = pw.orgs.keys()


db = RoseRocketIntegrationBackend()
pddata = []
print("generating report...")
counter=0
for org in orgs:
    results = db.getOrderHistory(org)
    rr = RoseRocketIntegration(org)
    auth = rr.authorg(org)

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(auth)


    }

    
    
    for result in results:
        
       
        apiurl = 'https://platform.roserocket.com/api/v1/customers/ext:{}/orders/ext:{}'.format(
            result.ARDIVISIONNO+result.CUSTOMERNO, result.SALESORDERNO)

        data = {
            "stationcode": '', "orderno": '', "housebill": '', "ofddate": '', "totalcost": '', "totalpieces": '', "routingvendor": ''

        }
        so = result.SALESORDERNO

        # this gets the order id
        try:
            resp = requests.get(apiurl, headers=headers).json()
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
            continue

        apiurl = 'https://platform.roserocket.com/api/v1/orders/{}/legs'.format(
            id)
        resp = requests.get(apiurl, headers=headers).json()
        legs = []
        # legs
        
        
        for leg in resp["legs"]:
            
            if(leg["manifest_id"] != None):
                totalweight = 0
                totalpieces = 0
                data['ofddate'] = leg["history"]["destination_delivered_at"]
                # print(leg)
                manifestid = leg["manifest_id"]
                # commodities in each leg
                for comm in leg["commodities"]:
                    # print(comm["weight"])
                    # print(comm["pieces"])
                    # print(comm["quantity"])
                    totalweight += comm["weight"]
                    data['totalweight'] = totalweight
                    if(comm["pieces"] == None or comm["pieces"]>=1):
                        totalpieces += comm["quantity"]
                        data['totalpieces'] = totalpieces
                    else:
                        totalpieces += comm["pieces"]
                        data['totalpieces'] = totalpieces

                    # getting manifestid for use to get manifests
                    apiurl = 'https://platform.roserocket.com/api/v1/manifests/{}'.format(
                        manifestid)
                    resp = requests.get(apiurl, headers=headers).json()
                    # print(resp)
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
                counter += 1
                pddata.append(data)
                print("orders processed {}".format(counter))
            else:
                pass
#                 print(
#                     "order not added to report because it hasn't shipped yet {}".format(so))
    
# print(pddata)
