import pandas as pd
import numpy as np
import os
import math

src = r"C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2"

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
