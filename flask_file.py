import os

import pandas as pd
from flask import Flask, render_template, request, session, logging, url_for, redirect, flash, g
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import json

from input import Input
from lc_dispatch import least_cost_dispatch
import pygal
from pygal.style import DarkGreenBlueStyle
from graph_style_sheet import custom_style
from html_table_template import template

src = r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2'

input_values = Input()

# Selecting folder for uploading actual demand input by the user
UPLOAD_FOLDER = os.path.join(src, "Uploads Folder")

# Selecting folder for uploading demand data for verification
UPLOAD_FOLDER_2 = os.path.join(src, "Verification Folder")

# for allowed extension of uploaded file--should be excel only
ALLOWED_EXTENSIONS = set(['xlsx'])

# Used for saving USERNAME PASSWORDS etc database in mysql...currently not required
engine = create_engine("mysql+pymysql://root:Acegik1357$@localhost/register")
db = scoped_session(sessionmaker(bind=engine))

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2


@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        loginemaildata = db.execute("SELECT email FROM users WHERE email=:email", {"email": email}).fetchone()
        loginpassworddata = db.execute("SELECT password FROM users WHERE email=:email", {"email": email}).fetchone()
        firstname_x = db.execute("SELECT firstname FROM users WHERE email=:email", {"email": email}).fetchone()
        state_x = db.execute("SELECT state FROM users WHERE email=:email", {"email": email}).fetchone()
        print(firstname_x)
        print(state_x)
        firstname_x = str(firstname_x)
        state_x = str(state_x)
        print(type(firstname_x))
        firstname_x = firstname_x.replace('(', '')
        firstname_x = firstname_x.replace(')', '')
        firstname_x = firstname_x.replace(',', '')
        firstname_x = firstname_x.replace('\'', '')
        state_x = state_x.replace('(', '')
        state_x = state_x.replace(')', '')
        state_x = state_x.replace(',', '')
        state_x = state_x.replace('\'', '')
        if loginemaildata is None:
            flash("No Username", "danger")
            return redirect(url_for('home'))
        else:
            for password_data in loginpassworddata:
                if sha256_crypt.verify(password, password_data):
                    flash("You are Logged In", "success")
                    session['user'] = firstname_x
                    return redirect(url_for('planning', firstname=firstname_x, state=state_x, **request.args))
                else:
                    flash("incorrect Password", "danger")
                    # return render_template("home.html")
    return render_template('home.html')


# -------------------------Login Page Ends----------------------------------
# -------------------------Registration Page----------------------------------

@app.route('/register', methods=["POST", "GET"])
def register():
    if request.method == "POST":
        firstname = request.form.get("firstname")
        surname = request.form.get("surname")
        email = request.form.get("email")
        state = request.form.get("state")
        password = request.form.get("password")
        print(firstname)
        secure_password = sha256_crypt.encrypt(str(password))
        if 2 >= 1:
            print("3")
            db.execute(
                "INSERT INTO users(firstname,surname,email,password,state) VALUES(:firstname, :surname,:email,"
                ":password,:state)",
                {"firstname": firstname, "surname": surname, "email": email, "password": secure_password,
                 "state": state})
            print("2")
            db.commit()
            print("1")
            flash("You have successfully Registered. Please Login", "success")
            return redirect(url_for('home'))
        else:
            flash("Password doesn't match", "Danger")
            return
    return render_template('register.html')


# -------------------------Registration page ends----------------------------------
# -------------------------Demand Forecasting Page----------------------------------
@app.route('/planning')
def planning():
    return render_template('planning.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# -----------------------------checking Uploaded Demand file by the user if of desired format---------------------------

@app.route('/planning/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        f = request.files['input_file']
        datetime = request.form['datetime']

        # load_growth = request.form['load_growth']  # Set to input
        # solar_growth = request.form['solar_growth']  # Set to input
        # wind_growth = request.form['wind_growth']  # Set to input
        # input_values.set_growth_rates([load_growth, solar_growth, wind_growth])

        # Displaying error if the Input is left Blank
        if datetime == '':
            flash("Enter the Input Date Field!!", "danger")
            return redirect(url_for('planning'))

        # Checking if the file uploaded is excel sheet only
        if f and allowed_file(f.filename):
            # filename = str(datetime) + ".xlsx"
            filename = "Data.xlsx"
            # Saving File in desired Location
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # df_test1 = pd.read_excel("C:\\Users\\nshaju\\Desktop\\Interns_copy\\flask_project_2\\Uploads\\" + filename)
            # # Checking if the length of uploaded file is 96 or not
            # if not len(df_test1) == 96:
            #     os.remove("C:\\Users\\nshaju\\Desktop\\Interns_copy\\flask_project_2\\Uploads\\" + filename)
            #     flash("The Given File Contains " + str(len(df_test1)) + " Data!! It should contain 96 Data", "danger")
            #     return redirect(url_for('planning'))
            # # Filling any NA value with 0
            # df_test1.fillna(0)
            flash("File uploaded successfully as: " + filename, "success")
        else:
            flash("Please Enter the File in xlsx Form   at!!", "danger")
        return redirect(url_for('planning'))


@app.route('/planning/growth_rate', methods=['POST', 'GET'])
def growth_rate():
    if request.method == 'POST':
        load_growth = float(request.form['load_growth'])  # Set to input
        solar_growth = float(request.form['solar_growth'])  # Set to input
        wind_growth = float(request.form['wind_growth'])  # Set to input
        years = int(request.form['years'])
        input_values.set_growth_rates([load_growth, solar_growth, wind_growth])
        input_values.set_years(years)

        return redirect(url_for('planning'))


# -----------------------------checking Uploaded Data-----------------------------
list_unmet_df = []


@app.route('/planning/forecast_dispatch')
def forecast_dispatch():
    list_unmet_df = least_cost_dispatch(UPLOAD_FOLDER, input_values, src)

    flash("Forecasting Completed!! Shift+F5 to View graph!", "success")
    return redirect(url_for('planning'))


def read_excel(filename):
    os.chdir(r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2\Working Files')
    df = pd.read_excel(filename)
    return df


@app.route('/graph', methods=['POST', 'GET'])
def graph_example(chartID='chart_ID', chart_type='line', chart_height=500):
    subtitleText = 'test'
    df = read_excel('Demand.xlsx')
    df1 = df.loc[:, 'Date':'2021-22']
    # df1.set_index('Date', inplace = True)
    list1 = [[1, 2], [2, 3]]
    # dataSet = json.loads(df1.to_json(orient='values'))
    # dataSet = [[1617235200000, 1], [1617236100000, 3.5], [1617237000000, 2], [1617237900000, 3]]
    # pageType = 'graph'
    # chart = {"renderTo": chartID, "type": chart_type, "height": chart_height, }
    # series = [{"name": 'Label1', "data": dataSet}]
    # title = {"text": 'My Title'}
    # xAxis = {"type": "datetime"}
    # yAxis = {"title": {"text": 'yAxis Label'}}
    #
    # return render_template('graph.html', pageType = pageType, subtitleText = subtitleText, chartID=chartID, chart=chart,
    #                        series=series, title=title, xAxis=xAxis, yAxis=yAxis)

    chart = {"renderTo": chartID, "type": chart_type, "height": chart_height, }
    series = [{"name": 'Label1', "data": [1, 2, 3]}, {"name": 'Label2', "data": [4, 5, 6]}]
    title = {"text": 'My Title'}
    xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
    yAxis = {"title": {"text": 'yAxis Label'}}
    return render_template('graph.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis,
                           yAxis=yAxis)


@app.route('/graph_try1', methods=['POST', 'GET'])
def graph_example1():
    return render_template('graph_try1.html')


@app.route('/graph_try2', methods=['POST', 'GET'])
def graph_example2():
    graph = pygal.Line(style=DarkGreenBlueStyle)
    graph.title = '% Change Coolness of programming languages over time.'
    # df = read_excel('Demand.xlsx')
    # df_dispatch = read_excel('Dispatch.xlsx')
    # xAxis = df['Date'].tolist()
    # demand = df['2021-22'].tolist()
    # dispatch = df_dispatch['2021-22'].tolist()

    xAxis = [i for i in range(0, 50)]
    demand = [2*i for i in range(0, 50)]
    dispatch = [3*i for i in range(0, 50)]

    graph.x_labels = xAxis
    graph.add('Demand', demand)
    graph.add('Dispatch', dispatch)
    graph_data = graph.render_data_uri()
    return render_template("graph_try2.html", graph_data=graph_data)

    # chart = {"renderTo": chartID, "type": chart_type, "height": chart_height, }
    # series = [{"name": 'Label1', "data": [1, 2, 3]}, {"name": 'Label2', "data": [4, 5, 6]}]
    # title = {"text": 'My Title'}
    # xAxis = {"categories": ['xAxis Data1', 'xAxis Data2', 'xAxis Data3']}
    # yAxis = {"title": {"text": 'yAxis Label'}}
    # return render_template('graph.html', chartID=chartID, chart=chart, series=series, title=title, xAxis=xAxis,
    #                        yAxis=yAxis)


@app.route('/table', methods=['POST', 'GET'])
def table():
    df = read_excel('BESS Benefits 4000 Cycles 2 Hours.xlsx')
    df1 = pd.DataFrame()

    size = 20

    divisor = 10000000
    if request.method == 'POST':
        option = request.form['options']
        if option == "option1":
            divisor = 10000000
        if option == "option2":
            divisor = size * 10000000

    df1['Year'] = df['Year']
    df1['Loan Repayment'] = df['Loan'] / divisor
    df1['Interest'] = df['Interest Payment'] / divisor
    df1['Return on Equity'] = df['Return on Equity'] / divisor
    df1['Opertional Expenses'] = df['Operational Expenses'] / divisor
    # if constant_throughput == 1:
    #     df1['Capacity Upgradation'] = df['Capacity Upgradation Cost']
    df1['Interest on working capital'] = df['Interest on Working Capital'] / divisor
    df1['Total Outflow'] = df['Total Outflow'] / divisor
    df1['Scrap Value'] = df['Scrap Value'] / divisor
    df1['Ramping & peak support benefits'] = df['Net Benefits'] / divisor
    df1['Loss reduction through BESS'] = df['Transmission Loss Reduction'] / divisor
    df1['Capacity Deferral'] = df['Capacity Deferral Benefits'] / divisor
    df1['Revenue by reducing outages'] = df['Outage Reduction Benefits'] / divisor
    df1['Net Cashflow'] = df['Net Cash flow'] / divisor
    df1 = df1.round(2)
    npv_list = df['Final NPV'] / divisor
    npv_list = npv_list.round(2)
    npv_value = npv_list.sum()
    # npv = ['' if x == 0 else x for x in npv_list]
    # df1['NPV'] = npv

    red_colour = False
    if npv_value < 0:
        red_colour = True

    # df1.set_index('Year', inplace=True)

    # return render_template(df1.to_html())

    df1['Year'] = pd.to_numeric(df1['Year'], downcast='integer')
    return render_template("table.html", column_names=df1.columns.values, row_data=list(df1.values.tolist()), zip=zip,
                           bess_name="20MW/40MWh 4000 cycles BESS", NPV=npv_value, colour=red_colour)



if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run()
