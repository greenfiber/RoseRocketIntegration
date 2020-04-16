import pyodbc
import logging
from secretprod import secrets as secrets
cx = pyodbc.connect("DSN=gf32;UID={};PWD={}; MARS_Connection=Yes".format(
    secrets.dbusr, secrets.dbpw))
# for use at home
# cx = pyodbc.connect("DSN=gf64;UID={};PWD={}".format(secrets.dbusr,secrets.dbpw))


class RoseRocketIntegrationBackend():

    def writefreightdata(self,data):
        query = ''' 
        
        insert into [InSynch].[dbo].[TOSAGE_SO_SalesOrderHeader](SalesOrderNo,UDF_OFD,UDF_EST_FREIGHT_CHG,ShipVia)values(?,?,?,?)
        '''
        cursor = cx.cursor()
        print(data["freightcharge"])
        print(data["SCAC"])
        cursor.execute(query,data["salesorderno"],"Y",data["freightcharge"],data["SCAC"][:15])
        cursor.commit()

    def getTestData(self):
        query = """
        SELECT  *
      
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
    def getUnitPriceByOrderID(self,so,sku):
        query = """
         
        SELECT

        [SALESORDERNO]
       ,ITEMCODE
        ,[UNITPRICE]
        
      
        
        FROM [SVExportStaging].[dbo].[RRINTEGRATION]
       where SALESORDERNO = ? and SALESORDERNO <> ''
       and ITEMCODE = ?
        """
        cursor = cx.cursor()
        cursor.execute(query, so,sku)
        rows = cursor.fetchone()
        return rows
    
    


    def writeapdata(self,data):
        
        
        
            
        query="""
        insert into [SVExportStaging].[dbo].apimport
            values(?,?,?,?,?,?,?,?,?,?)
        """
        
        cursor = cx.cursor()
        cursor.fast_executemany=True
        try:
            cursor.execute(query, str(data["invoiceno"])+str(data["manifestid"])[:8],data["vendorno"],data["whcode"],data["SCAC"],data['invoiceno'],data["total5000"],data["total6000"],data["invoicedate"],data["duedate"],data["manifestid"])
            cursor.commit()
            print("data logged! {}".format(data["invoiceno"]))
        except Exception as e:
            print("AP Import Log Error {}".format(e))
        
    def getallapimportdata(self):
    
        
        query="select * from [SVExportStaging].[dbo].apimport order by invoicedate desc"
        cursor=cx.cursor()
        cursor.execute(query)
        
        return cursor.fetchall()
    def getcurrentapdata(self,whcode):

        
        query="select manifestid from [SVExportStaging].[dbo].apimport where whcode = ?"
        cursor=cx.cursor()
        cursor.fast_executemany=True
        cursor.execute(query,(whcode,))
        
        return cursor.fetchall()

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
    def getorderbyso(self,so):
            query = """
            
            SELECT
            *
        from [SVExportStaging].[dbo].[RRINTEGRATION]
        where SALESORDERNO =?
            """
            cursor = cx.cursor()
            cursor.execute(query, so)
            rows = cursor.fetchall()
            return rows