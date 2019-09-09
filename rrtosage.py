from flask import Flask, request, render_template, redirect, flash, session, abort, jsonify
from flask_api import status
import os
app = Flask(__name__)
app.secret_key = os.urandom(12)

@app.route('/', methods=['GET','POST'])
def default():
    if(request.args['token'] == 'CTq74c42cuUMkudJbPVF3GsH'):
        if(request.method == 'GET'):
            print(request.data)
            return status.HTTP_200_OK
        else:
            print(request.data)
            return status.HTTP_200_OK

    else:
        return status.HTTP_401_UNAUTHORIZED