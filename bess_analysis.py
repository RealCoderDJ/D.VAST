import os
from timeit import default_timer as timer

import pandas as pd

from bess import Bess


def analysis(input_values, list_unmet_df, list_ramp_req_df, src):
    bess_size_start, bess_size_end, bess_size_incr = input_values.get_bess_range()
    hour = input_values.get_hours()

    bess_size = bess_size_start

    life, total_cycles, rt_efficiency, degr, scrap_percent, dod = input_values.get_bess_param()
    bess_cost = input_values.get_bess_cost(hour)
    constant_throughput = input_values.get_constant_throughput()

    file_name = "BESS Benefits " + str(total_cycles) + " Cycles " + str(hour) + " Hours " + str(life) + " Years"
    writer = pd.ExcelWriter(file_name + ".xlsx", engine="xlsxwriter")

    size_list = []
    npv_list = []

    while bess_size <= bess_size_end:
        start = timer()
        bess = Bess(bess_cost, bess_size, life, total_cycles, rt_efficiency,
                    hour, degr, scrap_percent, constant_throughput, dod)
        factor = 1
        bess.benefit(input_values, list_unmet_df, list_ramp_req_df, factor, src)
        bess.financial(input_values)
        end = timer()
        print("Time: ", str(end - start))
        df = make_df(bess)
        df.to_excel(writer, sheet_name=str(bess_size) + " MW " + str(hour) + " hour")
        size_list.append(bess_size)
        npv_list.append(bess.npv)

        bess_size += bess_size_incr
    directory = os.path.join(src, "Working Files")
    os.chdir(directory)
    writer.save()

    df_size_npv = pd.DataFrame()
    df_size_npv['Size'] = size_list
    df_size_npv['NPV'] = npv_list

    df_size_npv.set_index('Size', inplace = True)   #TODO remove

    npv_file_name = 'NPV vs Size ' + str(total_cycles) + ' Cycles ' + str(hour) + ' Hours ' + str(life) + ' Years'
    writer1 = pd.ExcelWriter(npv_file_name + ".xlsx", engine="xlsxwriter")
    df_size_npv.to_excel(writer1, sheet_name='Sheet1')
    writer1.save()

    return df_size_npv


def sensitivity_analysis_cost_roe(input_values, list_unmet_df, list_ramp_req_df, size, src):
    hour = input_values.get_hours()
    bess_size = size

    life, total_cycles, rt_efficiency, degr, scrap_percent, dod = input_values.get_bess_param()
    bess_cost = input_values.get_bess_cost(hour)
    constant_throughput = input_values.get_constant_throughput()
    roe, tax_rate = input_values.get_roe_tax()

    initial_roe = roe

    cost = bess_cost - 2525000
    costs = []
    while cost >= 20000000:
        costs.append(cost)
        cost -= 4000000
    roe_list = []
    i = 0
    while i <= 0.07:
        roe_list.append(roe - i)
        i += 0.02
    df_cost_roe = pd.DataFrame()
    df_cost_roe["Cost"] = costs
    df_cost_roe.set_index("Cost", inplace=True)

    start = timer()
    bess = Bess(bess_cost, bess_size, life, total_cycles, rt_efficiency,
                    hour, degr, scrap_percent, constant_throughput, dod)
    factor = 1
    bess.benefit(input_values, list_unmet_df, list_ramp_req_df, factor, src)
    for r in roe_list:
        input_values.set_roe(r)
        list_npv = []
        for c in costs:
            bess.set_cost(c+2525000)
            bess.financial(input_values)
            list_npv.append(bess.npv/10000000)
        df_cost_roe[str(int(r*100)) + "%"] = list_npv

    end = timer()
    input_values.set_roe(initial_roe)
    print("Time: ", str(end - start))

    file_name = "Cost-Roe sensitivity " + str(size) + " MW "+ str(total_cycles) + " Cycles " + str(hour) + " Hours"
    writer = pd.ExcelWriter(file_name + ".xlsx", engine="xlsxwriter")
    df_cost_roe.to_excel(writer)
    directory = os.path.join(src, "Working Files")
    os.chdir(directory)
    writer.save()

    return df_cost_roe


def make_df(bess):
    col = ["Battery Size", "Year", "Charge Cost 1", "Ramp Benefits", "Peak Benefits", "Net Benefits", "No of Cycles",
           "Degradation", "Scrap Value", "Opening Outstanding", "Depreciation", "Closing Outstanding",
           "Interest Payment", "Return on Equity", "Operational Expenses", "Capacity Upgradation Cost", "Total Outflow",
           "Interest on Working Capital", "Capacity Deferral Benefits", "Outage Reduction Benefits",
           "Transmission Loss Reduction", "Net Cash flow", "Final NPV"]
    df = pd.DataFrame()
    df["Battery Size"] = bess.battery_size
    df["Year"] = bess.year
    df["Charge Cost 1"] = bess.charge_cost_1
    df["Ramp Benefits"] = bess.ramp_benefits
    df["Peak Benefits"] = bess.peak_benefits
    df["Net Benefits"] = bess.net_benefits
    df["No of Cycles"] = bess.no_of_cycles
    df["Degradation"] = bess.degr_level
    df["Scrap Value"] = bess.scrap_value
    df["Opening Outstanding"] = bess.open_out_loan
    df["Depreciation"] = bess.depreciation
    df["Loan"] = bess.loan
    df["Closing Outstanding"] = bess.close_out_loan
    df["Interest Payment"] = bess.interest_loan
    df["Return on Equity"] = bess.roe
    df["Operational Expenses"] = bess.opex
    df["Capacity Upgradation Cost"] = bess.capacity_upgrade_cost
    df["Total Outflow"] = bess.total_out_loan
    df["Interest on Working Capital"] = bess.interest_working_capital_loan
    df["Capacity Deferral Benefits"] = bess.capacity_deferral
    df["Outage Reduction Benefits"] = bess.outage_reduction
    df["Transmission Loss Reduction"] = bess.transmission_loss
    df["Net Cash flow"] = bess.net_cash_flow
    df["Final NPV"] = bess.npv_list

    return df
