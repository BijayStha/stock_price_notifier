from flask import Flask, render_template, request, redirect, flash, url_for
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
        for ticker in tickers:
            ticker1 = yf.Ticker(ticker)
            data = ticker1.history(interval=freq)
            last_quote = data['Close'].iloc[-1]
    except:
        print(f"Cannot get info, it probably does not exist")
    finally:
        return(last_quote)

## Email alert 

def email_alert (subject, body, to):
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

## Message alert 

def msg_alert(message):
    servicePlanId = "715a0dcbf3ca47548d3ad8090099d1c6"
    apiToken = "9134711c309d4288b0c78f686c21c50a"
    sinchNumber = "447520651963"
    toNumber = "+9779846499837"
    url = "https://us.sms.api.sinch.com/xms/v1" + servicePlanId + "/batches"
    payload = {
        "from": sinchNumber,
        "to": [toNumber],"body": message}
    headers = {"Content-Type": "application/json","Authorization": "Bearer " + apiToken}
    response = requests.post(url, json=payload, headers=headers)
    data = response.json()
    return(data)

##sendAlert
def send_Alert(minimum,maximum,ltp,alert,email):
    if int(ltp)>=int(maximum):
        if alert=='sms':
            msg_alert("The price of stock has crossed upper price threshold")
        if alert=='email':
            body="The price of stock has crossed upper price threshold"
            subject="Stock Price Alert"
            to= email
            email_alert (subject, body, to) 
    if int(ltp)<=int(minimum):
        if alert=='sms':
            msg_alert("The price of stock has crossed lower price threshold")
        if alert=='email':
            body="The price of stock has crossed lower price threshold"
            subject="Stock Price Alert"
            to= email
            email_alert (subject, body, to) 



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
    return render_template("dashboard.html") 
 
@app.route("/savedetails",methods = ["POST","GET"])  
def saveDetails():  
    msg = "msg"  
    if request.method == 'POST':
        fname = request.form["fname"]  
        lname = request.form["lname"]  
        usr_email = request.form["email"] 
        usr_phone = request.form["phone"]   
        usr_password = request.form["password"] 
        
        new_user = User(firstname=fname, lastname=lname, email=usr_email, phone=usr_phone, password=usr_password)
        db.session.add(new_user)
        db.session.commit()

        msg="Client successfully Added"
        return render_template('index.html', msg=msg)
    else:
        return render_template('register.html', title='Register')
 


@app.route("/loginvalidate",methods = ["GET","POST"])  
def loginValidate():  
    msg = '' 
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user:
            if password != user.password:
                flash(f"Username or Password is not correct!", 'danger')
                return render_template('login.html', title='Login')
            else:
                flash(f"Successfully Logged In!", 'success')
                phone=user.phone

                return render_template('dashboard.html',email1=email,phone1=phone)
    else:
        return render_template('login.html', title='Login')


@app.route("/setalert",methods = ["POST","GET"])  
def setAlert():  
    msg = "msg"  
    email1='shresthabijay1@gmail.com'
    phone1='9860201115'
    if request.method == "POST":  
        
        email = email1  
        phone = phone1
        stock = request.form["stock"]
        upperlimit = request.form["upperlimit"] 
        lowerlimit = request.form["lowerlimit"]   
        frequency = request.form["frequency"]
        medium = request.form["medium"]
        ltp=retriveStock(stock, frequency)  
        new_alert = alert(email=email, phone=phone, stock=stock, upperlimit=upperlimit, lowerlimit=lowerlimit, frequency=frequency, medium=medium, ltp=ltp)
        db.session.add(new_alert)
        db.session.commit()

        msg="Alert set"
        send_Alert(lowerlimit,upperlimit,ltp,medium,email)


        return render_template('dashboard.html', msg=msg)
    else:
        return render_template('dashboard.html', title='Dashboard')
    

@app.route("/view")  
def view():  
    new_data = db.session.query(alert).all()
    demand = ["stock", "upperlimit", "lowerlimit", "frequency","ltp"]
    all_data_item = []
    for data in new_data:
        for item in demand:
            if item in data:
                all_data_item.append(data.item)
                return render_template("view.html", rows = all_data_item)

 
 

 


if __name__ == '__main__':
    app.run(debug=True)