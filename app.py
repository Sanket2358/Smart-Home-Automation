# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response,jsonify
from werkzeug.utils import secure_filename
import os
import cv2
import pandas as pd
import sqlite3
from datetime import datetime
import json
from flask import jsonify
from firebaseUpload import *
from firebaseUpload import device_states

name = ''


app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('dashboard'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    global name

    try:

        voltage, current, power = readFirebase()

        if power < 150:

            load = '🟢 Light Load'

        elif power < 500:

            load = '🟡 Moderate Load'

        elif power < 1200:

            load = '🟠 High Load'

        else:

            load = '🔴 Critical Load'

    except Exception as e:

        print("Firebase Error:", e)

        voltage = 220
        current = 2
        power = 440

        load = '🟡 Moderate Load'

    return render_template(

    'dashboard.html',

    name=name,

    slot1=voltage,
    slot2=current,
    slot3=power,
    slot4=load,

    devices=device_states

)

@app.route('/controlHome', methods=['GET', 'POST'])
def controlHome():

    global name

    voltage, current, power = readFirebase()

    # ================= ENERGY USAGE =================

    usage_percent = min(int((power / 2000) * 100), 100)

    # ================= EFFICIENCY =================

    efficiency = max(100 - usage_percent, 10)

    # ================= OPTIMIZATION =================

    optimization = int((efficiency + usage_percent) / 2)

    return render_template(

        'controlHome.html',

        name=name,

        usage_percent=usage_percent,

        efficiency=efficiency,

        optimization=optimization

    )

@app.route('/control', methods=['POST'])
def control():

    global device_states

    data = request.json

    appliance = data['appliance']

    action = int(data['action'])

    # ================= UPDATE DEVICE STATE =================

    device_states[appliance] = action

    try:

        writeFirebase(appliance, action)

    except Exception as e:

        print("Firebase Write Error:", e)

    return jsonify({

        'message': f'{appliance} updated successfully'

    })

@app.route('/smart-mode', methods=['POST'])
def smart_mode():

    global device_states

    data = request.json

    mode = data['mode']

    # ================= NIGHT MODE =================

    if mode == "night":

        device_states['lamp1'] = 0
        device_states['lamp2'] = 1
        device_states['fan'] = 1
        device_states['tv'] = 0
        device_states['ac'] = 0

    # ================= DAY MODE =================

    elif mode == "day":

        device_states['lamp1'] = 0
        device_states['lamp2'] = 0
        device_states['fan'] = 1
        device_states['tv'] = 0
        device_states['ac'] = 0

    # ================= MOVIE MODE =================

    elif mode == "movie":

        device_states['lamp1'] = 0
        device_states['lamp2'] = 0
        device_states['fan'] = 1
        device_states['tv'] = 1
        device_states['ac'] = 1

    # ================= SLEEP MODE =================

    elif mode == "sleep":

        device_states['lamp1'] = 0
        device_states['lamp2'] = 0
        device_states['fan'] = 1
        device_states['tv'] = 0
        device_states['ac'] = 1

    return jsonify({

        "message": f"{mode} mode activated"

    })

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response

@app.route('/history')
def history():

    import pandas as pd
    import sqlite3

    con = sqlite3.connect('mydatabase.db')

    df = pd.read_sql_query(

        "SELECT * FROM History",

        con

    )

    return render_template(

        'history.html',

        tables=[

            df.to_html(

                classes='table table-bordered table-hover',

                index=False

            )

        ]

    )
@app.route('/api/live-data')
def live_data():

    global device_states

    try:

        # ================= GET REAL DATA =================

        voltage, current, power = readFirebase()

        devices = device_states

        # ================= LOAD STATUS =================

        if power < 150:

            load = "🟢 Light Load"

        elif power < 500:

            load = "🟡 Moderate Load"

        elif power < 1200:

            load = "🟠 High Load"

        else:

            load = "🔴 Critical Load"

        # ================= RETURN REAL DATA =================

        return jsonify({

            "voltage": voltage,
            "current": current,
            "power": power,
            "load": load,
            "devices": devices

        })

    except Exception as e:

        print("Live API Error:", e)

        return jsonify({

            "voltage": 0,
            "current": 0,
            "power": 0,
            "load": "Error",
            "devices": device_states

        })

@app.route('/api/control-data')
def control_data():

    global device_states

    voltage, current, power = readFirebase()

    # ================= ENERGY USAGE =================

    usage_percent = min(int((power / 2000) * 100), 100)

    # ================= EFFICIENCY =================

    efficiency = max(100 - usage_percent, 10)

    # ================= SMART OPTIMIZATION =================

    optimization = 100

    # HEAVY DEVICES REDUCE OPTIMIZATION

    if device_states['ac'] == 1:

        optimization -= 35

    if device_states['tv'] == 1:

        optimization -= 15

    if device_states['fan'] == 1:

        optimization -= 10

    # LIGHTS CONSUME LESS

    if device_states['lamp1'] == 1:

        optimization -= 5

    if device_states['lamp2'] == 1:

        optimization -= 5

    # SECURITY SYSTEM IS EFFICIENT

    if device_states['security'] == 1:

        optimization -= 3

    # POWER BASED ADJUSTMENT

    if power > 1500:

        optimization -= 15

    elif power > 700:

        optimization -= 8

    # LIMIT VALUES

    optimization = max(min(optimization, 100), 5)

    return jsonify({

        "devices": device_states,

        "power": power,

        "voltage": voltage,

        "current": current,

        "usage_percent": usage_percent,

        "efficiency": efficiency,

        "optimization": optimization

        })

@app.route('/charts')
def charts():

    devices = {

        "lamp1": 1,
        "lamp2": 0,
        "fan": 1,
        "ac": 0,
        "tv": 1,
        "security": 1

    }

    slot1 = 230
    slot2 = 2.5
    slot3 = 580
    slot4 = "NORMAL"

    return render_template(

        'charts.html',

        slot1=slot1,
        slot2=slot2,
        slot3=slot3,
        slot4=slot4,
        devices=devices

    )

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)
