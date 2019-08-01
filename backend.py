import pyodbc
import logging
from secret import secrets as secrets
cx = pyodbc.connect("DSN=gf32;UID={};PWD={}".format(
    secrets.dbusr, secrets.dbpw))
# for use at home
# cx = pyodbc.connect("DSN=gf64;UID={};PWD={}".format(secrets.dbusr,secrets.dbpw))


class RoseRocketIntegrationBackend():

    def getTestData(self):
        query = """
        SELECT  [SALESORDERNO]
      ,[ORDERDATE]
      ,[ARDIVISIONNO]
      ,[CUSTOMERNO]
      ,[BILLTONAME]
      ,[BILLTOADDRESS1]
      ,[BILLTOADDRESS2]
      ,[BILLTOCITY]
      ,[BILLTOSTATE]
      ,[BILLTOZIPCODE]
      ,[BILLTOCOUNTRYCODE]
      ,[SHIPTONAME]
      ,[SHIPTOADDRESS1]
      ,[SHIPTOADDRESS2]
      ,[SHIPTOCITY]
      ,[SHIPTOSTATE]
      ,[SHIPTOCODE]
      ,[SHIPTOZIPCODE]
      ,[ORDERSTATUS]
      ,[SHIPEXPIREDATE]
      ,[WAREHOUSECODE]
      ,[FOB]
      ,[UDF_WFP_EXPORT]
      ,[COMMENT]
      ,[SALESPERSONNO]
      ,[ITEMCODE]
      ,[COMMENTS]
      ,[LINEITEMS]
      ,[ITEMDESC]
      ,[UNITOFMEASURE]
      ,[PROMISEDATE]
      ,[ITEMCODES]
      ,[UNITPRICE]
      ,[PURCHASEORDERNO]
      ,[SHIPWEIGHT]
      ,[TELEPHONENO]
      
        FROM [SVExportStaging].[dbo].[RRINTEGRATION]
        where CUSTOMERNO = 'HOMEDCO'
        """
        yCount = 0
        nCount = 0
        custCount = 0

        cursor = cx.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        data = []

        for row in rows:

            data.append(row)
            if(row.UDF_WFP_EXPORT == "Y"):
                yCount += 1
            else:
                nCount += 1
            custCount += 1

        print("Y:"+str(yCount) + " "+"N:"+str(nCount))

        return data

    def getskuinfo(self, gfsku):
        query = """
        
        where ITEMCODE =?
        """
        cursor = cx.cursor()
        cursor.execute(query, gfsku)
        rows = cursor.fetchall()
        data = []

        for row in rows:

            data.append(row)
        return data

    def updateorders(self, whcode):

        query = """
         SELECT  [SALESORDERNO]
      ,[ORDERDATE]
      ,[ARDIVISIONNO]
      ,[CUSTOMERNO]
      ,[BILLTONAME]
      ,[BILLTOADDRESS1]
      ,[BILLTOADDRESS2]
      ,[BILLTOCITY]
      ,[BILLTOSTATE]
      ,[BILLTOZIPCODE]
      ,[BILLTOCOUNTRYCODE]
      ,[SHIPTONAME]
      ,[SHIPTOADDRESS1]
      ,[SHIPTOADDRESS2]
      ,[SHIPTOCITY]
      ,[SHIPTOSTATE]
      ,[SHIPTOCODE]
      ,[SHIPTOZIPCODE]
      ,[ORDERSTATUS]
      ,[SHIPEXPIREDATE]
      ,[WAREHOUSECODE]
      ,[UDF_UPDATE_RR]
      ,[FOB]
      ,[UDF_WFP_EXPORT]
      ,[COMMENT]
      ,[SALESPERSONNO]
      ,[ITEMCODE]
      ,[PALLETQTY]
      ,[COMMENTS]
      ,[LINEITEMS]
      ,[ITEMDESC]
      ,[UNITOFMEASURE]
      ,[PROMISEDATE]
      ,[ITEMCODES]
      ,[UNITPRICE]
      ,[PURCHASEORDERNO]
      ,[SHIPWEIGHT]
      ,[TELEPHONENO]
      
      
        FROM [SVExportStaging].[dbo].[RRINTEGRATION]
        WHERE WAREHOUSECODE = ? and UDF_UPDATE_RR = 'Y'
        """

        cursor = cx.cursor()
        cursor.execute(query, whcode)
        rows = cursor.fetchall()
        data = []

        for row in rows:

            data.append(row)

        return data

    def getAllData(self, whcode):
        query = """
        SELECT  [SALESORDERNO]
      ,[ORDERDATE]
      ,[ARDIVISIONNO]
      ,[CUSTOMERNO]
      ,[BILLTONAME]
      ,[BILLTOADDRESS1]
      ,[BILLTOADDRESS2]
      ,[BILLTOCITY]
      ,[BILLTOSTATE]
      ,[BILLTOZIPCODE]
      ,[BILLTOCOUNTRYCODE]
      ,[SHIPTONAME]
      ,[SHIPTOADDRESS1]
      ,[SHIPTOADDRESS2]
      ,[SHIPTOCITY]
      ,[SHIPTOSTATE]
      ,[SHIPTOCODE]
      ,[SHIPTOZIPCODE]
      ,[ORDERSTATUS]
      ,[SHIPEXPIREDATE]
      ,[WAREHOUSECODE]
      ,[UDF_UPDATE_RR]
      ,[FOB]
      ,[UDF_WFP_EXPORT]
      ,[COMMENT]
      ,[SALESPERSONNO]
      ,[ITEMCODE]
      ,[PALLETQTY]
      ,[COMMENTS]
      ,[LINEITEMS]
      ,[ITEMDESC]
      ,[UNITOFMEASURE]
      ,[PROMISEDATE]
      ,[ITEMCODES]
      ,[UNITPRICE]
      ,[PURCHASEORDERNO]
      ,[SHIPWEIGHT]
      ,[TELEPHONENO]
      
      
        FROM [SVExportStaging].[dbo].[RRINTEGRATION]
        WHERE WAREHOUSECODE = ? 
        """
        yCount = 0
        nCount = 0
        custCount = 0

        cursor = cx.cursor()
        cursor.execute(query, whcode)
        rows = cursor.fetchall()
        data = []

        for row in rows:

            data.append(row)
            if(row.UDF_WFP_EXPORT == "Y"):
                yCount += 1
            else:
                nCount += 1
            custCount += 1

        print("Y:"+str(yCount) + " "+"N:"+str(nCount))

        return data

    def getPlantInfo(self, whcode):
        query = """
        SELECT
        [WAREHOUSECODE]
      ,[PLANTADDRESS1]
      ,[PLANTADDRESS2]
      ,[PLANTZIPCODE]
      ,[PLANTCITY]
      ,[PLANTSTATE]
      ,[PLANTNAME]
      ,[PLANTPHONENUMBER]
      ,[PLANTCOUNTRYCODE]
      ,[LAT]
      ,[LONG]
        FROM [SVExportStaging].[dbo].[PlantInfo]
        WHERE [WAREHOUSECODE]=?
         """
        cursor = cx.cursor()
        try:
            cursor.execute(query, whcode)
        except:
            #print("error in warehouse code: "+whcode)
            logging.warning("error in warehouse code: "+whcode)

        rows = cursor.fetchall()
        datadict = []

        for row in rows:
            rowdata = {
                "WarehouseCode": row.WAREHOUSECODE,
                "Address1": row.PLANTADDRESS1,
                "Address2": row.PLANTADDRESS2,
                "City": row.PLANTCITY,
                "State": row.PLANTSTATE,
                "PostalCode": row.PLANTZIPCODE,
                "CountryCode": row.PLANTCOUNTRYCODE,
                "plantPhoneNumber": row.PLANTPHONENUMBER,
                "plantName": row.PLANTNAME,
                "LAT": row.LAT,
                "LONG": row.LONG


            }
            datadict.append(rowdata)
        return datadict
