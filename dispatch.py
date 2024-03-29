import pandas as pd
import numpy as np
import os


def clearing_first_slot_first_day(ic, energy_demand, tech_min, ramp, ramp_time):
    dc = ic
    flag = True
    clearing = dc.copy()
    unmet = 0
    ct = 0
    i = 0
    while i < len(dc) and flag == True:
        clearing_plant = min(dc[ct], energy_demand)
        energy_demand = energy_demand - clearing_plant
        if energy_demand <= 0:
            unmet = energy_demand
            energy_demand = 0
            flag = False
        clearing[ct] = clearing_plant
        ct += 1
        i += 1
    lst = i - 1
    if energy_demand >= 0 and flag == True:
        unmet = energy_demand

    while i < len(dc):
        clearing[i] = 0
        i += 1

    if clearing[lst] < tech_min[lst] * dc[lst]:
        energy_demand = tech_min[lst] * dc[lst] - clearing[lst]
        clearing[lst] = tech_min[lst] * dc[lst]
    flag = True
    i = lst - 1
    while i > 0 and flag == True:
        clearing_plant = max(tech_min[lst] * dc[i], clearing[i] - energy_demand)
        energy_demand = energy_demand - (clearing[i] - clearing_plant)
        if energy_demand <= 0:
            unmet = energy_demand
            flag = True
            energy_demand = 0
        clearing[i] = clearing_plant
        i = i - 1
    flag = True
    i = len(clearing) - 1

    while i > 0 and flag == True:
        if clearing[i] != 0:
            flag = False
        i -= 1
    lra = i + 1  # index of last plant
    return clearing, unmet, lra


def clearing_any_other_slot(ic, energy, new_total_energy_required, previous_energy_clearing, tech_min, ramp, ramp_time):
    dc = ic

    max_energy_rampup = ramp * ramp_time
    max_energy_rampdown = ramp * ramp_time
    flag = True
    unmet = 0
    new_energy_clearing = previous_energy_clearing.copy()
    i = len(previous_energy_clearing) - 1

    "Determining index of plant cleared in previous slot:Start"
    while i > 0 and flag == True:
        if previous_energy_clearing[i] != 0:
            flag = False
        i -= 1
    previous_slot_last_cleared_plant_index = i + 1
    "Determining index of plant cleared in previous slot:Finish"

    for j in range(previous_slot_last_cleared_plant_index + 1):
        cleared_energy_plant = min(new_energy_clearing[j] + max_energy_rampup[j], dc[j])
        max_energy_rampup[j] = max_energy_rampup[j] - (cleared_energy_plant - new_energy_clearing[j])
        max_energy_rampdown[j] = max_energy_rampdown[j] + (cleared_energy_plant - new_energy_clearing[j])
        new_energy_clearing[j] = cleared_energy_plant

    for k in range(j + 1, len(dc)):
        new_energy_clearing[k] = 0
    new_total_energy_temp = sum(new_energy_clearing)
    energy_left = new_total_energy_required - new_total_energy_temp
    if energy_left < 0:  # case of ramp down
        energy_left = abs(energy_left)
        new_last_cleared_plant_index = previous_slot_last_cleared_plant_index

        flag = True
        while new_last_cleared_plant_index >= 0 and flag == True:
            new_clearing_plant_temp = min(max_energy_rampdown[new_last_cleared_plant_index], energy_left)

            new_clearing_plant = max(tech_min[new_last_cleared_plant_index] * dc[new_last_cleared_plant_index],
                                     new_energy_clearing[new_last_cleared_plant_index] - new_clearing_plant_temp)

            energy_left = energy_left - (new_energy_clearing[new_last_cleared_plant_index] - new_clearing_plant)

            max_energy_rampup[new_last_cleared_plant_index] = max_energy_rampup[new_last_cleared_plant_index] + \
                                                              (new_energy_clearing[
                                                                   new_last_cleared_plant_index] - new_clearing_plant)

            max_energy_rampdown[new_last_cleared_plant_index] = max_energy_rampdown[new_last_cleared_plant_index] - \
                                                                (new_energy_clearing[
                                                                     new_last_cleared_plant_index] - new_clearing_plant)

            new_energy_clearing[new_last_cleared_plant_index] = new_clearing_plant
            if energy_left <= 0:
                flag = False  # Exceeded ramp down
                unmet = -energy_left
                energy_left = 0
            new_last_cleared_plant_index = new_last_cleared_plant_index - 1
            if new_last_cleared_plant_index == -1:
                unmet = -energy_left
                energy_left = 0

    elif energy_left > 0:  # case of ramp up
        new_last_cleared_plant_index = previous_slot_last_cleared_plant_index + 1
        flag = True
        while new_last_cleared_plant_index < len(dc) and flag == True:
            new_clearing_plant = max(tech_min[new_last_cleared_plant_index] * dc[new_last_cleared_plant_index],
                                     max_energy_rampup[new_last_cleared_plant_index])
            new_energy_clearing[new_last_cleared_plant_index] = new_clearing_plant
            max_energy_rampup[new_last_cleared_plant_index] = max_energy_rampup[
                                                                  new_last_cleared_plant_index] - new_clearing_plant
            max_energy_rampdown[new_last_cleared_plant_index] = max_energy_rampdown[
                                                                    new_last_cleared_plant_index] + new_clearing_plant
            energy_left = energy_left - new_clearing_plant
            if energy_left < 0:
                flag = False
                energy_left = abs(energy_left)
                while energy_left > 0 and new_last_cleared_plant_index >= 0:
                    new_clearing_plant_temp = min(max_energy_rampdown[new_last_cleared_plant_index], energy_left)
                    new_clearing_plant = max(tech_min[new_last_cleared_plant_index] * dc[new_last_cleared_plant_index],
                                             new_energy_clearing[
                                                 new_last_cleared_plant_index] - new_clearing_plant_temp)
                    energy_left = energy_left - (new_energy_clearing[new_last_cleared_plant_index] - new_clearing_plant)
                    max_energy_rampup[new_last_cleared_plant_index] = max_energy_rampup[
                                                                          new_last_cleared_plant_index] + (
                                                                              new_energy_clearing[
                                                                                  new_last_cleared_plant_index] - new_clearing_plant)
                    max_energy_rampdown[new_last_cleared_plant_index] = max_energy_rampdown[
                                                                            new_last_cleared_plant_index] - (
                                                                                new_energy_clearing[
                                                                                    new_last_cleared_plant_index] - new_clearing_plant)
                    new_energy_clearing[new_last_cleared_plant_index] = new_clearing_plant
                    if energy_left <= 0:
                        flag = False
                        energy_left = 0
                        unmet = -energy_left
                    new_last_cleared_plant_index = new_last_cleared_plant_index - 1
                    if new_last_cleared_plant_index == -1:
                        unmet = -energy_left
                        energy_left = 0
            new_last_cleared_plant_index = new_last_cleared_plant_index + 1
        if energy_left >= 0 and flag == True:
            unmet = energy_left
            energy_left = 0
    flag = True
    i = len(new_energy_clearing) - 1
    while i > 0 and flag == True:
        if new_energy_clearing[i] != 0:
            flag = False
        i -= 1
    new_last_cleared_plant_index = i + 1  # index of last plant
    return new_energy_clearing, unmet, new_last_cleared_plant_index


def dispatch_sim(plants, net_schedule, year, src):
    plants.sort_values(by='VC', inplace=True)
    tech_min = np.asarray(plants['Tech Minimum (%)'])
    ramp = np.asarray(plants['Ramp Rate (MW/min)'])
    ic = np.asarray(plants['DC (MW)'])
    energy = ic * 0

    net_schedule = net_schedule.iloc[:, 0:365]
    net_demand = np.asarray(net_schedule.copy())
    unmet_matrix = np.asarray(net_schedule.copy())
    unmet_matrix *= 0

    ramp_time = (24 * 60) / len(net_schedule.index)

    for day in range(net_schedule.columns.size):
        for slot in range(net_schedule.index.size):
            if day == 0 and slot == 0:
                last_cl, unmet, last_plant = clearing_first_slot_first_day(ic, net_demand[slot, day],
                                                                           tech_min, ramp, ramp_time)
                unmet_matrix[slot, day] = unmet

            else:
                last_cl, unmet, last_plant = clearing_any_other_slot(ic, energy, net_demand[slot, day], last_cl,
                                                                     tech_min, ramp, ramp_time)
                unmet_matrix[slot, day] = unmet

    # -------------------------------------------DJ------------------------------------------------------#
    # To generate the maximum possible ramp up capacity when the demand exceeds the generation
    net_demand_adapted_for_max_generation = net_demand.copy()  # Copy net_demand to keep the original file intact
    generation_power_availability_for_supply = 1  # To denote the ratio of power available to power generated
    generation_matrix = net_demand_adapted_for_max_generation - unmet_matrix  # Total demand matrix
    max_generation = generation_power_availability_for_supply * sum(ic)

    # Limiting new demand so that only max generation capacity can be the maximum demand
    net_demand_adapted_for_max_generation[net_demand_adapted_for_max_generation > max_generation] = max_generation
    generation_matrix[generation_matrix > max_generation] = max_generation  # Nirmal Addition

    # Total ramp up required to reach the max generation capacity
    ramp_up_matrix = net_demand_adapted_for_max_generation - generation_matrix

    # Procedures to store the ramp up data in a new sheet of the excel workbook
    ramp_up_matrix_df = pd.DataFrame(ramp_up_matrix)
    ramp_up_matrix_df.columns = net_schedule.columns
    ramp_up_matrix_df.index = net_schedule.index

    os.chdir(os.path.join(src, "Working Files"))
    writer = pd.ExcelWriter("Ramp_up_" + str(year + 1) + ".xlsx", engine="xlsxwriter")
    ramp_up_matrix_df.to_excel(writer, sheet_name="sheet2")
    writer.save()
    # ---------------------------------------------DJ-------------------------------------------------------#

    unmet_df = pd.DataFrame(unmet_matrix)
    unmet_df.columns = net_schedule.columns
    unmet_df.index = net_schedule.index

    os.chdir(os.path.join(src, "Working Files"))
    writer = pd.ExcelWriter("Unmet_" + str(year + 1) + ".xlsx", engine="xlsxwriter")
    unmet_df.to_excel(writer, sheet_name="sheet1")
    writer.save()

    return unmet_df, ramp_up_matrix_df
