import os
import pandas as pd
from lc_dispatch import least_cost_dispatch
from bess_analysis import analysis, sensitivity_analysis_cost_roe, sensitivity_analysis_cost
from input import Input

src = r'C:\Users\utkakumar\Documents\Projects\World Bank Battery\codes\D.VAST v0.1.5'
UPLOAD_FOLDER = os.path.join(src, "Uploads Folder")

input_values = Input()

input_values.set_years(15)
input_values.set_growth_rates([6.06, 20, 13])

list_unmet_df, list_ramp_req_df = least_cost_dispatch(UPLOAD_FOLDER, input_values, src)

cycles_list = [4000, 5000, 7000]
# cycles_list = [7000]
hour_list = [1, 2]

cost_df = pd.DataFrame(index=hour_list+['life'], columns=cycles_list)
cost_df.loc[1] = [35000000, 39000000, 41300000]
cost_df.loc[2] = [48500000, 51400000, 54500000]
cost_df.loc['life'] = [10, 12, 15]
# cost_df.loc[1] = [53000000]
# cost_df.loc[2] = [70000000]
# cost_df.loc['life'] = [15]

transmission = [1000000, 2000000]

input_values.rt_efficiency = 0.85
input_values.dod = 0.94
input_values.scrap_percent = 0.1

input_values.set_constant_throughput(0)
input_values.set_bess_range(50, 1000, 50)
input_values.set_discount_rate(8.925)
input_values.set_costs([8.74, 7.13, 3.76, 3.05])
input_values.set_energy_cost_increase(-3)
input_values.set_financial_param(70, 9, 25, 14, 1)
input_values.set_bess_cost_reduction(8)
input_values.set_transformer_param(1300000, 11, 215278, 20)
input_values.set_outage_param(7, 0)


for c in cycles_list:
    for h in hour_list:
        input_values.total_cycles = c
        input_values.set_life(cost_df.loc['life', c])
        input_values.set_hours(h)
        if c < 7000:
            input_values.degr = 0.8
        else:
            input_values.degr = 0.7
        input_values.set_bess_cost(h, cost_df.loc[h, c])
        input_values.set_transmission_reduction([transmission[h-1]])

        df_size_npv = analysis(input_values, list_unmet_df, list_ramp_req_df, src)
        sensitivity_analysis_cost(input_values, list_unmet_df, list_ramp_req_df, src)

        print(str(c) + ' ' + str(h) + ' ' + 'DONE')

#
#
# # size = 20
# #
# #
# # df_size_npv = analysis(input_values, list_unmet_df, src)
# # sensitivity_analysis_cost_roe(input_values, list_unmet_df, size, src)
#
# # directory = os.path.join(src, "Working Files")
# # os.chdir(directory)
# # writer1 = pd.ExcelWriter("Demand.xlsx", engine="xlsxwriter")
# # writer2 = pd.ExcelWriter("Dispatch.xlsx", engine="xlsxwriter")
# #
# # df_load_schedule.to_excel(writer1)
# # df_unmet.to_excel(writer2)
# #
# # writer1.save()
# # writer2.save()
