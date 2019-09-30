from flask import Flask, render_template, redirect,request
from ..integrationutils import RoseRocketIntegrationUtils
app = Flask(__name__)

@app.route('/' ,methods=['GET',POST])
def hello_world():
    if(request.method == 'POST'):
        rr=RoseRocketIntegrationUtils()
        # startdate=rr.formatdateforreport(request.form['startdate'])
        # enddate=rr.formatdateforreport(request.form['enddate'])
        print(request.form['startdate'])
        print(request.form['enddate'])

    else:
        render_template('index.html')