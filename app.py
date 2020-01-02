from flask import Flask, render_template, redirect,request, send_file
from nickreport import NickReport
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "public"
class Report():
    report=""
report = Report()
def formatdate(date):
    pass
@app.route('/' ,methods=['GET','POST'])
def default():
    if(request.method == 'POST'):
        
        # startdate=rr.formatdateforreport(request.form['startdate'])
        # enddate=rr.formatdateforreport(request.form['enddate'])
        startdate=str(request.form['startdate']).replace('-','')
        enddate=str(request.form['enddate']).replace('-','')
        nr=NickReport(startdate,enddate)
        report.report=nr.generatereport()
        

        return render_template('done.html', file=report.report)

    else:
        return render_template('index.html')

@app.route("/download/<report>")
def sendreport(report):
    print("REPORT PATH{}".format(report))
    
    return send_file(report, as_attachment=True)

if __name__ == "__main__":
    app.run(port='80',host='0.0.0.0')