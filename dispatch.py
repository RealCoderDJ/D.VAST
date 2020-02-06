import pandas as pd
import numpy as np
import os


def maximum_minimum_gen(ic, tech_min, previous_clearing, ramp, ramp_time, plant_type, energy_year, total_slots_left,
                        new_total_energy_required, net_demand_old, first_slot):
    dc = ic.copy()
    maximum_gen = ic.copy() * 0
    minimum_gen = ic.copy() * 0

    ramping = ramp * ramp_time
    technical_min = tech_min * dc

    if first_slot:
        for p in range(len(plant_type)):
            if plant_type[p] == "GAS":
                dc[p] = 5 * energy_year[p] / total_slots_left

        maximum_gen = dc.copy()
        minimum_gen = technical_min

    else:
        if new_total_energy_required < 0 or net_demand_old < 0:
            demand_change = -1
        else:
            demand_change = (new_total_energy_required - net_demand_old) / net_demand_old
        energy_slot = energy_year / total_slots_left
        for p in range(len(plant_type)):
            if plant_type[p] == "GAS":
                if demand_change <= -1:
                    demand_change = -1
                dc[p] = min(5 * energy_slot[p] * (1 + demand_change), ic[p])

            maximum_gen[p] = min(dc[p], max(previous_clearing[p] + ramping[p], technical_min[p]))
            minimum_gen[p] = max(technical_min[p], previous_clearing[p] - ramping[p])

    return maximum_gen, minimum_gen, sum(dc)  # Total maximum gen in slot


def clearing(maximum_gen, minimum_gen, energy_demand, plant_type, energy_year, time_per_slot, previous_last_plant_index):
    clearing = maximum_gen.copy() * 0
    unmet = 0
    i = 0

    # ---------Dispatch Starts ---------------------------------------#
    # dispatching upto demand or maximum gen, whichever minimum
    while i < len(maximum_gen):
        clearing_plant = min(maximum_gen[i], energy_demand)
        clearing[i] = clearing_plant
        energy_demand -= clearing_plant
        if energy_demand <= 0:  # if demand is met
            unmet = 0
            energy_demand = 0
            break
        i += 1

    index_last = max(i, previous_last_plant_index)

    if energy_demand > 0:  # if demand greater than total Gen
        unmet = energy_demand

    else:
        # if last plant gen is less than min generation
        if clearing[index_last] < minimum_gen[index_last]:
            balance = minimum_gen[index_last] - clearing[index_last]
            clearing[index_last] = minimum_gen[index_last]

            j = index_last - 1
            while j >= 0:  # reducing balance from previous plants upto min of each
                clearing_plant = max(minimum_gen[j], (clearing[j] - balance))
                balance -= clearing[j] - clearing_plant
                clearing[j] = clearing_plant
                if balance <= 0:  # demand met
                    unmet = 0
                    balance = 0
                    break
                j -= 1

            if balance > 0:  # excess generation
                unmet = - balance
    # ---------Dispatch Ends ---------------------------------------#

    # index of last dispatched plant
    last_plant_index = len(clearing) - 1
    while last_plant_index >= 0:
        if clearing[last_plant_index] > 0:
            #            last_plant_index += 1
            break
        last_plant_index -= 1

    if last_plant_index < 0:
        last_plant_index = 0

    # reducing energy dispatched by gas plants
    for p in range(len(maximum_gen)):
        if plant_type[p] == "GAS":
            if clearing[p] != 0:
                energy_year[p] = energy_year[p] - clearing[p] * time_per_slot
                if energy_year[p] < 0:
                    energy_year[p] = 0

    return clearing, unmet, energy_year, last_plant_index


def dispatch_sim(plants, net_schedule, year, src):

    plants.sort_values(by='VC', inplace=True)
    tech_min = np.asarray(plants['Tech Minimum (%)'])
    ramp = np.asarray(plants['Ramp Rate (MW/min)'])
    ic = np.asarray(plants['DC (MW)'])
    plant_type = np.asarray(plants["Type"])
    energy_year = np.asarray(plants["Energy (MWh)"])

    net_schedule = net_schedule.iloc[:, 0:365]
    net_demand = np.asarray(net_schedule.copy())
    unmet_matrix = np.asarray(net_schedule.copy())
    unmet_matrix *= 0
    ramp_matrix_gas = unmet_matrix.copy()

    ramp_time = (24 * 60) / len(net_schedule.index)
    total_slots_left = 365 * len(net_schedule.index)
    time_per_slot = 24 / len(net_schedule.index)

    net_demand_old = 0
    previous_clearing = ic * 0

    first_slot = True
    previous_last_plant_index = 0

    for day in range(np.shape(net_demand)[1]):
        for slot in range(np.shape(net_demand)[0]):

            maximum_gen, minimum_gen, total_dc = maximum_minimum_gen(ic, tech_min, previous_clearing, ramp, ramp_time,
                                                                     plant_type, energy_year, total_slots_left,
                                                                     net_demand[slot, day], net_demand_old, first_slot)
            first_slot = False

            previous_clearing, unmet, energy_year, previous_last_plant_index = clearing(maximum_gen, minimum_gen,
                                                                                        net_demand[slot, day],
                                                                                        plant_type, energy_year,
                                                                                        time_per_slot,
                                                                                        previous_last_plant_index)

            unmet_matrix[slot, day] = unmet
            total_slots_left = total_slots_left - 1
            #
            net_demand_old = net_demand[slot, day]
            if unmet > 0:
                ramp_matrix_gas[slot, day] = max(min(net_demand[slot, day], total_dc) - sum(previous_clearing), 0)
            else:
                ramp_matrix_gas[slot, day] = 0


            # Procedures to store the ramp up data in a new sheet of the excel workbook
    ramp_up_matrix_df = pd.DataFrame(ramp_matrix_gas)
    ramp_up_matrix_df.columns = net_schedule.columns
    ramp_up_matrix_df.index = net_schedule.index

    os.chdir(os.path.join(src, "Working Files"))
    writer = pd.ExcelWriter("Ramp_up_" + str(year + 1) + ".xlsx", engine="xlsxwriter")
    ramp_up_matrix_df.to_excel(writer, sheet_name="sheet2")
    writer.save()

    unmet_df = pd.DataFrame(unmet_matrix)
    unmet_df.columns = net_schedule.columns
    unmet_df.index = net_schedule.index

    os.chdir(os.path.join(src, "Working Files"))
    writer = pd.ExcelWriter("Unmet_" + str(year + 1) + ".xlsx", engine="xlsxwriter")
    unmet_df.to_excel(writer, sheet_name="sheet1")
    writer.save()

    return unmet_df, ramp_up_matrix_df


