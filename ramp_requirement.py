import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
os.chdir(r"C:\Users\utkakumar\Documents\Projects\World Bank Battery\DATA")
data = pd.read_excel("20_years.xlsx")

slots = list(range(0, 24))
ramp_slot = np.zeros(shape =(365*20,24))
for days in range(0,365*20):
    for slot in slots:
       ramp_slot[days, slot] =  data.loc[slot + 24*days, "Cartered Ramp requirement" ]
       
averages = []      
   
for slot in slots:
    averages.append(np.average(ramp_slot[:,slot]))
       
    
plt.plot(averages)
