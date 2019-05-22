import pyodbc
from pws import Secrets as secrets
cx = pyodbc.connect("DSN=gf32;UID={};PWD={}".format(secrets.dbusr,secrets.dbpw))

class RoseRocketIntegrationBackend():
    def getAllData(self):
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
      
        FROM [SVExportStaging].[dbo].[SVExport_TEST]
        
        """
        yCount = 0
        nCount = 0
        custCount = 0

        cursor = SVDataSync.cx.cursor()
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