import pandas as pd


def forecast_table(input_values):
    years = input_values.years
    df = pd.DataFrame()
    df['S. No.'] = [i for i in range(1, years + 1)]
    list1 = []
    list2 = []
    list3 = []
    list4 = []
    for i in range(years):
        list1.append('Net Schedule for ' + str(2021+i) + '-' + str(22+i))
        list2.append("Net_Schedule_" + str(i + 1) + ".xlsx")
        list3.append('Unmet Demand for ' + str(2021 + i) + '-' + str(22 + i))
        list4.append("Unmet_" + str(i + 1) + ".xlsx")
    df['Net Schedule'] = list1
    df["Download1"] = list2
    df['Unmet Demand'] = list3
    df["Download2"] = list4
    df.rename(columns={'Download1': 'Download', 'Download2': 'Download'}, inplace=True)

    return df


def bess_table(input_values):
    start = input_values.bess_size_start
    end = input_values.bess_size_end
    incr = input_values.bess_size_incr
    cycles = input_values.total_cycles
    hr = input_values.hours
    df = pd.DataFrame()
    list1 = []
    list2 = []
    sno = [1]
    list1.append('Overall Cashflow (All Sizes)')
    list2.append('BESS Benefits ' + str(cycles) + ' Cycles ' + str(hr) + ' Hours.xlsx')
    j = 2
    for i in range(start, end + 1, incr):
        sno.append(j)
        list1.append('Result - ' + str(i) + 'MW/' + str(i*hr) + 'MWh BESS (' + str(cycles) + 'cycles)')
        list2.append('Result BESS' + str(i) + '_' + str(hr) + 'hr ' + str(cycles) + ".xlsx")
        j += 1
    df['S. No.'] = sno
    df['Result'] = list1
    df["Download"] = list2

    return df


def sensitivity_table(input_values):
    start = input_values.bess_size_start
    end = input_values.bess_size_end
    incr = input_values.bess_size_incr
    cycles = input_values.total_cycles
    hr = input_values.hours
    df = pd.DataFrame()
    list1 = []
    list2 = []
    sno = [1]
    list1.append('Overall Cashflow (All Sizes)')
    list2.append('BESS Benefits ' + str(cycles) + ' Cycles ' + str(hr) + ' Hours.xlsx')
    j = 2
    for i in range(start, end + 1, incr):
        sno.append(j)
        list1.append('Result - ' + str(i) + 'MW/' + str(i*hr) + 'MWh BESS (' + str(cycles) + 'cycles)')
        list2.append('Result BESS' + str(i) + '_' + str(hr) + 'hr ' + str(cycles) + ".xlsx")
        j += 1
    df['S. No.'] = sno
    df['Result'] = list1
    df["Download"] = list2

    return df
