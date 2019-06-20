
import requests
# import simplejson
import pysftp
import ftputil
import csv
import logging
from datetime import datetime
from time import strftime,strptime
from shutil import copy2,move
from backend import RoseRocketIntegrationBackend 
from secret import secrets as pw



class RoseRocketIntegration():
    db = RoseRocketIntegrationBackend()
    
    apiurl=''
    #warehousecode:warehousename
    orgs={
        '130':'GFNorfolk',
        '161':'GFWaco',
        '310':'GFTampa',
        '336':'GFDelphos',
        '810':'GFChandler',
        '841':'GFSLC',
        '842':'GFSLC',
        '845': 'GFSLC',
        '906': "GFWilkes-Barre",
        '920': 'GFVars',
        '921': 'GFDebert'
    
    }
    
    
    data=db.getAllData()

    def logStart(self):
        logging.basicConfig(filename='C:\\svsync\\sync.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    def authorg(self, whcode):
        authurl='https://auth.sandbox01.roserocket.com/oauth2/token'
        authheader={'Accept': 'application/json'}

        params = {
            "grant_type": "password",
            "username": pw.rruser,
            "password": pw.rrpw,
            "client_id":pw.orgs[whcode]['clientid'],
            "client_secret":pw.orgs[whcode]['secretid']


        }

        r = requests.post(authurl, json=params, headers=authheader)
        resp = r.json()
        # print("Token: {}".format(resp['data']['access_token']))
        pw.orgs[whcode]['accesstoken']=resp['data']['access_token']
        return pw.orgs[whcode]['accesstoken']
    def processComments(self,comments):
        concat=""
        for comment in comments:
            concat += comment +" "
        return concat
    # this method parses the combined pieces from line items for the salesorders
    def processPieces(self, lines, data, desc, products):
        lindesc = desc.split('|')
        items = lines.split('|')
        prods = products.split('|')
        piecesData = []
        for i in range(0, len(prods)-1):
            try:
                # there's something wrong with this depending on data from SQL
                qty = int(float(items[i]))
            except ValueError:
               # print("Quantity was blank")
                logging.warning("Quantity was blank and threw an exception")
            if(data.SHIPWEIGHT):
                try:
                    weight= float(data.SHIPWEIGHT)
                except:
                    logging.error("Weight through an exception")
                    
            else:
                weight=float(0)
            

            if(data.CUSTOMERNO == 'HOMEDCO' or data.CUSTOMERNO == 'HOMERDC'): #this is needed for homedepot orders only
                nmfc = '10330'
                pieceClass = '100'
                pieces = {
                "weight_unit":"lb",
                "freight_class":pieceClass,

                "quantity": qty,
                "weight": weight,
                
                "measurement_unit": "inch",
                "description": lindesc[i],
                "sku": prods[i],
                "nmfc":nmfc,
                "commodity_type":"other"}
            else:
                
                pieces = {
                "weight_unit":"lb",
                "freight_class": 'none' ,

                "quantity": qty,
                "weight": weight,
                
                "measurement_unit": "inch",
                "description": lindesc[i],
                "sku": prods[i],
                "nmfc": 'none',
                "commodity_type":"other"

            
                
            }
            #check if special sku is in products array
            #item code didn't work as that line might have diff sku
            if("INS765LD/E" in prods[i]):
                pieces = {
                "weight_unit":"lb",
                "freight_class":pieceClass,

                "quantity": qty,
                "weight": data.SHIPWEIGHT,
                
                "UnitOfMeasure": "in",
                "description": lindesc[i],
                "sku": prods[i],
                "nmfc":nmfc,
                "commodity_type":"other"
            }
            # don't append items with slashes in pieces
            if("/" not in prods[i]):
                piecesData.append(pieces)
            elif("/NOINV" in prods[i] or "/MISC" in prods[i] or "INS765LD/E" in prods[i]):
                piecesData.append(pieces)
            i += 1
        return piecesData
    
    def formatDate(self, data):
        try:
            fd = datetime.strptime(data,'%Y/%m/%d').isoformat()
            return str(fd)
        except:
        #print("error in formatting date ")
            logging.error("Format date error")


    def sendData(self, data):
        logging.debug("Starting sync...")
        logging.info("=====================================")
        logging.info("NEW SYNC STARTED!")
        logging.info("=====================================")
       
        
        recordcount = 0
        # keeps track of sent SO#s
        ordernos = []
        # keeps track of successful sends to SV
        sentorders = []
        # keeps track of failed orders going to SV
        failedorders = []

        for order in data:
            headers = {
         'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.authorg(order.WAREHOUSECODE))

            
        }
            # sets shipment service type based on order quantity
            if(int(float(str(order.LINEITEMS).split('|')[0])) > 700):
                ServiceTypeCode = "ftl"
            else:
                ServiceTypeCode = "ltl"
            whcode = order.WAREHOUSECODE
            try:
                plantInfo = self.db.getPlantInfo(whcode)[0]
            except Exception as e:
                logging.error("ERROR IN WAREHOUSE LOOKUP")
                print(e)
            #THIS IS USED FOR TESTING ONLY
            #rand = self.genrnd()

            #FOB logic to conform to SV standards
            if(order.FOB=='CC'): fob='collect'
            if(order.FOB=='PP'):fob='prepaid'
            if(order.CUSTOMERNO=='HOMEDCO'):fob='thirdparty'
            

            params = {

                "external_id":order.SALESORDERNO,
                "destination": {
                    "contact_name": order.SHIPTONAME,
                    
            
                    "address_1": order.SHIPTOADDRESS1,
                    "address_2": order.SHIPTOADDRESS2,
                    "city": order.SHIPTOCITY,
                    "state": order.SHIPTOSTATE,
                    "postal": order.SHIPTOZIPCODE,
                    "country": "US",  # REPLACE THIS WITH COLUMN

                    
                    "phone": order.TELEPHONENO
                },  # end of consignee


                "origin": {"contact_name": plantInfo["plantName"],
                    "address_1": plantInfo["Address1"],
                    "address_2": plantInfo["Address2"],
                    "city": plantInfo["City"],
                    "state": plantInfo["State"],
                    "postal": plantInfo["PostalCode"],
                    "country": plantInfo["CountryCode"],
                 "phone": plantInfo["plantPhoneNumber"]

                },  # end of shipper

                # "DatesandTimes": {
                #     "HousebillDate": self.formatDate(order.ORDERDATE),
                #     "ScheduledDeliveryDateType": "on",
                #     "ScheduledDeliveryDate": self.formatDate(order.PROMISEDATE)

                # },

                "dim_type": str(ServiceTypeCode),
                "billing_option":fob,

                "billing": {
                    "address_book_external_id": order.ARDIVISIONNO + order.CUSTOMERNO,
                    "contact_name": order.BILLTONAME,
                    
                        "address_1": order.BILLTOADDRESS1,
                        "address_2": order.BILLTOADDRESS2,
                        "city": order.BILLTOCITY,
                        "state": order.BILLTOSTATE,
                        "postal": order.BILLTOZIPCODE,
                        "country": "US",  # REPLACE THIS WITH COLUMN
                    

                    
                    
                },  # end of billto
                "po_num":order.PURCHASEORDERNO,
                # end of pieces
                "commodities": self.processPieces(order.LINEITEMS, order, order.ITEMDESC, order.ITEMCODES),

                "notes": 
                    # "InternalNotes":self.groupRecords(order.COMMENTS)[0],
                    
                    "OriginInstructions: {}".format(self.processComments(order.COMMENTS.split('|'))),
                    
                

                
                "ref_num": order.SALESORDERNO,
                 "accessorials": []



            }
            recordcount += 1

            # checks if item code is valid for current record
            if("INS" in str(order.ITEMCODE) or "FRM" in str(order.ITEMCODE) or "ABS" in str(order.ITEMCODE)):
                # this enables duplicates to be found
                if(len(ordernos) > 1):
                    # checks if the current SO is not equal to the last order submitted
                    # if they are the same then that means it is a duplicate and shouldn't be sent
                    if(order.SALESORDERNO != ordernos.pop()):
                       
                        #sets apiurl for the correct customer for this order
                        apiurl='https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/orders'.format(order.ARDIVISIONNO,order.CUSTOMERNO)
                        r = requests.post(
                            apiurl, json=params, headers=headers)
                        resp = r.json()

                        if('error_code' in resp):
                            #print("Send was successful! " + str(recordcount))
                            logging.error(
                                "Send was NOT successful for order: " + str(order.SALESORDERNO))
                            logging.error("Error: "+ str(resp))
                            sentorders.append(order.SALESORDERNO)
                        else:
                            #print("SVAPI reports an Error when sending data")
                            # print(resp)
                            # TODO: reason why it fpyailed
                            logging.info(
                                "Success when sending SO#: " + str(order.SALESORDERNO))
                            
                            failedorders.append(order.SALESORDERNO)
                        # this is what keeps track of any extra lines still in db
                        ordernos.append(order.SALESORDERNO)
                    else:
                        #print("Duplicate record removed " +
                            #  str(order.SALESORDERNO))
                        logging.info("Duplicate record removed " +
                                     str(order.SALESORDERNO))

                    # except Exception :
                    # print("Something went wrong with sending data to SV API" )
                # if it's the first record in the data sync then go ahead and send it
                else:
                    # appends sales order to duplicate checking list
                    # this is what keeps track of any extra lines still in db
                    ordernos.append(order.SALESORDERNO)
                   # print("Valid record: " + order.ITEMCODE)


                    #sets apiurl for the correct customer for this order
                    apiurl='https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/orders'.format(order.ARDIVISIONNO,order.CUSTOMERNO)
                    print("APIURL: {}".format(apiurl))
                    print("PARAMS: {}".format(params))
                    r = requests.post(
                        apiurl, json=params, headers=headers)
                    resp = r.json()
                    #sentorders.append(order.SALESORDERNO)
                    if('error_code' in resp):
                        #print("Send was successful! " + str(recordcount))
                        logging.error(
                            "Send was NOT successful for order: " + str(order.SALESORDERNO))
                        logging.error("Error: "+ str(resp))
                        sentorders.append(order.SALESORDERNO)
                    else:
                        #print("SVAPI reports an Error when sending data")
                        # print(resp)
                        # TODO: reason why it fpyailed
                        logging.info(
                            "Success when sending SO#: " + str(order.SALESORDERNO))
                            
                            # failedorders.append(order.SALESORDERNO)

                    failedorders.append(order.SALESORDERNO)
    def synccustomers(self,data):
        apiurl='https://platform.sandbox01.roserocket.com/api/v1/customers'
        
        for order in data:

            #this determins the billing type
            if(order.FOB=='CC'): fob='collect'
            if(order.FOB=='PP'):fob='prepaid'
            if(order.CUSTOMERNO=='HOMEDCO'):fob='thirdparty'
                

            # print("Auth Token: {}".format(self.authorg(order.WAREHOUSECODE)))
            headers = {
         'Accept': 'application/json',
        'Authorization': 'Bearer {}'.format(self.authorg(order.WAREHOUSECODE))

            
            }
            params={
                        "external_id": order.ARDIVISIONNO + order.CUSTOMERNO,
                        "name": order.BILLTONAME,
                        
                            "address_1": order.BILLTOADDRESS1,
                            "address_2": order.BILLTOADDRESS2,
                            "city": order.BILLTOCITY,
                            "state": order.BILLTOSTATE,
                            "postal": order.BILLTOZIPCODE,
                            "country": "US",
                            "short_code":str(order.CUSTOMERNO)[:6],
                            "currency":'usd',
                            "default_billing_option":fob,
                            "default_dim_type":"ltl",
                            "measurement_unit":"inch",
                            "weight_unit":"lb",
                            "is_active":True,
                        "billing_contact_name": order.BILLTONAME}
            # print(params)
          
            r = requests.post(
            apiurl, json=params, headers=headers)
            print("Sync Customer Response: {}".format(r.text))
            resp = r.json()
           
            #sentorders.append(order.SALESORDERNO)
            if('error_code' in resp):
            # if(str(resp['Success']) == str('True')):
                #print("Send was successful! " + str(recordcount))
                logging.error(
                    "Send was unsuccessful for customer: " + str(order.CUSTOMERNO))
               
                
            else:
                #print("SVAPI reports an Error when sending data")
                # TODO: reason why it failed
                print("Send was successful when sending Customer " +
                            str(order.CUSTOMERNO))
                logging.info("Send was successful when sending Customer " +
                            str(order.CUSTOMERNO))
    

if __name__ == "__main__":
    data = RoseRocketIntegrationBackend().getTestData()
    rr = RoseRocketIntegration()
    rr.synccustomers(data)
    rr.sendData(data)