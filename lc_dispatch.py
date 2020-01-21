import os
from timeit import default_timer as timer

import pandas as pd
from datetime import datetime, timedelta

from dispatch import dispatch_sim
from net_load import net_load


def datetime_range(start, end, delta):
    current = start
    while current < end:
        yield current
        current += delta


#  REMOVE FUNCTION CALL AT BOTTOM
def least_cost_dispatch(directory, input_values, src):
    # directory = os.path.join(src, 'Uploads')
    os.chdir(directory)
    data = pd.ExcelFile("Data.xlsx")
    schedule = data.parse("Load Data", index_col=0)
    solar = data.parse("Solar Generation", index_col=0)
    nuclear = data.parse("Nuclear Generation", index_col=0)
    wind = data.parse("Wind Generation", index_col=0)
    hydro = data.parse("Hydro Generation", index_col=0)
    plants = data.parse("Generating Stations", index_col=0)

    load_growth, solar_growth, wind_growth = input_values.get_growth_rates()
    life = input_values.get_years()  # Set to input

    col = schedule.columns.tolist()
    dates = [date_obj.strftime('%d - %m') for date_obj in col]
    date_col = []
    empty_95 = [''] * 95
    for d in dates:
        date_col.append(d)
        date_col += empty_95
    dates_col = [dt for dt in datetime_range(datetime(2021, 4, 1), datetime(2022, 4, 1), timedelta(minutes=15))]
    df_load_schedule = pd.DataFrame()
    df_unmet = pd.DataFrame()
    df_load_schedule["Date"] = dates_col
    df_unmet["Date"] = dates_col

    year = 0
    list_unmet_df = []
    list_ramp_req_df = []
    while year < life:
        print("Year ", str(year + 1))
        start_net_load = timer()
        net_schedule = net_load(schedule, solar, nuclear, wind, hydro, year,
                                load_growth, solar_growth, wind_growth, src)
        end_net_load = timer()
        print("Time taken for calculating Net Load ", str(end_net_load - start_net_load), "s")  # Time in seconds

        start_dispatch = timer()
        unmet_df, ramp_req_df = dispatch_sim(plants, net_schedule, year, src)
        list_unmet_df.append(unmet_df)
        list_ramp_req_df.append(ramp_req_df)
        end_dispatch = timer()
        print("Time taken for dispatch ", str(end_dispatch - start_dispatch), "s")  # Time in seconds
        list_schedule = []
        list_unmet = []
        unmet_df = net_schedule - unmet_df
        for c in net_schedule.columns.tolist():
            list_schedule += net_schedule[c].tolist()
            list_unmet += unmet_df[c].tolist()
        df_load_schedule[str(2021 + year) + "-" + str(22 + year)] = list_schedule
        df_unmet[str(2021 + year) + "-" + str(22 + year)] = list_unmet

        year += 1
    return list_unmet_df, list_ramp_req_df, df_load_schedule, df_unmet
