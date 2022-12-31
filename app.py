from flask import Flask, render_template, request,session, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import yfinance as yf
import smtplib
from email. message import EmailMessage
import requests


app = Flask(__name__) 

app.config['SECRET_KEY'] = '1857140a590c6bc21498eb23bf9f79d5'

# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  firstname = db.Column(db.String(20), unique=False, nullable=False)
  lastname = db.Column(db.String(20), unique=False, nullable=False)
  email = db.Column(db.String(20), unique=True, nullable=False)
  phone = db.Column(db.Integer(), unique=True, nullable=False)
  password = db.Column(db.String(20), nullable=False)
  
class alert(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(20), unique=False, nullable=False)
  phone = db.Column(db.Integer(), unique=False, nullable=False)
  stock = db.Column(db.String(20), unique=False, nullable=False)
  upperlimit = db.Column(db.Float(), unique=False, nullable=False)
  lowerlimit = db.Column(db.Float(), nullable=False)
  frequency = db.Column(db.String(20), nullable=False)
  medium = db.Column(db.String(20), nullable=False)
  ltp=db.Column(db.Float(), nullable=False)

## recieve stock LTP
def retriveStock(stock_name,freq):
    tickers = yf.Ticker(stock_name)
    info = None
    last_quote=0
    try:
        info = tickers.info
        if (info['regularMarketPrice'] == None):
            print("You did not input a correct stock ticker! Try again.")
        else:
            todays_data = tickers.history(period=freq)
            last_quote=todays_data['Close'][0]

       
    except:
        print(f"Cannot get info, it probably does not exist")
    finally:
        print(last_quote)
        return(last_quote)

## Email alert 

def email_alert (subject, body, to):
    status=0
    try:
        msg = EmailMessage()
        msg. set_content ( body)
        msg['subject']= subject
        msg['to'] = to
        
        user = "shresthabijay1@gmail.com"
        msg['from']=user
        password ="hcjlqpakxosddbyn"
        
        server= smtplib.SMTP("smtp.gmail.com",587)
        server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit ()
        status=1
        return status
    
    except:
        return status
    finally:
        return status


## Message alert 

def msg_alert(message,number):
    status=0
    try:
        servicePlanId = "715a0dcbf3ca47548d3ad8090099d1c6"
        apiToken = "9134711c309d4288b0c78f686c21c50a"
        sinchNumber = "447520651963"
        toNumber = number
        url = "https://us.sms.api.sinch.com/xms/v1" + servicePlanId + "/batches"
        payload = {
            "from": sinchNumber,
            "to": [toNumber],"body": message}
        headers = {"Content-Type": "application/json","Authorization": "Bearer " + apiToken}
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        status=1
    except:
        return status
    finally:
        return(status)
   

##sendAlert
def send_Alert(minimum,maximum,ltp,medium,email,phone):

    if int(ltp)==int(maximum):
        if medium=='sms':
            status=msg_alert("The price of stock has touched upper price threshold",phone)
            if status==0:
                return 0
            else:
                return 1

        if medium=='email':
            body="The price of stock has touched upper price threshold"
            subject="Stock Price Alert"
            to= email
            status=email_alert (subject, body, to)
            if status==0:
                return 0
            else:
                return 1

    if int(ltp)>=int(maximum):
        if medium=='sms':
            status=msg_alert("The price of stock has crossed upper price threshold",phone)
            if status==0:
                return 0
            else:
                return 1

        if medium=='email':
            body="The price of stock has crossed upper price threshold"
            subject="Stock Price Alert"
            to= email
            status=email_alert (subject, body, to)
            if status==0:
                return 0
            else:
                return 1

    if int(ltp)==int(minimum):
        if medium=='sms':
            status=msg_alert("The price of stock has touched lower price threshold",phone)
            if status==0:
                return 0
            else:
                return 1

        if medium=='email':
            body="The price of stock has touched lower price threshold"
            subject="Stock Price Alert"
            to= email
            status=email_alert (subject, body, to)
            if status==0:
                return 0
            else:
                return 1

    if int(ltp)<=int(minimum):
        if medium=='sms':
            status=msg_alert("The price of stock has crossed lower price threshold",phone)
            if status==0:
                return 0
            else:
                return 1

        if medium=='email':
            body="The price of stock has crossed lower price threshold"
            subject="Stock Price Alert"
            to= email
            status=email_alert (subject, body, to)
            if status==0:
                return 0
            else:
                return 1 



@app.route("/")  
def index():
    db.create_all()  
    return render_template("index.html");  
 
@app.route("/register")  
def register():  
    return render_template("register.html")  

@app.route("/login")  
def login():  
    return render_template("login.html") 

@app.route("/dashboard")  
def dashboard():
   
    return render_template('dashboard.html')    
   
 
@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    try:

        if request.method == 'POST':
            fname = request.form["fname"]  
            lname = request.form["lname"]  
            usr_email = request.form["email"] 
            usr_phone = request.form["phone"]   
            usr_password = request.form["password"]
            confirm_passs= request.form["password1"]
            if not fname and not lname and not usr_email and not usr_phone and not usr_password:
                msg="Field empty"
                return render_template('register.html', msg=msg)
                
            else:
                if usr_password != confirm_passs:
                    msg="Password doesnot match"
                    return render_template('register.html', msg=msg)
                else:
                    new_user = User(firstname=fname, lastname=lname, email=usr_email, phone=usr_phone, password=usr_password)
                    db.session.add(new_user)
                    db.session.commit()
                    msg="Client successfully Added"
                    return render_template('index.html', msg=msg)
                
        else:
            return render_template('register.html', title='Register')
    except:
        msg="User already registered"
        return render_template('register.html', msg=msg)



 


@app.route("/loginvalidate",methods = ["GET","POST"])  
def loginValidate():  
    msg = ''
    data_alert=None
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            user = User.query.filter_by(email=email).first()
            if user:
                if password != user.password:
                    msg="Username or Password is not correct!"
                    return render_template('login.html', title='Login')
                else:
                    msg="Successfully Logged In!"
                    phone=user.phone
                    session['email'] = email
                    session['phone'] = phone

                    
                    data_alert = alert.query.filter_by(email=email)
                    

                    return render_template('dashboard.html',data=data_alert)
        else:
            return render_template('login.html', title='Login')

    except:
        msg="User not registered"
        return render_template('login.html', msg=msg)

        

@app.route("/setalert",methods = ["POST","GET"])  
def setAlert():  
    msg = "msg"  
    notify="Failed to notify"
    email1=session.get('email')
    phone1=session.get('phone')
    if request.method == "POST":  
        
        email = email1  
        phone = phone1
        stock = request.form["stock"]
        upperlimit = request.form["upperlimit"] 
        lowerlimit = request.form["lowerlimit"]   
        frequency = request.form["frequency"]
        medium = request.form["medium"]
        ltp=retriveStock(stock, frequency)
        if ltp != 0:
            new_alert = alert(email=email, phone=phone, stock=stock, upperlimit=upperlimit, lowerlimit=lowerlimit, frequency=frequency, medium=medium, ltp=ltp)
            db.session.add(new_alert)
            db.session.commit()
            msg="New alert added"
            status_alert=send_Alert(lowerlimit,upperlimit,ltp,medium,email,phone)
            if status_alert==1:
                notify="User has been notified"
            else:
                notify="Server issue. Failed to notify"


        else:
            msg="Invalid stock"
            

        ## Display alert in dashboard
        data_alert = alert.query.all()


        return render_template('dashboard.html', data_alert=data_alert,msg=msg, notify=notify)
    else:
        return render_template('dashboard.html', data_alert=data_alert)
    


  

if __name__ == '__main__':
    app.run(debug=True)