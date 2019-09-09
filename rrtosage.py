from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify, make_response
from flask_api import status
import requests
import simplejson
from integrationutils import RoseRocketIntegrationUtils
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)

def getfreightamt(orderid,org):
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
        
        data=str(request.data).encode("utf-8")
        datajson=simplejson.dumps(data)
        print(datajson)
        # try:
        #     freightcharge = getfreightamt(orderid,request.args.get('org'))
        # except:
        #     freightcharge = "error in freight charge lookup for order {}".format(datajson)
        
        return '200'

    else:
        return 'Not okay auth'

if __name__ == '__main__':
    
    app.run(port='6969', host="0.0.0.0")