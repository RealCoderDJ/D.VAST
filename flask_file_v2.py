import os
import webbrowser

import pandas as pd
import pygal
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory

import download_tables
from bess_analysis import analysis, sensitivity_analysis_cost_roe
from graph_style_sheet import custom_style
from input import Input
from lc_dispatch import least_cost_dispatch

src = r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2'

input_values = Input()

# Selecting folder for uploading actual demand input by the user
UPLOAD_FOLDER = os.path.join(src, "Uploads Folder")

# Selecting folder for uploading demand data for verification
UPLOAD_FOLDER_2 = os.path.join(src, "Verification Folder")

working_files = os.path.join(src, 'Working Files')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2

# input_done = False
# model_run = False

input_done = True
model_run = True

list_unmet_df = []
df_load_schedule = pd.DataFrame()
df_unmet = pd.DataFrame()
df_size_npv = pd.DataFrame()


# TODO loading screens

# Function to input ramp up time to select the specific time slot in the system
@app.route('/input/ramp_time', methods=['POST', 'GET'])
def ramp_up_time_calculation():
    if request.method == 'POST':
        # Extracting inputs from the 'input' html page given by the user
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        input_values.set_ramp_up_time_selection(start_time, end_time)
        print(input_values.ramp_up_start_time, input_values.ramp_up_end_time)

    return redirect(url_for('input_page'))


@app.route('/', methods=["GET", "POST"])
def home():
    return render_template('home.html', input_done=input_done, model_run=model_run)


@app.route('/input', methods=["GET", "POST"])
def input_page():
    # Do Input
    return render_template('input.html', input_done=input_done, model_run=model_run)


@app.route('/input/upload', methods=['POST', 'GET'])
def input_upload():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        f = request.files['datafile']

        filename = "Data.xlsx"
        # Saving File in desired Location
        f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        flash("File uploaded successfully as: " + filename, "success")
        return redirect(url_for('input_page'))


@app.route('/input/installed_capacity', methods=['POST', 'GET'])
def installed_capacity():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        solar_ic = float(request.form['solar_ic'])
        wind_ic = float(request.form['wind_ic'])
        solar_ic_cur = float(request.form['solar_ic_cur'])
        wind_ic_cur = float(request.form['wind_ic_cur'])

        input_values.set_re_ic(solar_ic, wind_ic, solar_ic_cur, wind_ic_cur)

        return redirect(url_for('input_page'))


@app.route('/input/forecast', methods=['POST', 'GET'])
def input_forecast():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        load = float(request.form['load'])
        solar = float(request.form['solar'])
        wind = float(request.form['wind'])
        year = int(request.form['year'])

        input_values.set_years(year)
        input_values.set_growth_rates([load, solar, wind])
        print(input_values.load_growth, input_values.solar_growth, input_values.wind_growth, input_values.years)

        return redirect(url_for('input_page'))


@app.route('/forecast', methods=['POST', 'GET'])
def forecast_scheduling():
    global list_unmet_df, list_ramp_req_df, df_load_schedule, df_unmet

    list_unmet_df, list_ramp_req_df = least_cost_dispatch(UPLOAD_FOLDER, input_values, src)
    flash("Forecast and Dispatch Simulations Done!", "success")
    return redirect(url_for('input_page'))


@app.route('/input/bess_parameters', methods=['POST', 'GET'])
def input_bess_parameters():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        life = int(request.form['life'])
        hours = int(request.form['hour'])
        rt_efficiency = float(request.form['rt_efficiency'])
        dod_up = float(request.form['ul'])
        dod_low = float(request.form['ll'])

        cycles = int(request.form['cycles'])
        cost = float(request.form['cost'])
        degr = float(request.form['degr'])
        scrap_percent = float(request.form['scrap'])
        if 'yesno' in request.form:
            throughput = int(request.form['yesno'])
            if throughput == 1:
                bess_cost_reduction_rate = float(request.form['cost_redn'])

        input_values.set_life(life)
        input_values.set_hours(hours)
        input_values.set_bess_param(cycles, rt_efficiency, dod_up, dod_low, degr, scrap_percent)
        input_values.set_bess_cost(hours, cost)
        if 'yesno' in request.form:
            input_values.set_constant_throughput(throughput)
            if throughput == 1:
                input_values.set_bess_cost_reduction(bess_cost_reduction_rate)

        print(input_values.cost_2hr, input_values.hours, input_values.degr, input_values.dod)

        return redirect(url_for('input_page'))


@app.route('/input/bess_size', methods=['POST', 'GET'])
def input_bess_size():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        start = int(request.form['start'])
        end = int(request.form['end'])
        incr = int(request.form['incr'])

        input_values.set_bess_range(start, end, incr)

        print(input_values.bess_size_start, input_values.bess_size_end, input_values.bess_size_incr)

        return redirect(url_for('input_page'))


@app.route('/input/energy_charge', methods=['POST', 'GET'])
def input_energy_charge():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        costs = [0, 0, 0, 0]
        costs[0] = float(request.form['dsm'])
        costs[1] = float(request.form['peak'])
        costs[2] = float(request.form['even'])
        costs[3] = float(request.form['morn'])

        eci = float(request.form['eci'])

        input_values.set_energy_cost_increase(eci)
        input_values.set_costs(costs)

        print(input_values.costs)

        return redirect(url_for('input_page'))


@app.route('/input/financial_param', methods=['POST', 'GET'])
def input_financial_param():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        loan = float(request.form['loan'])
        interest = float(request.form['interest'])
        tax_rate = float(request.form['tax'])
        roe = float(request.form['roe'])
        discount = float(request.form['discount'])
        opex = float(request.form['opex'])

        input_values.set_financial_param(loan, interest, tax_rate, roe, opex)
        input_values.set_discount_rate(discount)

        print(input_values.roe)

        return redirect(url_for('input_page'))


@app.route('/input/other_benefits', methods=['POST', 'GET'])
def input_other_benefits():
    if request.method == 'POST':
        # Extracting Inputs from the HTML Page given by user
        transformer_cost = float(request.form['trans_cost'])
        transformer_interest = float(request.form['trans_int'])
        land_cost = float(request.form['land_cost'])
        trans_land_req = float(request.form['land_req'])
        total_outage = float(request.form['outage'])
        average_tariff = float(request.form['tariff'])
        transmission_reduction = float(request.form['trans_save'])

        input_values.set_transformer_param(transformer_cost, transformer_interest, land_cost, trans_land_req)
        input_values.set_outage_param(average_tariff, total_outage)
        input_values.set_transmission_reduction(transmission_reduction)

        print(input_values.transformer_cost, input_values.transformer_interest, input_values.land_cost, input_values.trans_land_req)

        return redirect(url_for('input_page'))
    # TODO Input forms


@app.route('/analysis', methods=['POST', 'GET'])
def battery_analysis():
    global df_size_npv, input_done, model_run
    input_done = True
    df_size_npv = analysis(input_values, list_unmet_df, list_ramp_req_df, src)
    model_run = True

    # TODO Remove this
    bess_size = input_values.bess_size_start
    while bess_size <= input_values.bess_size_end:
        df = sensitivity_analysis_cost_roe(input_values, list_unmet_df, list_ramp_req_df, bess_size, src)
        bess_size += input_values.bess_size_incr

    flash("Forecast and Scheduling Done!", "success")
    return redirect(url_for('home'))


@app.route('/graph_npv_size', methods=['POST', 'GET'])
def graph_npv_size():
    graph = pygal.Line(style=custom_style, x_title='BESS Size (MW)', y_title='NPV / MW (₹ crores / MW)',
                       show_legend=False, show_y_guides=False, include_x_axis=True,
                       x_label_rotation=270, stroke_style={'width': 3})
    graph.title = 'NPV vs BESS Size'

    # To read from excel
    cycles = input_values.total_cycles
    hours = input_values.hours
    years = input_values.life
    df = read_excel('NPV vs Size ' + str(cycles) + ' Cycles ' + str(hours) + ' Hours ' + str(years) + ' Years.xlsx',
                    'Sheet1')

    # Without Reading File
    # df = df_size_npv.copy()
    df['NPV'] /= df['Size']
    xAxis = df['Size'].tolist()
    npv = ((df['NPV'] / 10000000).round(2)).tolist()

    graph.x_labels = xAxis
    graph.add('NPV', npv)
    graph_data = graph.render_data_uri()
    return render_template("graph_npv_size.html", graph_data=graph_data)


@app.route('/sensitivity_graph/<size>', methods=['POST', 'GET'])
def sensitivity_graph(size):
    bess_size = int(size)
    hr = input_values.hours

    sizes = []
    i = input_values.bess_size_start
    while i <= input_values.bess_size_end:
        sizes.append(i)
        i += input_values.bess_size_incr

    graph = pygal.Line(include_x_axis=True, style=custom_style, x_title='BESS Cost / MW (₹ crores)', dots_size=1.5,
                       y_title='NPV / MW (₹ crores)', x_label_rotation=270, stroke_style={'width': 2})
    graph.title = 'Cost-Roe Sensitivity Analysis (' + size + ' MW / ' + str(hr * bess_size) + ' MWh)'

    # df = sensitivity_analysis_cost_roe(input_values, list_unmet_df, bess_size, src)
    # TODO remove from /analysis also
    # TODO remove reading from excel
    cycles = input_values.total_cycles
    df = read_excel('Cost-Roe sensitivity ' + size + ' MW ' + str(cycles) + ' Cycles ' + str(hr) + ' Hours.xlsx',
                    'Sheet1')
    df.set_index("Cost", inplace=True)  # remove this later
    df.sort_index(inplace=True)

    df_viable = pd.DataFrame()

    cost = list((df.index.values / 10000000).round(2))
    cost_crore = df.index.values
    graph.x_labels = cost
    cols = df.columns.tolist()
    viable_list = []
    for c in cols:
        npv_list = (df[c] / bess_size).round(2).tolist()
        graph.add(c, npv_list)
        l = len(npv_list)
        viable_cost = cost_crore[l - 1] - npv_list[l - 1] * (
                    (cost_crore[l - 1] - cost_crore[0]) / (npv_list[l - 1] - npv_list[0]))
        viable_cost = round(viable_cost / 10000000, 2)
        viable_list.append(viable_cost)
    df_viable['RoE Percent (Post-tax)'] = cols
    df_viable['Cost at which BESS becomes Viable'] = viable_list

    graph.render_to_file(r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2/chart.svg')
    graph_data = graph.render_data_uri()
    # graph_data.render_in_browser()
    return render_template("sensitivity_graph.html", graph_data=graph_data, sizes=sizes, sel_op=bess_size, hr=hr,
                           column_names=df_viable.columns.values, row_data=list(df_viable.values.tolist()), zip=zip, )


def read_excel(filename, sheetname):
    os.chdir(r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2\Working Files')
    df = pd.read_excel(filename, sheet_name=sheetname)
    return df


def make_table(df, divisor):
    df1 = pd.DataFrame()

    df1['Year'] = df['Year']
    df1['Loan Repayment'] = df['Loan'] / divisor
    df1['Interest'] = df['Interest Payment'] / divisor
    df1['Return on Equity'] = df['Return on Equity'] / divisor
    df1['Opertional Expenses'] = df['Operational Expenses'] / divisor
    if input_values.constant_throughput == 1:
        df1['Capacity Upgradation'] = df['Capacity Upgradation Cost']
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
    df1['Year'] = [round(x) for x in df1['Year'].tolist()]

    return df1, npv_value


@app.route('/table', methods=['POST', 'GET'])
def table():
    df = read_excel('BESS Benefits 4000 Cycles 2 Hours.xlsx', '20 MW 2 hour')

    sizes = [i for i in range(1, 51)]

    divisor = 10000000
    if request.method == 'POST':
        option = request.form['options']
        if option == "option1":
            divisor = 10000000
        if option == "option2":
            divisor = 20 * 10000000

    df1, npv_value = make_table(df, divisor)

    red_colour = False
    if npv_value < 0:
        red_colour = True

    return render_template("table.html", column_names=df1.columns.values, row_data=list(df1.values.tolist()), zip=zip,
                           bess_name="20MW/40MWh 4000 cycles BESS", NPV=npv_value, NPV_MW=round(npv_value / 20, 2),
                           colour=red_colour, sizes=sizes)


@app.route('/input_print', methods=['GET', 'POST'])
def print_input():
    print(input_values.roe, input_values.tax_rate, input_values)


@app.route('/table/<size>', methods=['GET', 'POST'])
def select_size(size):
    sizes = []
    i = input_values.bess_size_start
    while i <= input_values.bess_size_end:
        sizes.append(i)
        i += input_values.bess_size_incr

    bess_size = int(size)
    hr = input_values.hours
    cycles = input_values.total_cycles
    life = input_values.life
    df = read_excel('BESS Benefits ' + str(cycles) + ' Cycles ' + str(hr) + ' Hours ' + str(life) + ' Years.xlsx',
                    size + ' MW ' + str(hr) + ' hour')

    divisor = 10000000
    if request.method == 'POST':
        option = request.form['options']
        if option == "option1":
            divisor = 10000000
        if option == "option2":
            divisor = size * 10000000

    df1, npv_value = make_table(df, divisor)

    red_colour = False
    if npv_value < 0:
        red_colour = True

    # df1.set_index('Year', inplace=True)

    return render_template("table_size.html", column_names=df1.columns.values, row_data=list(df1.values.tolist()),
                           zip=zip, bess_name=size + 'MW/' + str(bess_size * 2) + 'MWh ' + str(cycles) + ' cycles BESS',
                           NPV=npv_value, NPV_MW=round(npv_value / bess_size, 2), colour=red_colour, sizes=sizes,
                           sel_op=bess_size)


@app.route('/downloads/<dwnld>', methods=['GET', 'POST'])
def select_download(dwnld):
    downloads = ['Forecast and Schedule', 'BESS Analysis'] #, 'BESS Sensitivity Analysis']

    if dwnld == 'Forecast and Schedule':
        df = download_tables.forecast_table(input_values)

    if dwnld == 'BESS Analysis':
        df = download_tables.bess_table(input_values)

    # if dwnld == 'BESS Sensitivity Analysis':
    #     df = download_tables.forecast_table(input_values)

    return render_template("download.html", column_names=df.columns.values, row_data=list(df.values.tolist()),
                           zip=zip, downloads=downloads, sel_op=dwnld)


@app.route('/file/<name>', methods=['GET', 'POST'])
def return_file(name):
    os.chdir(working_files)
    print(name)
    return send_from_directory(working_files, name, as_attachment=True)
    # return name


webbrowser.open('http://127.0.0.1:5000/', new=1)

if __name__ == '__main__':
    app.secret_key = os.urandom(24)
    app.debug = True
    app.run()
