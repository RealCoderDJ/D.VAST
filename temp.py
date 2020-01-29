# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import pandas as pd
import xlsxwriter
#from typing import List, Union
from xlrd import open_workbook
import numpy as np
import time
from openpyxl import Workbook
from datetime import timedelta, date
from shutil import copyfile
import shutil
from openpyxl import load_workbook 

os.chdir(r'C:\Users\dimitra\Documents\BRPL\Test')

ramp_sum = pd.DataFrame()
ramp_count = pd.DataFrame()
unmet_sum = pd.DataFrame()
unmet_count = pd.DataFrame()

for i in range(1, 30):
    ramp = pd.read_excel('Ramp_up_' + str(i) + '.xlsx', index_col=0)
    unmet = pd.read_excel('Unmet_' + str(i) + '.xlsx', index_col=0)
    
    ramp[ramp<=0] = 0
    
    cols = unmet.columns
    for c in cols:
        flag = 0
        unmet_list = unmet[c].tolist()
        for j in range(len(unmet_list)):
            if unmet_list[j] > 0:
                flag = 1
            if flag == 1:
                unmet_list[j] = 0
        unmet[c] = unmet_list
        
    r_count = ramp.copy()
    r_count[r_count>0.1] = 1
    r_count[r_count<1] = 0
    
    u_count = unmet.copy()
    u_count[u_count>-0.1] = 0
    u_count[u_count<-0.1] = 1
        
    ramp_sum[i] = ramp.sum(1).tolist()
    ramp_count[i] = r_count.sum(1).tolist()
    unmet_sum[i] = unmet.sum(1).tolist()
    unmet_count[i] = u_count.sum(1).tolist()
    
    writer1 =  pd.ExcelWriter("Excess_" + str(i) + ".xlsx", engine="xlsxwriter")
    unmet.to_excel(writer1, sheet_name="sheet1")
    writer1.save()
    writer2 =  pd.ExcelWriter("Ramp_req_" + str(i) + ".xlsx", engine="xlsxwriter")
    ramp.to_excel(writer2, sheet_name="sheet1")
    writer2.save()
    
    print(i)
    
    

