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
    data = pd.ExcelFile("Data_15min_w_gas_8_re_var.xlsx")
    schedule = data.parse("Load Data", index_col=0)
    solar = data.parse("Solar Generation", index_col=0)
    nuclear = data.parse("Nuclear Generation", index_col=0)
    biomass = data.parse("Biomass Generation", index_col=0)
    wind = data.parse("Wind Generation", index_col=0)
    hydro = data.parse("Hydro Generation", index_col=0)
    plants = data.parse("Generating Stations", index_col=0)
    power_purchase = data.parse("Power Purchase", index_col=0)
    new_gen = data.parse("New Generation", index_col=0)

    load_growth, solar_growth, wind_growth = input_values.get_growth_rates()
    solar_2022, wind_2022, solar_cur, wind_cur = input_values.get_re_ic()
    life = input_values.get_years()  # Set to input

    year = 0  # TODO
    list_unmet_df = []
    list_ramp_req_df = []
    temp_solar_growth = solar_growth
    temp_wind_growth = wind_growth
    while year < life:
        print("Year ", str(year + 1))

        # if year <= 2:
        #     solar_growth = (solar_2022 / solar_cur) ** (1/3)
        #     wind_growth = (wind_2022 / wind_cur) ** (1/3)
        # else:
        #     solar_growth = temp_solar_growth
        #     if wind_growth > temp_wind_growth:
        #         wind_growth = temp_wind_growth

        if year >= 4:
            diff = year - 4
            plants1 = plants.append(new_gen.iloc[diff], ignore_index=True)
        else:
            plants1 = plants.copy()
        start_net_load = timer()
        net_schedule = net_load(schedule, solar, nuclear, wind, hydro, biomass, power_purchase, year,
                                load_growth, solar_growth, wind_growth, src)
        end_net_load = timer()
        print("Time taken for calculating Net Load ", str(end_net_load - start_net_load), "s")  # Time in seconds

        start_dispatch = timer()
        unmet_df, ramp_req_df = dispatch_sim(plants1, net_schedule, year, src)
        list_unmet_df.append(unmet_df)
        list_ramp_req_df.append(ramp_req_df)
        end_dispatch = timer()
        print("Time taken for dispatch ", str(end_dispatch - start_dispatch), "s")  # Time in seconds
        # list_schedule = []
        # list_unmet = []
        # unmet_df = net_schedule - unmet_df
        # for c in net_schedule.columns.tolist():
        #     list_schedule += net_schedule[c].tolist()
        #     list_unmet += unmet_df[c].tolist()
        # df_load_schedule[str(2021 + year) + "-" + str(22 + year)] = list_schedule
        # df_unmet[str(2021 + year) + "-" + str(22 + year)] = list_unmet

        year += 1
    # return list_unmet_df, list_ramp_req_df, df_load_schedule, df_unmet
    return list_unmet_df, list_ramp_req_df
    # return list_unmet_df, list_unmet_df
