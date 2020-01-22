import pandas as pd
import numpy as np
import os
from datetime import datetime


class Input:

    def __init__(self):
        additional_hour_conversion = 0
        self.ramp_up_start_time = []
        self.ramp_up_end_time = []
        self.FMT = '%H:%M'
        self.ramp_up_time_in_hours = 0
        self.years = 15
        self.life = 15
        self.hours = 2
        self.solar_ic = 8020
        self.wind_ic = 8800
        self.solar_ic_cur = 1680.74
        self.wind_ic_cur = 59557
        self.load_growth = 1.045  # Set to input
        self.solar_growth = 1.2  # Set to input
        self.wind_growth = 1.2  # Set to input
        if self.life >= 14:
            self.total_cycles = 7000
        elif self.life == 12:
            self.total_cycles = 5000
        elif self.life == 10:
            self.total_cycles = 4000

        self.rt_efficiency = 0.85
        self.dod = 0.94

        if self.total_cycles == 4000:
            self.degr = 0.8
        if self.total_cycles == 5000:
            self.degr = 0.7
        if self.total_cycles == 7000:
            self.degr = 0.7

        self.scrap_percent = 0.1

        if self.total_cycles == 4000:
            self.cost_1hr = 45500000
            self.cost_2hr = 62525000
        if self.total_cycles == 5000:
            self.cost_1hr = 50000000
            self.cost_2hr = 66000000
        if self.total_cycles == 7000:
            self.cost_1hr = 53000000
            self.cost_2hr = 70276036.47

        self.constant_throughput = 0

        self.bess_size_start = 10  # Input
        self.bess_size_end = 50  # Input
        self.bess_size_incr = 5  # Input

        self.discount_rate = 0.089

        self.costs = [8, 7.03, 3.63, 2.81]
        self.eci = 0.03

        self.loan_percent = 0.7
        self.interest_rate = 0.09
        self.tax_rate = 0.25
        self.roe = 0.14 / (1 - self.tax_rate)
        self.op_ex = 0.01
        self.transmission_reduction_1hr = 1000000
        self.transmission_reduction_2hr = 2000000
        self.bess_cost_reduction_rate = 0.1

        self.transformer_cost = 1300000
        self.transformer_interest = 0.11
        self.land_cost = 215278
        self.trans_land_req = 20

        self.average_tariff = 7
        self.total_outage = 20

    def set_ramp_up_time_selection(self, start_time, end_time):
        self.ramp_up_start_time = start_time
        self.ramp_up_end_time = end_time
        self.ramp_up_start_time = datetime.strptime(self.ramp_up_start_time, self.FMT) \
                                  - datetime.strptime("00:00", self.FMT)
        self.ramp_up_end_time = datetime.strptime(self.ramp_up_end_time, self.FMT) \
                                  - datetime.strptime("00:00", self.FMT)
        self.ramp_up_start_time = float(self.ramp_up_start_time.total_seconds()/3600)
        self.ramp_up_end_time = float(self.ramp_up_end_time.total_seconds()/3600)

    def set_years(self, years):
        self.years = years

    def set_life(self, life):
        self.life = life

    def set_hours(self, hours):
        self.hours = hours

    def set_re_ic(self, solar, wind, solar_cur, wind_cur):
        self.solar_ic = solar
        self.wind_ic = wind
        self.solar_ic_cur = solar_cur
        self.wind_ic_cur = wind_cur

    def set_growth_rates(self, input_values):
        self.load_growth = 1 + input_values[0] / 100
        self.solar_growth = 1 + input_values[1] / 100
        self.wind_growth = 1 + input_values[2] / 100

    def set_bess_param(self, cycles, efficiency, dod_up, dod_low, degr, scrap_percent):
        self.total_cycles = cycles
        self.rt_efficiency = efficiency / 100
        self.dod = (dod_up - dod_low) / 100
        self.degr = degr / 100
        self.scrap_percent = scrap_percent / 100

    def set_bess_cost(self, hour, cost):
        if hour == 1:
            self.cost_1hr = cost
        if hour == 2:
            self.cost_2hr = cost

    def set_constant_throughput(self, throughput):
        self.constant_throughput = throughput  # 0 - degradation, 1 - no degradation

    def set_bess_range(self, start, end, incr):
        self.bess_size_start = start  # Input
        self.bess_size_end = end  # Input
        self.bess_size_incr = incr  # Input

    def set_discount_rate(self, discount):
        self.discount_rate = discount / 100

    def set_costs(self, costs):
        # costs: costs[0] - dsm price, costs[1] - vc_peak, costs[2] - vc_min, costs[3] - vc_exc, (All for year 1)
        self.costs = costs

    def set_energy_cost_increase(self, eci):
        self.eci = eci / 100

    def set_financial_param(self, loan_percent, interest_rate, tax_rate, post_tax_roe, op_ex):
        self.loan_percent = loan_percent / 100
        self.interest_rate = interest_rate / 100
        self.tax_rate = tax_rate / 100
        self.roe = (post_tax_roe / 100) / (1 - tax_rate / 100)
        self.op_ex = op_ex / 100

    def set_roe(self, post_tax_roe):
        self.roe = post_tax_roe / (1 - self.tax_rate)

    def set_transmission_reduction(self, transmission_reduction):
        hour = self.hours
        if hour == 1:
            self.transmission_reduction_1hr = transmission_reduction
        if hour == 2:
            self.transmission_reduction_2hr = transmission_reduction

    def set_bess_cost_reduction(self, bess_cost_reduction_rate):
        self.bess_cost_reduction_rate = bess_cost_reduction_rate / 100

    def set_transformer_param(self, transformer_cost, transformer_interest, land_cost, trans_land_req):
        self.transformer_cost = transformer_cost
        self.transformer_interest = transformer_interest / 100
        self.land_cost = land_cost
        self.trans_land_req = trans_land_req

    def set_outage_param(self, average_tariff, total_outage):
        self.average_tariff = average_tariff
        self.total_outage = total_outage

    def get_years(self):
        return self.years

    def get_life(self):
        return self.life

    def get_hours(self):
        return self.hours

    def get_re_ic(self):
        return self.solar_ic, self.wind_ic, self.solar_ic_cur, self.wind_ic_cur

    def get_growth_rates(self):
        return self.load_growth, self.solar_growth, self.wind_growth

    def get_bess_param(self):
        return self.life, self.total_cycles, self.rt_efficiency, self.degr, self.scrap_percent, self.dod

    def get_bess_cost(self, hour):
        if hour == 1:
            return self.cost_1hr
        if hour == 2:
            return self.cost_2hr

    def get_constant_throughput(self):
        return self.constant_throughput

    def get_bess_range(self):
        return self.bess_size_start, self.bess_size_end, self.bess_size_incr

    def get_discount_rate(self):
        return self.discount_rate

    def get_costs(self):
        # costs: costs[0] - dsm price, costs[1] - vc_peak, costs[2] - vc_min, costs[3] - vc_exc, (All for year 1)
        return self.costs

    def get_energy_cost_increase(self):
        return 1 + self.eci

    def get_ramp_up_time_selection(self):
        return self.ramp_up_start_time, self.ramp_up_end_time

    def get_financial_param(self):
        return self.loan_percent, self.interest_rate, self.roe, self.op_ex

    def get_roe_tax(self):
        post_tax_roe = self.roe * (1 - self.tax_rate)
        return post_tax_roe, self.tax_rate

    def get_transmission_reduction(self, hour):
        if hour == 1:
            return self.transmission_reduction_1hr
        if hour == 2:
            return self.transmission_reduction_2hr

    def get_bess_cost_reduction(self):
        return self.bess_cost_reduction_rate

    def get_transformer_param(self):
        return self.transformer_cost, self.transformer_interest, self.land_cost, self.trans_land_req

    def get_outage_param(self):
        return self.average_tariff, self.total_outage
