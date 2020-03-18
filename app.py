from flask import Flask, render_template, redirect,request, send_from_directory
import asyncio
from nickreport import NickReport
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "public"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# class Report():
#     report=""
# report = Report()
def formatdate(date):
    pass
@app.route('/apimport',methods=['GET'])
def apimport():
    from backend import RoseRocketIntegrationBackend
    data=RoseRocketIntegrationBackend().getallapimportdata()
    return render_template("apimportview.html",data=data)
@app.route('/' ,methods=['GET','POST'])
def default():
    if(request.method == 'POST'):
        
        # startdate=rr.formatdateforreport(request.form['startdate'])
        # enddate=rr.formatdateforreport(request.form['enddate'])
        startdate=str(request.form['startdate']).replace('-','')
        enddate=str(request.form['enddate']).replace('-','')
        nr=NickReport(startdate,enddate)
        print("event loop app.py")
        file=nr.main()
        print(file)
        
        
        

        return render_template('done.html', file=file)

    else:
        return render_template('index.html')

@app.route("/download/<report>")
def sendreport(report):
    print("REPORT PATH{}".format(report))
    return send_from_directory(app.config["UPLOAD_FOLDER"],report,as_attachment=True,cache_timeout=0)


if __name__ == "__main__":
    app.run(port='80',host='0.0.0.0')