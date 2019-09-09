from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify
from flask_api import status
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/', methods=['GET','POST'])
def default():
    token = request.args.get('token')
    if(token == 'CTq74c42cuUMkudJbPVF3GsH'):
        print(request.data)
        # if(request.method == 'GET'):
        #     print(request.data)
        #     return status.HTTP_200_OK
        # else:
        #     print(request.data)
        #     return status.HTTP_200_OK

    else:
        return status.HTTP_401_UNAUTHORIZED

if __name__ == '__main__':
    
    app.run(port='6969', host="0.0.0.0")