
import requests
import simplejson
import pysftp
import ftputil
import csv
import logging
from shutil import copy2,move
from backend import RoseRocketIntegrationBackend as db

class RoseRocketIntegration():
    def __init__(self,orgname):
        self.orgname=orgname
        
    headers = {

            
        }
    orgs={}
    for org in orgs:
        pass
    apiurl = ""
    data=db.getAllData()
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

            # sets shipment service type based on order quantity
            if(int(float(str(order.LINEITEMS).split('|')[0])) > 700):
                ServiceTypeCode = "TL"
            else:
                ServiceTypeCode = "LT"
            whcode = order.WAREHOUSECODE
            try:
                plantInfo = self.getPlantInfo(whcode)[0]
            except:
                logging.error("ERROR IN WAREHOUSE LOOKUP")
            #THIS IS USED FOR TESTING ONLY
            #rand = self.genrnd()

            #FOB logic to conform to SV standards
            if(order.FOB=='CC'): fob='C'
            if(order.FOB=='PP'):fob='P'
            if(order.CUSTOMERNO=='HOMEDCO'):fob='T'
            else: fob=''

            params = {


                "Consignee": {
                    "CustomerName": order.SHIPTONAME,
                    "Reference": str(order.PURCHASEORDERNO),
                    "CustomerAddress": {
                        "Address1": order.SHIPTOADDRESS1,
                        "Address2": order.SHIPTOADDRESS2,
                        "City": order.SHIPTOCITY,
                        "State": order.SHIPTOSTATE,
                        "PostalCode": order.SHIPTOZIPCODE,
                        "CountryCode": "US",  # REPLACE THIS WITH COLUMN

                    },
                    "Phone": order.TELEPHONENO
                },  # end of consignee


                "Shipper": {"CustomerName": plantInfo["plantName"], "CustomerAddress": {
                    "Address1": plantInfo["Address1"],
                    "Address2": plantInfo["Address2"],
                    "City": plantInfo["City"],
                    "State": plantInfo["State"],
                    "PostalCode": plantInfo["PostalCode"],
                    "CountryCode": plantInfo["CountryCode"]
                }, "Phone": plantInfo["plantPhoneNumber"]

                },  # end of shipper

                "DatesandTimes": {
                    "HousebillDate": self.formatDate(order.ORDERDATE),
                    "ScheduledDeliveryDateType": "on",
                    "ScheduledDeliveryDate": self.formatDate(order.PROMISEDATE)

                },

                "ServiceTypeCode": str(ServiceTypeCode),
                "PaymentCode":fob,

                "BillTo": {
                    "BillToCode": order.ARDIVISIONNO + order.CUSTOMERNO,
                    "BillToName": order.BILLTONAME,
                    "BillToAddress": {
                        "Address1": order.BILLTOADDRESS1,
                        "Address2": order.BILLTOADDRESS2,
                        "City": order.BILLTOCITY,
                        "State": order.BILLTOSTATE,
                        "PostalCode": order.BILLTOZIPCODE,
                        "CountryCode": "US",  # REPLACE THIS WITH COLUMN
                        "Reference": order.PURCHASEORDERNO

                    },
                    "ContactFirstName": order.BILLTONAME
                },  # end of billto

                # end of pieces
                "PiecesDetail": self.processPieces(order.LINEITEMS, order, order.ITEMDESC, order.ITEMCODES),

                "NotesAndDescriptions": {
                    # "InternalNotes":self.groupRecords(order.COMMENTS)[0],
                    "GeneralGoodsDescription": str("SO#: "+order.SALESORDERNO),
                    "OriginInstructions": self.processComments(order.COMMENTS.split('|')),
                    "DeliveryInstructions": ""
                },

                "Station1Code": whcode,
                "HousebillNumber": order.SALESORDERNO



            }
            recordcount += 1

            # checks if item code is valid for current record
            if("INS" in str(order.ITEMCODE) or "FRM" in str(order.ITEMCODE) or "ABS" in str(order.ITEMCODE)):
                # this enables duplicates to be found
                if(len(ordernos) > 1):
                    # checks if the current SO is not equal to the last order submitted
                    # if they are the same then that means it is a duplicate and shouldn't be sent
                    if(order.SALESORDERNO != ordernos.pop()):
                        #print("Valid record: " + order.ITEMCODE)

                        r = requests.post(
                            self.apiurl, json=params, headers=self.headers)
                        resp = simplejson.loads(r.text)

                        if(str(resp['Success']) == str('True')):
                            #print("Send was successful! " + str(recordcount))
                            logging.info(
                                "Send was successful for order: " + str(order.SALESORDERNO))
                            sentorders.append(order.SALESORDERNO)
                        else:
                            #print("SVAPI reports an Error when sending data")
                            # print(resp)
                            # TODO: reason why it fpyailed
                            logging.error(
                                "Error when sending SO#: " + str(order.SALESORDERNO))
                            logging.error("Error: "+ str(resp))
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
                    r = requests.post(
                        self.apiurl, json=params, headers=self.headers)
                    resp = simplejson.loads(r.text)
                    #sentorders.append(order.SALESORDERNO)
                    if(str(resp['Success']) == str('True')):
                        #print("Send was successful! " + str(recordcount))
                        logging.info(
                            "Send was successful for order: " + str(order.SALESORDERNO))
                        sentorders.append(order.SALESORDERNO)
                    else:
                        #print("SVAPI reports an Error when sending data")
                        # TODO: reason why it failed
                        logging.error("Error when sending SO#: " +
                                      str(order.SALESORDERNO))

                        failedorders.append(order.SALESORDERNO)