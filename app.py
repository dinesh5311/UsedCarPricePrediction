from flask import*
import sqlite3
import os
import pickle
import numpy as np
import sklearn

app = Flask(__name__)
app.secret_key = os.urandom(24)



@app.route('/')
def index():
    if ("user_id") in session:
        return redirect(url_for('loggedin'))
    else:
        return render_template("index.html")
@app.route('/loggedin')
def loggedin():
    if "user_id" in session:
        return render_template("user.html")
    else:
        return redirect(url_for('index'))
@app.route('/logout')
def logout():
    session.pop("user_id",None)
    return redirect(url_for('index'))

    
@app.route('/signin')
def signin():
    return render_template('signin.html')
@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/about')
def about():
    return render_template('about.html')        

@app.route('/predict')
def predict():

    if ("user_id") in session:
        return render_template("predict.html")
    else:
        return redirect(url_for('index'))
        
@app.route('/validateSignup',methods = ['GET','POST'])
def validateSignup():
    msg = None
    r =""
    if request.method == 'POST':
        email = request.form["email"]
        username = request.form["username"]
        password = request.form["password"]
        if len(password)>=6:
            
            conn = sqlite3.connect("detailsDB.db")
            c = conn.cursor()
            r = c.execute("SELECT * FROM userdetail WHERE email = '"+email+"'")
            em =  "notem"
            for i in r :
                em = i
            if em == "notem":
                q = c.execute("SELECT * FROM userdetail WHERE username = '"+username+"'")
                us = "notus"
                for x in q:
                    us = x
                if us == "notus":
                    c.execute("INSERT INTO userdetail VALUES('"+email+"','"+username+"','"+password+"')")
                    conn.commit()
                    conn.close()
                    msg = "Account Created"
                    return render_template("signin.html", mssg = msg)
                else:
                    msg = "User Already exist"
                    return render_template("index.html",msg = msg)
            else:
                msg = "User Already exist"
                return render_template("index.html",msg = msg)
        else:   
            msg = "password >= 6"
            return render_template("signup.html",msg= msg)


    else:
        return redirect(url_for('index'))
@app.route('/validateSignin',methods = ['GET','POST'])
def validateSignin():
    msg = "Invalid Details "
    if request.method == 'POST':
        email = request.form["email"]
        password = request.form["password"]
        conn = sqlite3.connect("detailsDB.db")
        c = conn.cursor()
        c.execute("SELECT * FROM userdetail WHERE email = '"+email+"' and password = '"+password+"'")
        r = c.fetchall()
        for i in r :
            if (email == i[0] and password == i[2]):
                username = i[1]
                session["loggedin"] = True
                session["user_id"] = email
                session["user"] = username
                return redirect(url_for('loggedin'))
            else:
                break
        return render_template("signin.html" ,msg = msg )



    else:
        return redirect(url_for('index'))
@app.route('/validatepredict' ,methods=['GET','POST'])
def validatepredict():
    if request.method == 'POST':
        model_Year = int(request.form['model_year'])
        if model_Year == 0 or model_Year<2000 or model_Year>2021:
            msg = "invalid detail"
            return render_template("predict.html",msg = msg)
        else:
            years_old = 2020-model_Year
            Present_Price = float(request.form['Present_Price'])
            Kms_Driven = int(request.form['Kms_Driven'])
            Fuel_Type_CNG = request.form['Fuel_Type_CNG']
            if Present_Price == 0:
                msg= "invalid detail"
                return render_template("predict.html",mssg = msg)
            else:
                if (Fuel_Type_CNG == 'CNG'):
                    Fuel_Type_CNG = 1
                    Fuel_Type_Pertol = 0
                    Fuel_Type_Diesel = 0
                elif (Fuel_Type_CNG == 'Diesel'):
                    Fuel_Type_CNG = 0
                    Fuel_Type_Pertol =0
                    Fuel_Type_Diesel =1
                else:
                    Fuel_Type_CNG = 0
                    Fuel_Type_Diesel =0
                    Fuel_Type_Pertol=1
                Transmission_Manual = request.form['Transmission_Manual']
                if (Transmission_Manual == 'Manual'):
                    Transmission_Manual = 1
                    Transmission_Automatic = 0
                else:
                    Transmission_Manual = 0
                    Transmission_Automatic = 1
                Owner = int(request.form['Owner'])
                Seller_Type_Dealer = request.form['Seller_Type_Dealer']
                if (Seller_Type_Dealer == 'Dealer'):
                    Seller_Type_Dealer = 1
                    Seller_Type_Individual =0
                else:
                    Seller_Type_Dealer = 0
                    Seller_Type_Individual = 1

                features = [Present_Price,Kms_Driven,Owner,years_old,Fuel_Type_CNG,Fuel_Type_Diesel,Fuel_Type_Pertol,Seller_Type_Dealer,Seller_Type_Individual,Transmission_Automatic,Transmission_Manual]
                final_features = [np.array(features)]
                print(final_features)
                model=pickle.load(open('RF_regressionModel.pkl','rb'))
                prediction=model.predict(final_features)
                output=round(prediction[0],2)
                print(output)
            if output<0:
                return render_template('result.html',prediction_text="Sorry you cannot sell the car")
            else:
                return render_template('result.html',prediction_text="The selling price should be {} L".format(output))

    else:
        return redirect(url_for('index'))
    
if __name__ == '__main__':
    app.run(debug = True)


