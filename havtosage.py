from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify, make_response
from secretprod import secrets as pw
import requests
import pyodbc
import simplejson
import os
import datetime
from pprint import pprint
app = Flask(__name__)
app.secret_key = os.urandom(12)



def logdata(freightcharge,salesorderno,carrier,org,e=None):
    cx = pyodbc.connect("DSN=gf64;UID={};PWD={}".format(
    pw.dbusr, pw.dbpw))
    query = '''
    INSERT INTO [SVExportStaging].[dbo].[HavToSageImportLogs](orderid, salesorderno, orgid, logtime, jsonerror, freightcharge, scac) values(?,?,?,?,?,?,?)
    '''
    cursor = cx.cursor()
    cursor.execute(query,"N/A",salesorderno,org,str(datetime.datetime.now()),str(e),freightcharge, carrier[:9])
    cursor.commit()
        

def writedata(freightcharge,salesorderno,carrier):
    cx = pyodbc.connect("DSN=gf64;UID={};PWD={}".format(
    pw.dbusr, pw.dbpw))
    query = ''' 
    
    insert into [InSynch].[dbo].[TOSAGE_SO_SalesOrderHeader](SalesOrderNo,UDF_OFD,UDF_EST_FREIGHT_CHG,ShipVia)values(?,?,?,?)
    '''
    cursor = cx.cursor()
  
    cursor.execute(query,salesorderno,"Y",freightcharge,carrier[:9])
    cursor.commit()

@app.route('/', methods=['POST'])
def default():
    token = request.args.get('token')
    dev = request.args.get('dev')
    print(dev)
    if(token == 'CTq74c42cuUMkudJbPVF3GsH' and dev =='True'):
        orgs={
            "35":"CDN",
            "22":"Norfolk",
            "24":"Mesa",
            "19":"Corporate",
            "20":"Wilkes-Barre",
            "21":"Tampa",
            "25":"SLC",
            "23":"Waco",
            "131":"Machine Repair"
        }




        # data=str(request.data).encode("utf-8")
        datajson=simplejson.loads(request.data)
        pprint(datajson)
        # print(datajson["order_id"])
        salesorderno=datajson["primary_reference"]["value"]
        print("so {}".format(salesorderno))
        carrier=datajson["carrier"]
        org=orgs[datajson["site"]]
        freightcharge = datajson["amount"]
        # print("orderid {}".format(str(orderid)))
        # print(datajson)
        print("freight amount: {}".format(freightcharge))
        print(len(salesorderno))
        if(len(salesorderno) ==7 and len(freightcharge)>0):
            try:
                
                # logdata(freightcharge,salesorderno,carrier)
                writedata(freightcharge,salesorderno,carrier)
                logdata(freightcharge,salesorderno,carrier,org,"Successful Send")
                print("freight amount: {}".format(freightcharge))
            except Exception as e:
                print("error in freight charge lookup for order {}".format(datajson))
                # freightcharge['datajson']="Error during info lookup"
                logdata(freightcharge,salesorderno,carrier,org,e)
                print(e)
                return '500'
            return '200'
        else:
            print("sales order format or freight charge missing. Did not log to Sage")
            logdata(freightcharge,salesorderno,"n/a",org,"ERROR*** Freight Charge: {} SO: {} Did not log".format(freightcharge,salesorderno))
            return 'bad data'
    else:
        return 'Unauthorized access. Go away.'

if __name__ == '__main__':
    
    app.run(port='6969', host="0.0.0.0")