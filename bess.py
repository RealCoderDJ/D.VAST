import pandas as pd
import numpy as np
import os
import math


class Bess:

    def __init__(self, bess_cost, bess_size, life, total_cycles, rt_efficiency, hr, degr, scrap, constant_throughput,
                 dod):

        self.ramp_up_start_cycle = 0
        self.ramp_up_start_time = 0
        self.ramp_up_time = 0
        self.size = bess_size
        self.cost = bess_cost
        self.life = life
        self.cycles = total_cycles
        self.rt_efficiency = rt_efficiency
        self.discharge_period = hr
        self.degradation = degr
        self.scrap_percent = scrap
        self.constant_throughput = constant_throughput
        self.dod = dod
        self.bess_cost_reduction = 0.1
        self.battery_size = np.zeros(life)
        self.year = np.zeros(life)
        self.charge_cost_1 = np.zeros(life)
        self.ramp_benefits = np.zeros(life)
        self.peak_benefits = np.zeros(life)
        self.net_benefits = np.zeros(life)
        self.no_of_cycles = np.zeros(life)
        self.degr_level = np.zeros(life)
        self.scrap_value = np.zeros(life)
        self.open_out = np.zeros(life)
        self.open_out_loan = np.zeros(life)
        self.depreciation = np.zeros(life)
        self.close_out = np.zeros(life)
        self.loan = np.zeros(life)
        self.close_out_loan = np.zeros(life)
        self.interest = np.zeros(life)
        self.interest_loan = np.zeros(life)
        self.roe = np.zeros(life)
        self.opex = np.zeros(life)
        self.capacity_upgrade_cost = np.zeros(life)
        self.total_out = np.zeros(life)
        self.total_out_loan = np.zeros(life)
        self.interest_working_capital = np.zeros(life)
        self.interest_working_capital_loan = np.zeros(life)
        self.capacity_deferral = np.zeros(life)
        self.outage_reduction = np.zeros(life)
        self.transmission_loss = np.zeros(life)
        self.net_cash_flow = np.zeros(life)
        self.npv_list = np.zeros(life)
        self.npv = 0

    def set_cost(self, bess_cost):
        self.cost = bess_cost

    def benefit_morning_evening_discharge(self, input_value, list_unmet_df, list_ramp_req_df, df_peak_cost, src):
        life = self.life
        rt_efficiency = self.rt_efficiency
        hr = self.discharge_period
        dod = self.dod
        energy_cost_increase = input_value.get_energy_cost_increase()
        costs = input_value.get_costs()

        os.chdir(os.path.join(src, "Working Files"))
        writer = pd.ExcelWriter("Result BESS" + str(self.size) + "_" + str(hr) + "hr " + str(self.cycles) + ".xlsx",
                                engine="xlsxwriter")
        print("BESS: ", str(self.size), "MW /", str(self.size * hr), "MWh")

        # ramp_up_start_time, ramp_up_end_time = input_value.get_ramp_up_time_selection()

        charge_left_first = 0
        cycles_run = 0
        change_year = int(life * 515 - self.cycles) / 150
        cycles_left = self.cycles
        for year in range(1, life + 1):
            rem_cycles = self.cycles - cycles_run
            if self.constant_throughput == 0:
                degr = self.degradation + ((rem_cycles / self.cycles) * (1 - self.degradation))
                bess_size = degr * self.size * dod
            else:
                bess_size = self.size * dod

            if year > change_year:
                no_of_cycles = int(rem_cycles / (life - year + 1))
            else:
                no_of_cycles = 365

            dsm_cost = costs[0]
            if year < 8:                # Todo change: add variable
                late_night_cost_average = costs[2] * (energy_cost_increase ** (year - 1))  # 3.44
                evening_cost_average = costs[3] * (energy_cost_increase ** (year - 1))  # 2.788 vc_exec
            else:
                late_night_cost_average = costs[2] * (energy_cost_increase ** 7) * (0.95 ** (year - 7))
                evening_cost_average = costs[3] * (energy_cost_increase ** 7) * (0.95 ** (year - 7))

            df_ramp = list_ramp_req_df[year - 1]
            df_excess = list_unmet_df[year - 1]
            df_excess = df_excess[df_excess < 0]
            df_excess.fillna(0, inplace=True)

            # slots_per_hour = len(df_ramp.index) / 24
            slots_per_hour = 4

            ramp_matrix = np.asarray(df_ramp)
            excess_matrix = np.asarray(df_excess)
            peak_cost_matrix = np.asarray(df_peak_cost) * (1.03 ** (year - 1))  # TODO add variable

            # converting to np and slicing
            total_slots = np.shape(ramp_matrix)[0]

            # ramp_up_start_cycle = int((ramp_up_start_time * total_slots / 24) - 1)
            # ramp_up_end_cycle = int((ramp_up_end_time * total_slots / 24) - 1)

            ramp_morning = ramp_matrix.copy()[:slots_per_hour * 12]
            ramp_evening = ramp_matrix.copy()[slots_per_hour * 12: (total_slots - slots_per_hour * hr)]
            excess = excess_matrix.copy()[slots_per_hour * 8:slots_per_hour * 18]
            peak_cost_morning = peak_cost_matrix.copy()[:slots_per_hour * 8]
            peak_cost_evening = peak_cost_matrix.copy()[slots_per_hour * 18: (total_slots - slots_per_hour * hr)]
            # excess = excess_matrix.copy()[ramp_up_start_cycle: ramp_up_end_cycle]
            # peak_cost_morning = peak_cost_matrix.copy()[:ramp_up_start_cycle]
            # peak_cost_evening = peak_cost_matrix.copy()[ramp_up_end_cycle: (total_slots - slots_per_hour * hr)]

            # limiting energy in a slot to capacity
            ramp_morning[ramp_morning > bess_size] = bess_size
            ramp_morning[ramp_morning < 0.001] = 0
            ramp_evening[ramp_evening > bess_size] = bess_size
            ramp_evening[ramp_evening < 0.001] = 0

            excess[excess < -bess_size] = -bess_size  # Excess is negative
            excess[excess > -0.001] = 0

            # converting to energy in each slice and limiting to total battery energy
            ramp_energy_morning = ramp_morning.sum(0) / slots_per_hour
            ramp_energy_evening = ramp_evening.sum(0) / slots_per_hour
            excess_energy = excess.sum(0) / slots_per_hour

            ramp_energy_morning[ramp_energy_morning > bess_size * hr] = bess_size * hr
            ramp_energy_evening[ramp_energy_evening > bess_size * hr] = bess_size * hr
            excess_energy[excess_energy < -(bess_size * hr) / rt_efficiency] = -(bess_size * hr) / rt_efficiency

            # average cost of the highest slots where peak plant is running
            peak_cost_morning_idx = peak_cost_morning.argsort(axis=0)
            peak_cost_morning_ascending = peak_cost_morning[
                peak_cost_morning_idx, np.arange(peak_cost_morning_idx.shape[1])]
            peak_cost_evening_idx = peak_cost_evening.argsort(axis=0)
            peak_cost_evening_ascending = peak_cost_evening[
                peak_cost_evening_idx, np.arange(peak_cost_evening_idx.shape[1])]

            peak_cost_morning_average = peak_cost_morning_ascending[-(hr * slots_per_hour):, :].mean(0)
            peak_cost_evening_average = peak_cost_evening_ascending[-(hr * slots_per_hour):, :].mean(0)

            ####-----------------------------------NEW RAMP + ENERGY-----------------------------------------------------

            arbitrage_energy_morning = bess_size * hr - ramp_energy_morning
            arbitrage_energy_evening = bess_size * hr - ramp_energy_evening
            arbitrage_energy_morning[arbitrage_energy_morning < 0.001] = 0
            arbitrage_energy_evening[arbitrage_energy_evening < 0.001] = 0
            arbitrage_energy_morning[arbitrage_energy_morning > (min(bess_size, 500) * hr)] = (min(bess_size, 500) * hr)
            arbitrage_energy_evening[arbitrage_energy_evening > (min(bess_size, 500) * hr)] = (min(bess_size, 500) * hr)

            required_energy_morning = ramp_energy_morning + arbitrage_energy_morning
            required_energy_evening = ramp_energy_evening + arbitrage_energy_evening

            cost_morning = dsm_cost * ramp_energy_morning + peak_cost_morning_average * arbitrage_energy_morning
            cost_evening = dsm_cost * ramp_energy_morning + peak_cost_evening_average * arbitrage_energy_evening

            ####-----------------------------------NEW------------------------------------------------------------

            # checking if ramping or energy arbitrage is more beneficial
            # bool_morning = (dsm_cost * ramp_energy_morning) / (min(bess_size, 500) * hr) > peak_cost_morning_average    # TODO 500 to be input
            # bool_morning_int = bool_morning.astype(int)
            # bool_morning_int_inverted = np.invert(bool_morning).astype(int)
            # bool_evening = (dsm_cost * ramp_energy_evening) / (min(bess_size, 500) * hr) > peak_cost_evening_average    # TODO 500 to be input
            # bool_evening_int = bool_evening.astype(int)
            # bool_evening_int_inverted = np.invert(bool_evening).astype(int)
            #
            # ramp_energy_morning *= bool_morning_int
            # ramp_energy_evening *= bool_evening_int
            #
            # available_arbitrage_morning_cost = bool_morning_int_inverted * peak_cost_morning_average
            # available_arbitrage_evening_cost = bool_evening_int_inverted * peak_cost_evening_average
            #
            # # making array of costs and energy required in morning and evening
            # cost_morning = dsm_cost * bool_morning_int + available_arbitrage_morning_cost
            # cost_evening = dsm_cost * bool_evening_int + available_arbitrage_evening_cost
            #
            # bool_int_morning_requirement = cost_morning.copy()
            # bool_int_evening_requirement = cost_evening.copy()
            #
            # bool_int_morning_requirement[bool_int_morning_requirement > 0] = 1  # days where requirement is there
            # bool_int_evening_requirement[bool_int_evening_requirement > 0] = 1
            #
            # required_energy_morning = ramp_energy_morning + (min(bess_size, 500) * hr) * bool_morning_int_inverted  # TODO 500 to be input
            # required_energy_evening = ramp_energy_evening + (min(bess_size, 500) * hr) * bool_evening_int_inverted
            #
            # required_energy_morning *= bool_int_morning_requirement
            # required_energy_evening *= bool_int_evening_requirement
            #
            # bool_required_energy_day = (required_energy_morning + required_energy_evening).copy()
            # bool_required_energy_day[bool_required_energy_day > 0] = 1

            # choose most beneficial days
            # costs_1 = cost_morning * required_energy_morning
            # costs_2 = cost_evening * required_energy_evening

            costs_1 = cost_morning.copy()                                               # NEW
            costs_2 = cost_evening.copy()

            costs_both = np.append(costs_1, costs_2)
            costs_required = np.argsort(np.argsort(costs_both))
            costs_required[costs_required < (len(costs_required) - no_of_cycles)] = 0
            costs_required[costs_required > 0] = 1
            costs_1 = costs_required[: 365]
            costs_2 = costs_required[365:]

            required_energy_morning *= costs_1
            required_energy_evening *= costs_2

            cost_morning *= costs_1
            cost_evening *= costs_2

            # charging energy and cost arrays
            charge_morning = np.append(required_energy_morning.copy() * 0, 0)
            charge_evening = required_energy_evening.copy() * 0
            charge_morning_paid = charge_morning.copy()
            charge_evening_paid = charge_evening.copy()

            charge_morning[0] = charge_left_first
            for i in range(len(charge_evening)):
                charge_left_morning = max(charge_morning[i] - required_energy_morning[i] / rt_efficiency, 0)
                excess_energy_evening = min(((-1 * excess_energy[i]) + charge_left_morning),
                                            (bess_size * hr) / rt_efficiency)
                charge_evening[i] = max(excess_energy_evening, required_energy_evening[i] / rt_efficiency)
                charge_left_evening = charge_evening[i] - required_energy_evening[i] / rt_efficiency

                if i < (len(charge_evening) - 1):
                    charge_morning[i + 1] = max(charge_left_evening, required_energy_morning[i + 1] / rt_efficiency)
                else:
                    charge_morning[i + 1] = charge_left_evening

                charge_evening_paid[i] = charge_evening[i] - excess_energy_evening
                charge_morning_paid[i + 1] = charge_morning[i + 1] - charge_left_evening

            charge_left_first = charge_morning[len(charge_morning) - 1]
            charge_morning = charge_morning[:-1]
            charge_morning_paid = charge_morning_paid[:-1]

            charging_cost_morning = charge_morning_paid * late_night_cost_average * 1000
            charging_cost_evening = charge_evening_paid * evening_cost_average * 1000

            # benefit_morning = required_energy_morning * cost_morning * 1000
            # benefit_evening = required_energy_evening * cost_evening * 1000

            benefit_morning = cost_morning * 1000       # NEW
            benefit_evening = cost_evening * 1000

            cycles_run_year = sum(required_energy_morning + required_energy_evening) / (bess_size * hr)
            cycles_run += cycles_run_year

            # ramp_benefit = (benefit_morning * bool_morning_int).sum() + (benefit_evening * bool_evening_int).sum()
            # peak_benefit = (benefit_morning * bool_morning_int_inverted).sum() \
            #                + (benefit_evening * bool_evening_int_inverted).sum()

            ramp_benefit = 1000 * sum(dsm_cost * (ramp_energy_morning * costs_1 + ramp_energy_evening * costs_2))  #NEW
            peak_benefit = 1000 * (sum(peak_cost_morning_average * arbitrage_energy_morning * costs_1) \
                           + sum(peak_cost_evening_average * arbitrage_energy_evening * costs_2))

            df = pd.DataFrame()
            df['Charging Cost LN'] = [late_night_cost_average] * len(cost_morning)
            df['Charge LN'] = charge_morning
            df['Charge Late Night Paid'] = charge_morning_paid
            df['Morning Sell Price'] = cost_morning
            df['Energy Req Morning'] = required_energy_morning
            df['Excess'] = excess_energy
            df['Charging Cost Ev'] = [evening_cost_average] * len(charge_evening)
            df['Charge EV'] = charge_evening
            df['Charge Evening Paid'] = charge_evening_paid
            df['Evening Sell Price'] = cost_evening
            df['Energy Req Evening'] = required_energy_evening
            df['Total Charge Morn'] = charging_cost_morning
            df['Total Charge Eve'] = charging_cost_evening
            df['Total Sell Morn'] = benefit_morning
            df['Total Sell Even'] = benefit_evening
            df['Ramp Energy Morning'] = ramp_energy_morning * costs_1
            df['Arbitrage Energy Morning'] = arbitrage_energy_morning* costs_1
            df['Ramp Energy Evening'] = ramp_energy_evening * costs_2
            df['Arbitrage Energy Evening'] = arbitrage_energy_evening * costs_2
            df['Benefits'] = benefit_morning + benefit_evening - charging_cost_morning - charging_cost_evening
            df.index = df_ramp.columns

            df.to_excel(writer, sheet_name="Year_" + str(year))

            cycles_left -= cycles_run_year
            degr = self.degradation + ((cycles_left / self.cycles) * (1 - self.degradation))
            if self.constant_throughput != 0:
                cycles_left = self.cycles

            # ["Battery Size", "Year", "Charge Cost 1", "Ramp Benefits", "Peak Benefits", 'Net Benefits",
            # "No of Cycles", "Degradation", "Scrap Value"]
            self.battery_size[year - 1] = self.size
            self.year[year - 1] = year
            self.charge_cost_1[year - 1] = charging_cost_morning.sum() + charging_cost_evening.sum()
            self.ramp_benefits[year - 1] = ramp_benefit
            self.peak_benefits[year - 1] = peak_benefit
            self.net_benefits[year - 1] = self.peak_benefits[year - 1] + self.ramp_benefits[year - 1] \
                                          - self.charge_cost_1[year - 1]
            self.no_of_cycles[year - 1] = cycles_run_year
            self.degr_level[year - 1] = degr

            if year == life:
                if self.constant_throughput == 0:
                    scrap_val = self.cost * self.size * self.scrap_percent
                    self.scrap_value[year - 1] = scrap_val
                else:
                    scrap_val = self.compute_scrap_value(cycles_run_year, input_value, energy_cost_increase)
                    self.scrap_value[year - 1] = scrap_val
            else:
                self.scrap_value[year - 1] = 0

        writer.save()

    def benefit(self, input_value, list_unmet_df, list_ramp_req_df, factor, src):

        life = self.life
        rt_efficiency = self.rt_efficiency
        hr = self.discharge_period
        dod = self.dod
        energy_cost_increase = input_value.get_energy_cost_increase()
        costs = input_value.get_costs()
        add_cycles = self.cycles - (365 * life)

        os.chdir(os.path.join(src, "Working Files"))

        writer = pd.ExcelWriter("Result BESS" + str(self.size) + "_" + str(hr) + "hr " + str(self.cycles) + ".xlsx",
                                engine="xlsxwriter")
        print("BESS: ", str(self.size), "MW /", str(self.size * hr), "MWh")
        rem_cycles = self.cycles
        cycles_left_at_eol = self.cycles
        for year in range(1, life + 1):
            total_size = self.size
            if self.constant_throughput == 0:
                degr = self.degradation + ((rem_cycles / self.cycles) * (1 - self.degradation))
                bess_size = degr * self.size
            else:
                bess_size = self.size

            print("Year", str(year))
            df_delta = list_unmet_df[year - 1]
            df_delta_ramp = list_ramp_req_df[year - 1]
            if "Sno" in df_delta.columns:
                df_delta.drop("Sno", axis=1, inplace=True)
                df_delta_ramp.drop("Sno", axis=1, inplace=True)
            df_delta["Slot"] = [f for f in range(1, 97)]
            df_delta.set_index("Slot", inplace=True)
            df_delta_ramp["Slot"] = [f for f in range(1, 97)]
            df_delta_ramp.set_index("Slot", inplace=True)
            columns_df = df_delta.columns.tolist()

            no_time_slots = len(df_delta.index)
            energy_per_time = 24 / no_time_slots

            df_delta = np.asarray(df_delta)  # Change to NumPy array
            df_delta_ramp = np.asarray(df_delta_ramp)

            dsm = costs[0] * (energy_cost_increase ** (year - 1))
            vc_peak = costs[1] * (energy_cost_increase ** (year - 1))
            vc_min = costs[2] * (energy_cost_increase ** (year - 1))
            vc_exc = costs[3] * (energy_cost_increase ** (year - 1))

            # # Only for No increase in Market Price
            # dsm = costs[0]
            # vc_peak = costs[1] * (energy_cost_increase ** (year - 1))
            # vc_min = costs[2]
            # vc_exc = costs[3]

            # ---------------------------------------DJ--------------------------------------------------------#
            # Using the ramp-up start time and end time to evaluate the time slots that needs to be selected

            # Calling the function to calculate the cycle of ramp up peak

            ramp_up_start_time, ramp_up_end_time = input_value.get_ramp_up_time_selection()

            ramp_up_start_cycle = int((ramp_up_start_time * no_time_slots / 24) - 1)
            ramp_up_end_cycle = int((ramp_up_end_time * no_time_slots / 24) - 1)

            df_eve = df_delta_ramp.copy()[ramp_up_start_cycle:ramp_up_end_cycle]
            df_morn = df_delta.copy()[int((5 * no_time_slots / 24) - 1):
                                      int(math.floor((ramp_up_start_cycle + ramp_up_end_cycle) / 2))]

            # ----------------------------------------DJ---------------------------------------------------- #

            df_morn[df_morn > 0] = 0
            df_morn[df_morn < -(bess_size * dod)] = -(bess_size * dod)
            df_eve[df_eve < 0] = 0
            df_eve[df_eve > (bess_size * dod)] = (bess_size * dod)

            df = pd.DataFrame(columns=columns_df)
            df.loc["Avl Charging (MWh)"] = abs(df_morn.sum(
                0) * energy_per_time)  # Total charging energy in MWh #df_morn.sum(0) * 0.25---->df_morn.sum(0)
            df.loc["Ramp req (MWh)"] = df_eve.sum(
                0) * energy_per_time  # Total ramp req energy in MWh #df_eve.sum(0) * 0.25------>df_eve.sum(0)
            df.loc["Charge 1 cost (Rs.)"] = [0] * len(columns_df)  # Charging Cost 1
            df.loc["Ramp Benefit (Rs.)"] = [0] * len(columns_df)
            df.loc["Peak Benefit (Rs.)"] = [0] * len(columns_df)

            charge_1 = np.asarray(df.loc["Avl Charging (MWh)"].copy())
            charge_1[charge_1 < hr * ((bess_size * dod) / rt_efficiency)] = -1
            charge_1[charge_1 >= hr * ((bess_size * dod) / rt_efficiency)] = 0  # Making charge cost 0 if
            # sufficient surplus avl
            charge_1 = abs(charge_1)

            ramp_req = np.asarray(df.loc["Ramp req (MWh)"].copy())
            ramp_req[ramp_req > hr * (bess_size * dod)] = hr * (bess_size * dod)  # equal to total BESS energy
            ramp_req[ramp_req < (factor * hr * (bess_size * dod) * (vc_peak / dsm))] = 0  # If peak benefits > ramp
            # benefits, make 0

            ramp_req_count = ramp_req.copy()
            ramp_energy = ramp_req.sum() * 1000  # total ramp energy in kWh
            ramp_req_count[ramp_req_count > 0] = 1
            days_w_ramp_req = ramp_req_count.sum()

            cycles_req = min(days_w_ramp_req, max(add_cycles, 0))
            ramp_energy *= cycles_req / days_w_ramp_req
            unrequired_charge_energy = cycles_req * hr * (bess_size * dod) * 1000 - ramp_energy

            add_cycles -= cycles_req
            rem_cycles -= (cycles_req + 365)
            cycles_left_at_eol -= (cycles_req + 365)

            addn_benefits = (bess_size * dod) * hr * 1000 * cycles_req * (vc_peak - vc_min / rt_efficiency)
            addn_benefits += unrequired_charge_energy * vc_min / rt_efficiency  # adding back unnecessary charging cost

            df.loc["Additional Benefit"] = [addn_benefits] + [0] * 364

            df.loc["Charge 1 cost (Rs.)"] = charge_1 * vc_exc * hr * ((bess_size * dod) / rt_efficiency) * 1000
            df.loc["Ramp Benefit (Rs.)"] = dsm * ramp_req * 1000
            d_temp = np.asarray(df.loc["Ramp Benefit (Rs.)"].copy())
            d_temp[d_temp > 0] = -1
            d_temp[d_temp == 0] = 1
            d_temp[d_temp == -1] = 0
            df.loc["Peak Benefit (Rs.)"] = vc_peak * hr * (bess_size * dod) * 1000 * d_temp

            df.to_excel(writer, sheet_name="Year_" + str(year))
            total = np.asarray(df).sum(1)

            degr = self.degradation + ((rem_cycles / self.cycles) * (1 - self.degradation))
            if self.constant_throughput != 0:
                rem_cycles = self.cycles

            # ["Battery Size", "Year", "Charge Cost 1", "Ramp Benefits", "Peak Benefits", 'Net Benefits",
            # "No of Cycles", "Degradation", "Scrap Value"]
            self.battery_size[year - 1] = total_size
            self.year[year - 1] = year
            self.charge_cost_1[year - 1] = total[2]
            self.ramp_benefits[year - 1] = total[3]
            self.peak_benefits[year - 1] = total[4] + total[5]
            self.net_benefits[year - 1] = self.peak_benefits[year - 1] + self.ramp_benefits[year - 1] \
                                          - self.charge_cost_1[year - 1]
            self.no_of_cycles[year - 1] = (365 + cycles_req)
            self.degr_level[year - 1] = degr

            if year == life:
                if self.constant_throughput == 0:
                    scrap_val = self.cost * self.size * self.scrap_percent
                    self.scrap_value[year - 1] = scrap_val
                else:
                    scrap_val = self.compute_scrap_value((cycles_req + 365), input_value, energy_cost_increase)
                    self.scrap_value[year - 1] = scrap_val
            else:
                self.scrap_value[year - 1] = 0
        writer.save()
        if add_cycles > 0:
            factor -= 0.1
            print(factor)
            self.benefit(input_value, list_unmet_df, list_ramp_req_df, factor, src)

    def compute_scrap_value(self, cycles_done, input_value, energy_cost_increase):
        degradation = cycles_done * (1 - self.degradation) / self.cycles
        cycles_remaining = self.cycles - cycles_done
        scrap_benefit = np.zeros(math.ceil(cycles_remaining / 365) + 1)
        year = self.life
        costs = input_value.get_costs()
        while cycles_remaining > 0:
            cycles_run = min(365, cycles_remaining)
            vc_peak = costs[1] * (energy_cost_increase ** year)

            scrap_benefit[year - self.life + 1] = self.size * self.dod * (
                    1 - degradation) * self.discharge_period * 1000 * cycles_run * vc_peak

            degradation += cycles_run * (1 - self.degradation) / self.cycles
            cycles_remaining -= cycles_run

            if cycles_remaining <= 0:
                scrap_benefit[year - self.life + 1] += self.cost * self.size * self.scrap_percent

            year += 1
        discount_rate = input_value.get_discount_rate()
        npv = np.npv(discount_rate, scrap_benefit)
        return npv

    def financial(self, input_values):
        life, total_cycles, rt_efficiency, degr, scrap_percent, dod = input_values.get_bess_param()
        discount_rate = input_values.get_discount_rate()
        loan_percent, interest_rate, roe, op_ex = input_values.get_financial_param()
        transmission_loss = input_values.get_transmission_reduction(self.discharge_period)
        energy_cost_increase = input_values.get_energy_cost_increase()
        energy_cost_increase = 1.03     # TODO Change this, add variable
        transformer_cost, transformer_interest, land_cost, trans_land_req = input_values.get_transformer_param()
        average_tariff, total_outage = input_values.get_outage_param()
        avg_energy_cost = input_values.get_costs()[2]

        temp_opening_bal = (self.cost * loan_percent * self.battery_size) - ((self.year - 1) * self.cost
                                                                             * self.battery_size
                                                                             * (1 - scrap_percent) / life)
        temp_opening_bal[temp_opening_bal < 0] = 0
        self.open_out = temp_opening_bal.copy()
        temp_opening_bal_loan = self.cost * loan_percent * self.battery_size * (life + 1 - self.year) / (life - 1)
        for i in range(len(temp_opening_bal_loan)):
            if temp_opening_bal_loan[i] > (self.cost * loan_percent * self.battery_size[i]):
                temp_opening_bal_loan[i] = self.cost * loan_percent * self.battery_size[i]
        # temp_opening_bal_loan[temp_opening_bal_loan > (self.cost * loan_percent * self.battery_size)] = (self.cost
        #                                                                            * loan_percent) * self.battery_size
        self.open_out_loan = temp_opening_bal_loan

        self.depreciation = self.cost * self.size * (1 - scrap_percent) / self.life
        temp_closing = self.open_out - self.depreciation
        temp_closing[temp_closing < 0] = 0
        self.close_out = temp_closing.copy()

        # temp_outstanding = (self.cost * loan_percent) * self.battery_size * (self.life - self.year) / (self.life - 1)
        # temp_outstanding[temp_outstanding < 0] = 0
        # self.loan = self.open_out - temp_outstanding
        if self.life == 15:     # TODO
            self.loan = (self.cost * loan_percent) * self.battery_size / (self.life - 2)
            self.loan[len(self.loan)-1] = 0
        else:
            self.loan = (self.cost * loan_percent) * self.battery_size / (self.life - 1)
        self.loan[0] = 0  # Monetorium
        self.close_out_loan = self.open_out_loan - self.loan
        self.close_out_loan[self.close_out_loan < 0] = 0

        self.interest = (self.open_out + self.close_out) * interest_rate / 2
        self.interest_loan = (self.open_out_loan + self.close_out_loan) * interest_rate / 2

        self.roe = self.battery_size * self.cost * (1 - loan_percent) * roe
        self.opex = self.battery_size * self.cost * op_ex

        if self.constant_throughput == 0:
            self.capacity_upgrade_cost = np.zeros(self.life)
        else:
            self.capacity_upgrade_cost = (1 - self.degr_level) * self.battery_size \
                                         * (self.cost * np.power((1 - self.bess_cost_reduction), self.year))

        self.total_out = - (self.depreciation + self.interest + self.roe + (self.opex * (1 + ((1 / 12) * 0.1)))
                            + self.capacity_upgrade_cost) * (80 / 79)
        self.total_out_loan = - (self.loan + self.interest_loan + self.roe + (self.opex * (1 + ((1 / 12) * 0.1)))
                                 + self.capacity_upgrade_cost) * (80 / 79)

        self.interest_working_capital = ((- self.total_out / 8) + (self.opex * (1 / 12))) * 0.1
        self.interest_working_capital_loan = ((- self.total_out_loan / 8) + (self.opex * (1 / 12))) * 0.1

        self.capacity_deferral = (self.battery_size * transformer_cost * (loan_percent * transformer_interest
                                                                          + (1 - loan_percent) * roe)) \
                                 + (self.battery_size * trans_land_req * land_cost
                                    * (loan_percent * transformer_interest + (1 - loan_percent) * roe))
        self.outage_reduction = self.battery_size * 1000 * total_outage * (average_tariff - avg_energy_cost) \
                                * pow(energy_cost_increase, (self.year - 1))
        self.transmission_loss = transmission_loss * pow(energy_cost_increase, (self.year - 1)) * (
                self.battery_size / 20)

        self.net_cash_flow = self.total_out_loan + self.net_benefits + self.scrap_value + self.capacity_deferral \
                             + self.outage_reduction + self.transmission_loss
        npv_array = np.append([0], self.net_cash_flow)
        self.npv = np.npv(discount_rate, npv_array)
        self.npv_list = np.append(np.zeros(self.life - 1), self.npv)
