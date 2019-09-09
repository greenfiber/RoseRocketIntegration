from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify
from flask_api import status
import requests
from integration import RoseRocketIntegrationUtils
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)

def getfreightamt(orderid):
    rr = RoseRocketIntegrationUtils()
    auth = rr.authorg(org)

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(auth)


    }
    apiurl = 'https://sandbox01.platform.roserocket.com/api/v1/orders/{}/legs'.format(
            id)
    resp = requests.get(apiurl, headers=headers).json()
    # print(resp)
    legs = []
    # legs

    for leg in resp["legs"]:

        if(leg["manifest_id"] != None and leg["history"]["origin_pickedup_at"] != None):
            
           
            manifestid = leg["manifest_id"]
            
            # getting manifestid for use to get manifests
            apiurl = 'https://sandbox01.platform.roserocket.com/api/v1/manifests/{}/payment'.format(
                manifestid)
            resp = requests.get(apiurl, headers=headers).json()
            #get estimated cost
            return resp["manifest_payment"]["sub_total_amount"]

@app.route('/', methods=['GET','POST'])
def default():
    token = request.args.get('token')
    if(token == 'CTq74c42cuUMkudJbPVF3GsH'):
        print(request.data)
        try:
            freightcharge = getfreightamt(request.args.get('org'))
        except:
            freightcharge = "error in freight charge lookup for order {}".format(request.data['order_id'])
        # if(request.method == 'GET'):
        #     print(request.data)
        #     return status.HTTP_200_OK
        # else:
        #     print(request.data)
        return str(str(freightcharge))

    else:
        return 'Not okay auth'

if __name__ == '__main__':
    
    app.run(port='6969', host="0.0.0.0")