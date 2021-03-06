from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify, make_response
from secret import secrets as pw
import requests
import pyodbc
import simplejson
from integrationutils import RoseRocketIntegrationUtils
import os
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(12)



def logdata(data):
    cx = pyodbc.connect("DSN=gf32;UID={};PWD={}".format(
    pw.dbusr, pw.dbpw))
    query = '''
    INSERT INTO [SVExportStaging].[dbo].[RRToSageImportLogs](orderid, salesorderno, orgid, logtime, jsonerror, freightcharge, scac) values(?,?,?,?,?,?,?)
    '''
    cursor = cx.cursor()
    cursor.execute(query,data['orderid'],data['salesorderno'],data['org'],datetime.datetime.now(),str(data['datajson']),data['freightcharge'], data['SCAC'])
    cursor.commit()
        

def writedata(data):
    cx = pyodbc.connect("DSN=gf32;UID={};PWD={}".format(
    pw.dbusr, pw.dbpw))
    query = ''' 
    
    insert into [InSynch].[dbo].[TOSAGE_SO_SalesOrderHeader](SalesOrderNo,UDF_OFD,UDF_EST_FREIGHT_CHG,ShipVia)values(?,?,?,?)
    '''
    cursor = cx.cursor()
    print(data["freightcharge"])
    print(data["SCAC"])
    cursor.execute(query,data["salesorderno"],"Y",data["freightcharge"],data["SCAC"])
    cursor.commit()
def getfreightinfo(orderid,org):
    rr = RoseRocketIntegrationUtils()
    auth = rr.authorg(org)

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(auth)


    }
    data={"freightcharge":"",
            "SCAC":"",
            "salesorderno":"",
            "orderid":str(orderid),
            "org":"",
            "datajson":""
            
            
    }
    #get the salesorderno
    apiurl = "https://platform.sandbox01.roserocket.com/api/v1/orders/{}".format(orderid)
    try:
        data["salesorderno"] = requests.get(apiurl,headers=headers).json()["order"]["external_id"]
    except:
        print("Error in order lookup from RR: SALESORDERSTAGE")
        return data
    #gets the legs to get the manifestid
    apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/orders/{}/legs'.format(
            orderid)
    resp = requests.get(apiurl, headers=headers).json()
    # print(resp)
    legs = []
    # legs

    for leg in resp["legs"]:

        if(leg["manifest_id"] != None):

            
           
            manifestid = leg["manifest_id"]
            
            # getting manifestid for use to get manifests
            apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/manifests/{}/payment'.format(
                manifestid)
            resp = requests.get(apiurl, headers=headers).json()
            print(resp)
            #get estimated cost
            data["freightcharge"] = resp["manifest_payment"]["sub_total_amount"]
            apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/manifests/{}/'.format(
                    manifestid)
            resp = requests.get(apiurl, headers=headers).json()

            carrierid = resp["manifest"]["partner_carrier_id"]
            # manifest is used to get partner carrier id
            apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/partner_carriers/{}'.format(
                carrierid)
            resp = requests.get(apiurl, headers=headers).json()
            # finally with the partner carrier id you can get the SCAC code
            try:

                data['SCAC'] = resp["partner_carrier"]["name"][:15]
            except:
                data['SCAC'] = "NULL"
            
            return data

@app.route('/', methods=['GET','POST'])
def default():
    token = request.args.get('token')
    if(token == 'CTq74c42cuUMkudJbPVF3GsH'):
        
        # data=str(request.data).encode("utf-8")
        datajson=simplejson.loads(request.data)
        # print(datajson["order_id"])
        orderid=datajson["order_id"]
        print("orderid {}".format(str(orderid)))
        # print(datajson)
        try:
            freightcharge = getfreightinfo(datajson["order_id"],request.args.get('org'))
            freightcharge['org']=request.args.get('org')
            logdata(freightcharge)
            writedata(freightcharge)
            print("freight amount: {}".format(freightcharge))
        except Exception as e:
            print("error in freight charge lookup for order {}".format(datajson))
            freightcharge['datajson']="Error during info lookup"
            logdata(freightcharge)
            print(e)
        return '200'

    else:
        return 'Not okay auth'

if __name__ == '__main__':
    
    app.run(port='6969', host="0.0.0.0")