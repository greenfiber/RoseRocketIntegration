
import requests
# import simplejson

import csv
import logging
from datetime import datetime
from time import strftime, strptime

from backend import RoseRocketIntegrationBackend
from secret import secrets as pw


class RoseRocketIntegration():
    db = RoseRocketIntegrationBackend()
    LTLFLAG = False

    def __init__(self, whcode):
        self.whcode = whcode

    apiurl = ''
    
    def synccarriers(self,data):
        import pandas as pd
        df=pd.read_excel(io="C:\\Users\\friesdj\\Downloads\\Carrier Report.xlsx")
        sheet=df.where((pd.notnull(df)),'none')
        for index,row in sheet.iterrows():
            params={
            "external_id": row.Code,
            "short_code": row.Code[:6],
            "name": row.Name,
            "address_1": row.Address1,
            "address_2": row.Address2,
            "is_active":True,
            "city": row.City,
            "postal": str(row.Zip),
            "phone": row.Phone,
            
            
            }
            auth = self.authorg(self.whcode)
        
            headers = {
                'Accept': 'application/json',
                


            }
            apiurl = 'https://platform.roserocket.com/v1/partner_carriers'
            r = requests.post(
                apiurl, json=params, headers=headers)
            resp = r.json()
        

    def logStart(self):
        logging.basicConfig(filename='C:\\rrsync\\sync.log', level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')

    def authorg(self, whcode):
        authurl = 'https://auth.sandbox01.roserocket.com/oauth2/token'
        authheader = {'Accept': 'application/json'}

        params = {
            "grant_type": "password",
            "username": pw.rruser,
            "password": pw.rrpw,
            "client_id": pw.orgs[whcode]['clientid'],
            "client_secret": pw.orgs[whcode]['secretid']


        }

        r = requests.post(authurl, json=params, headers=authheader)
        resp = r.json()
        logging.info("AUTHRESP: {}".format(resp))
        print("AUTHRESP: {}".format(resp))
        # print("Token: {}".format(resp['data']['access_token']))
        pw.orgs[whcode]['accesstoken'] = resp['data']['access_token']
        return pw.orgs[whcode]['accesstoken']

    def processComments(self, comments):
        concat = ""
        for comment in comments:
            concat += comment
        return concat
    # this method parses the combined pieces from  lineitems for the salesorders

    def processPieces(self, lines, data, desc, products, unitprice, palletqty, LTLFLAG):
        itemdesc = desc.split('|')
        lineitems = lines.split('|')
        itemcodes = products.split('|')
        pallets = palletqty.split('|')
        skuinfo = {
            "INS541LD": {"THDSKU": "211904", "UPC": "716891001087"},
            "INS765LD/E": {'THDSKU': "1002476568", "UPC": "729477076546"}


        }
        piecesData = []
        for i in range(0, len(itemcodes)-1):
            try:
                # there's something wrong with this depending on data from SQL
                qty = int(float(lineitems[i]))
            except ValueError:
               # print("Quantity was blank")
                logging.warning("Quantity was blank and threw an exception")
            if(data.SHIPWEIGHT):
                try:
                    weight = float(data.SHIPWEIGHT)
                except:
                    logging.error("Weight through an exception")

            else:
                weight = float(0)

            # class and nmfc are none if not HD
            nmfc = 'none'
            pieceClass = 'none'
            #checks if the shipments is a FTL
            #FTL must always have a quantity of one
            # print('LTLFLAG: {}'.format(LTLFLAG))
            if(LTLFLAG == False):
                totalweight = weight*qty
                pieces = {
                "weight_unit": "lb",
                "freight_class": pieceClass,

                "pieces": qty,
                "quantity": 1,
                "weight": float(totalweight),

                "measurement_unit": "inch",
                "description": itemdesc[i],
                "sku": itemcodes[i],
                "nmfc": nmfc,
                "commodity_type": "skid"}
            #this distinction in the pieces dictionary is
            #so the shipments show correct total weights for LTL
            #it uses number of bags and each bag weight 
            #it must always have a piece count of one to make it 'per bag'
            else:
                pieces = {
                    "weight_unit": "lb",
                    "freight_class": pieceClass,

                    "pieces": 1,
                    "quantity": qty,
                    "weight": weight,

                    "measurement_unit": "inch",
                    "description": itemdesc[i],
                    "sku": itemcodes[i],
                    "nmfc": nmfc,
                    "commodity_type": "package"}
            if(data.CUSTOMERNO == 'HOMEDEP' or data.CUSTOMERNO == 'HOMERDC'):
                # print("hd logic")
                nmfc = '10330'
                pieceClass = '100'
                # print("ITEM CODE: {}".format(itemcodes[i]))
                if("INS765LD/E" in itemcodes[i] or "INS541LD" in itemcodes[i]):
                    # print("hd sku logic both skus")
                    print("Pallet Count: {}".format(pallets[i]))
                    if(int(pallets[i]) > 0):
                        palletweight = (qty * weight)/int(pallets[i])
                    else:
                        logging.error("Sales order {} was not sent  because pallet info was not entered. Approximating weight".format(
                            data.SALESORDERNO))
                        palletweight = (qty*weight)/int(qty/42)
                        # raise Exception(
                        #     'pallet quantity should be greater than zero and shouldn\'t get to this point. ')

                    pieces = {
                        "weight_unit": "lb",
                        "freight_class": pieceClass,
                        "pieces": qty,
                        "quantity": int(pallets[i]),
                        "weight": palletweight,

                        "measurement_unit": "inch",
                        "description": """{} THDSKU:{} UPC:{} UNITPRICE: {}""".format(itemdesc[i], skuinfo[itemcodes[i]]["THDSKU"], skuinfo[itemcodes[i]]["UPC"], unitprice),
                        "sku": itemcodes[i],
                        "nmfc": nmfc,
                        "commodity_type": "skid"
                    }
                    # print(pieces)
                    piecesData.append(pieces)
                elif("/" not in itemcodes[i]):
                    # print("hd sku alt logic")
                    # print(pieces)
                    piecesData.append(pieces)
            elif(data.CUSTOMERNO == 'HOMEDCO'):
                nmfc = '10330'
                pieceClass = '100'
                if(LTLFLAG == False):
                    totalweight = weight*qty
                    pieces = {
                    "weight_unit": "lb",
                    "freight_class": pieceClass,

                    "pieces": qty,
                    "quantity": 1,
                    "weight": float(totalweight),

                    "measurement_unit": "inch",
                    "description": itemdesc[i],
                    "sku": itemcodes[i],
                    "nmfc": nmfc,
                    "commodity_type": "skid"}

            #this distinction in the pieces dictionary is
            #so the shipments show correct total weights for LTL
            #it uses number of bags and each bag weight 
            #it must always have a piece count of one to make it 'per bag'
                else:
                    pieces = {
                        "weight_unit": "lb",
                        "freight_class": pieceClass,

                        "pieces": 1,
                        "quantity": qty,
                        "weight": weight,

                        "measurement_unit": "inch",
                        "description": itemdesc[i],
                        "sku": itemcodes[i],
                        "nmfc": nmfc,
                        "commodity_type": "package"}
                if("/" not in itemcodes[i]):
                    piecesData.append(pieces)
            # ******
            # specifically check for only HD skus instead of relying on slash to determine if appended
            # **********
            # don't append lineitems with slashes in pieces

            # check if special sku is in products array
            # item code didn't work as that line might have diff sku

            else:  # any other customer besides HD

                if("/" not in itemcodes[i]):
                    # print("Slash logic non HD")
                    piecesData.append(pieces)

            # if("/NOINV" in itemcodes[i] or "/MISC" in itemcodes[i] or "INS765LD/E" in itemcodes[i]):
            #     print("Weird Logic at bottom")
            #     piecesData.append(pieces)
            i += 1
        # print("PIECES: {}".format(piecesData))
        return piecesData

    def formatDate(self, data):
        import pytz
        try:
            fd = datetime.strptime(data, '%Y%m%d')
            local = pytz.timezone("America/New_York")
            localized = local.localize(fd, is_dst=None)
            utc = localized.astimezone(pytz.utc)
            return str(utc.isoformat())
        except Exception as e:
            #print("error in formatting date ")
            logging.error("Format date error {}".format(e))

    def genrnd(self):
        import string
        import random
        return random.choice(string.ascii_letters)

    def sendData(self, data):
        logging.debug("Starting sync...")
        logging.info("=====================================")
        logging.info("NEW SYNC STARTED!")
        logging.info("=====================================")

        recordcount = 0
        # keeps track of sent SO#s
        ordernos = []
        # keeps track of successful sends to RR
        sentorders = []
        # keeps track of failed orders going to RR
        failedorders = []

        auth = self.authorg(self.whcode)
        for order in data:
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(auth)


            }
            # sets shipment service type based on order quantity
            if(int(float(str(order.LINEITEMS).split('|')[0])) > 700):
                ServiceTypeCode = "ftl"
            else:
                ServiceTypeCode = "ltl"
            # if the order has pallets, send it as ltl so it displays properly in rr covers all HD SQUs
            if(order.CUSTOMERNO == 'HOMEDCO' or order.CUSTOMERNO == 'HOMERDC' or order.CUSTOMERNO == 'HOMEDEP'):
                ServiceTypeCode = 'ltl'
            whcode = order.WAREHOUSECODE
            try:
                plantInfo = self.db.getPlantInfo(whcode)[0]
            except Exception as e:
                logging.error("ERROR IN WAREHOUSE LOOKUP")
                print(e)
            # THIS IS USED FOR TESTING ONLY
            rand = self.genrnd()

            # FOB logic to conform to SV standards
            fob = ''
            if(order.FOB == 'CC'):
                fob = 'collect'
            if(order.FOB == 'PP'):
                fob = 'prepaid'
            if(order.CUSTOMERNO == 'HOMEDCO'):
                fob = 'thirdparty'
                billingaddress={
                    
                    "org_name": "HOMEDEPOT.COM",

                    "address_1": "ATTN: FREIGHT PAYABLES",
                    "address_2": "2455 PACES FERRY ROAD",
                    "city": "ATLANTA",
                    "state": "GA",
                    "postal": "30339",
                    "country": "US",  # REPLACE THIS WITH COLUMN




                }
            else:
                billingaddress={
                    "address_book_external_id": order.ARDIVISIONNO + order.CUSTOMERNO,
                    "org_name": order.BILLTONAME,

                    "address_1": order.BILLTOADDRESS1,
                    "address_2": order.BILLTOADDRESS2,
                    "city": order.BILLTOCITY,
                    "state": order.BILLTOSTATE,
                    "postal": order.BILLTOZIPCODE,
                    "country": "US",  # REPLACE THIS WITH COLUMN




                }


            if(ServiceTypeCode == 'ltl'):
                self.LTLFLAG = True
            else:
                self.LTLFLAG = False
            commodities = self.processPieces(
                order.LINEITEMS, order, order.ITEMDESC, order.ITEMCODES, order.UNITPRICE, order.PALLETQTY, self.LTLFLAG)
            notes = order.COMMENTS.split('|')
            params = {

                "external_id": order.SALESORDERNO+rand,
                "destination": {
                    "org_name": order.SHIPTONAME,


                    "address_1": order.SHIPTOADDRESS1,
                    "address_2": order.SHIPTOADDRESS2,
                    "city": order.SHIPTOCITY,
                    "state": order.SHIPTOSTATE,
                    "postal": order.SHIPTOZIPCODE,
                    "country": "US",  # REPLACE THIS WITH COLUMN


                    "phone": order.TELEPHONENO
                },  # end of consignee


                "origin": {"org_name": plantInfo["plantName"],
                           "address_1": plantInfo["Address1"],
                           "address_2": plantInfo["Address2"],
                           "city": plantInfo["City"],
                           "state": plantInfo["State"],
                           "postal": plantInfo["PostalCode"],
                           "country": plantInfo["CountryCode"],
                           "phone": plantInfo["plantPhoneNumber"],
                           "latitude": float(plantInfo["LAT"]),
                           "longitude": float(plantInfo["LONG"])

                           },  # end of shipper

                # "DatesandTimes": {
                #     "HousebillDate": self.formatDate(order.ORDERDATE),
                #     "ScheduledDeliveryDateType": "on",
                #     "ScheduledDeliveryDate": self.formatDate(order.PROMISEDATE)

                # },

                "dim_type": str(ServiceTypeCode),
                "billing_option": fob,
                "tender_num": order.SHIPTOCODE,
                "billing": billingaddress,  # end of billto
                "po_num": order.PURCHASEORDERNO,
                "pickup_start_at": self.formatDate(order.ORDERDATE),
                "delivery_appt_start_at": self.formatDate(order.PROMISEDATE),
                # end of pieces
                "commodities": commodities,

                "notes":
                    # "InternalNotes":self.groupRecords(order.COMMENTS)[0],

                    "OriginInstructions: {}".format(
                        self.processComments(str(notes))),





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

                        # sets apiurl for the correct customer for this order

                        logging.info("Sending SO# {}".format(
                            order.SALESORDERNO))
                        apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/create_booked_order'.format(
                            order.ARDIVISIONNO, order.CUSTOMERNO)
                        r = requests.post(
                            apiurl, json=params, headers=headers)
                        resp = r.json()

                        if('error_code' in resp):
                            logging.error(params)
                            #print("Send was successful! " + str(recordcount))
                            logging.error(
                                "Send was NOT successful for order: " + str(order.SALESORDERNO))
                            logging.error("Error: " + str(resp))
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
                        # print("Duplicate record removed " +
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

                    # sets apiurl for the correct customer for this order
                    apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/create_booked_order'.format(
                        order.ARDIVISIONNO, order.CUSTOMERNO)
                    # print("APIURL: {}".format(apiurl))
                    # print("PARAMS: {}".format(params))
                    print("Sending SO# {}".format(order.SALESORDERNO))

                    r = requests.post(
                        apiurl, json=params, headers=headers)
                    resp = r.json()
                    # sentorders.append(order.SALESORDERNO)
                    if('error_code' in resp):
                        #print("Send was successful! " + str(recordcount))
                        # logging.error(params)
                        logging.error(
                            "Send was NOT successful for order: " + str(order.SALESORDERNO))
                        logging.error("Error: " + str(resp))
                        failedorders.append(order.SALESORDERNO)
                    else:
                        #print("SVAPI reports an Error when sending data")
                        # print(resp)
                        # TODO: reason why it fpyailed
                        logging.info(
                            "Success when sending SO#: " + str(order.SALESORDERNO))

                        # failedorders.append(order.SALESORDERNO)

                    failedorders.append(order.SALESORDERNO)

    def updateorders(self, data):
        recordcount = 0
        # keeps track of sent SO#s
        ordernos = []
        # keeps track of successful Updates to SV
        sentorders = []
        # keeps track of failed orders going to SV
        failedorders = []
        auth = self.authorg(self.whcode)
        for order in data:
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(auth)


            }

            commodities = self.processPieces(
                order.LINEITEMS, order, order.ITEMDESC, order.ITEMCODES, order.UNITPRICE, order.PALLETQTY, self.LTLFLAG)
            params = {
                "commodities": commodities
            }

            # checks if item code is valid for current record
            # this ignores / skus in rows from DB from sending as separate orders to TMS
            if("INS" in str(order.ITEMCODE) or "FRM" in str(order.ITEMCODE) or "ABS" in str(order.ITEMCODE)):
                # this enables duplicates to be found
                if(len(ordernos) > 1):
                    # checks if the current SO is not equal to the last order submitted
                    # if they are the same then that means it is a duplicate and shouldn't be sent
                    if(order.SALESORDERNO != ordernos.pop()):

                        # sets apiurl for the correct customer for this order

                        print("ORDER UPDATED! {}".format(order.SALESORDERNO))
                        apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/orders/ext:{}/revise_commodities'.format(
                            order.ARDIVISIONNO, order.CUSTOMERNO, order.SALESORDERNO)
                        print("UPDATED COMMODITIES JSON: {}".format(params))
                        r = requests.put(
                            apiurl, json=params, headers=headers)
                        resp = r.json()

                        if('error_code' in resp):
                            # logging.error(params)
                            #print("Update was successful! " + str(recordcount))
                            logging.error(
                                "Update was NOT successful for order: " + str(order.SALESORDERNO))
                            logging.error("Error: " + str(resp))
                            sentorders.append(order.SALESORDERNO)
                        else:
                            #print("SVAPI reports an Error when Updateing data")
                            # print(resp)
                            # TODO: reason why it fpyailed
                            logging.info(
                                "Success when Updateing SO#: " + str(order.SALESORDERNO))

                            # this is what keeps track of any extra lines still in db
                        ordernos.append(order.SALESORDERNO)

                    else:
                        # print("Duplicate record removed " +
                            #  str(order.SALESORDERNO))
                        logging.info("Duplicate record removed " +
                                     str(order.SALESORDERNO))

                    # except Exception :
                    # print("Something went wrong with Updateing data to SV API" )
                # if it's the first record in the data sync then go ahead and Update it
                else:
                    # appends sales order to duplicate checking list
                    # this is what keeps track of any extra lines still in db
                    ordernos.append(order.SALESORDERNO)
                    # print("Valid record: " + order.ITEMCODE)

                    # sets apiurl for the correct customer for this order
                    apiurl = 'https://platform.sandbox01.roserocket.com/api/v1/customers/external_id:{}{}/orders/ext:{}/revise_commodities'.format(
                        order.ARDIVISIONNO, order.CUSTOMERNO, order.SALESORDERNO)
                    # print("APIURL: {}".format(apiurl))
                    # print("PARAMS: {}".format(params))
                    print("Updating SO# {}".format(order.SALESORDERNO))
                    print("UPDATED COMMODITIES JSON: {}".format(params))
                    r = requests.put(
                        apiurl, json=params, headers=headers)
                    resp = r.json()
                    # sentorders.append(order.SALESORDERNO)
                    if('error_code' in resp):
                        #print("Update was successful! " + str(recordcount))
                        # logging.error(params)
                        logging.error(
                            "Update was NOT successful for order: " + str(order.SALESORDERNO))
                        logging.error("Error: " + str(resp))
                        failedorders.append(order.SALESORDERNO)
                    else:
                        #print("SVAPI reports an Error when Updateing data")
                        # print(resp)
                        # TODO: reason why it fpyailed
                        logging.info(
                            "Success when Updateing SO#: " + str(order.SALESORDERNO))

                        # failedorders.append(order.SALESORDERNO)

                    failedorders.append(order.SALESORDERNO)

    def synccustomers(self, data):
        apiurl = 'https://platform.roserocket.com/api/v1/customers'
        auth = self.authorg(self.whcode)
        for order in data:

            # this determins the billing type
            fob = ''
            if(order.FOB == 'CC'):
                fob = 'collect'
            if(order.FOB == 'PP'):
                fob = 'prepaid'

            if(order.CUSTOMERNO == 'HOMEDCO'):
                fob = 'thirdparty'

            # print("Auth Token: {}".format(self.authorg(order.WAREHOUSECODE)))
            headers = {
                'Accept': 'application/json',
                'Authorization': 'Bearer {}'.format(auth)


            }
            params = {
                "external_id": order.ARDIVISIONNO + order.CUSTOMERNO,
                "name": order.BILLTONAME,

                "address_1": order.BILLTOADDRESS1,
                "address_2": order.BILLTOADDRESS2,
                "city": order.BILLTOCITY,
                "state": order.BILLTOSTATE,
                "postal": order.BILLTOZIPCODE,
                "country": "US",
                "short_code": str(order.CUSTOMERNO)[:6],
                "currency": 'usd',
                            "default_billing_option": fob,
                            "default_dim_type": "ltl",
                            "measurement_unit": "inch",
                            "weight_unit": "lb",
                            "is_active": True,
                "billing_contact_name": order.BILLTONAME}
            # print(params)

            r = requests.post(
                apiurl, json=params, headers=headers)
            logging.info("Sync Customer Response: {}".format(r.text))
            resp = r.json()

            # sentorders.append(order.SALESORDERNO)
            if('error_code' in resp):
                # if(str(resp['Success']) == str('True')):
                #print("Send was successful! " + str(recordcount))
                logging.error(
                    "Send was unsuccessful for customer: " + str(order.CUSTOMERNO))

            else:
                #print("SVAPI reports an Error when sending data")
                # TODO: reason why it failed
                logging.info("Send was successful when sending Customer " +
                             str(order.CUSTOMERNO))
                logging.info("Send was successful when sending Customer " +
                             str(order.CUSTOMERNO))

    def updatesync(self,org):
        
        updatedata = RoseRocketIntegrationBackend().updateorders(org)
        self.updateorders(updatedata)


if __name__ == "__main__":

    orgs = pw.orgs.keys()
    for org in orgs:
        logging.info("ORG: {}".format(org))
        data = RoseRocketIntegrationBackend().getAllData(org)
        rr = RoseRocketIntegration(org)
        rr.logStart()
        rr.synccustomers(data)
        rr.sendData(data)
