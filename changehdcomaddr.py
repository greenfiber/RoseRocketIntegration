from integration import RoseRocketIntegration  
from backend import RoseRocketIntegrationBackend
from secret import secrets as pw
import requests
orgs = pw.orgs.keys()
apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/customers/ext:00HOMEDCO'

 
for org in orgs:
    auth = RoseRocketIntegration(org).authorg(org)
    # print("Auth Token: {}".format(auth))
    billingaddress={
                    
                    "name": "HOMEDEPOT.COM",

                    "address_1": "ATTN: FREIGHT PAYABLES",
                    "address_2": "2455 PACES FERRY ROAD",
                    "city": "ATLANTA",
                    "state": "GA",
                    "postal": "30339",
                    "country": "US",  # REPLACE THIS WITH COLUMN




                }
    headers = {
                'Content-Type': 'application/json',
                
                'Authorization': 'Bearer {}'.format(auth)


            }
    params = {
        
        "name": billingaddress['name'],

        "address_1": billingaddress['address_1'],
        "address_2": billingaddress['address_2'],
        "city": billingaddress['city'],
        "state": billingaddress['state'],
        "postal": billingaddress['postal'],
        "country": "US",
        "short_code": str('00HOMEDCO')[:6],
        "currency": 'usd',
                    "default_billing_option": 'thirdparty',
                    "default_dim_type": "ltl",
                    "measurement_unit": "inch",
                    "weight_unit": "lb",
                    "is_active": True,
        }
    r = requests.put(
                apiurl, json=params, headers=headers)
            # logging.info("Sync Customer Response: {}".format(r.text))
    resp = r.json()

    print(resp)