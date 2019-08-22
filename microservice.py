from flask import request, jsonify
import flask
from backend import RoseRocketIntegrationBackend
db = RoseRocketIntegrationBackend()
app = flask.Flask(__name__)

data={
            "INS541LD": {"THDSKU": "211904", "UPC": "716891001087","UNITPRICE":""},
            "INS765LD/E": {'THDSKU': "1002476568", "UPC": "729477076546","UNITPRICE":""}


        }

@app.route('/api/orderinfo/<so>/<sku>',methods=['GET'])
def orderinfo(so,sku):
    try:
        orderdata=db.getUnitPriceByOrderID(so,sku)
        data[orderdata.ITEMCODE]["UNITPRICE"] = orderdata.UNITPRICE
        return jsonify(data[orderdata.ITEMCODE])
    except:
        return jsonify({"Error":"Lookup for order data failed"})
    
    
    

app.run()