import os
import pandas as pd
from lc_dispatch import least_cost_dispatch
from bess_analysis import analysis, sensitivity_analysis_cost_roe
from input import Input

src = r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2'
UPLOAD_FOLDER = os.path.join(src, "Uploads Folder")

input_values = Input()
size = 20

list_unmet_df, df_load_schedule, df_unmet = least_cost_dispatch(UPLOAD_FOLDER, input_values, src)
df_size_npv = analysis(input_values, list_unmet_df, src)
sensitivity_analysis_cost_roe(input_values, list_unmet_df, size, src)

directory = os.path.join(src, "Working Files")
os.chdir(directory)
writer1 = pd.ExcelWriter("Demand.xlsx", engine="xlsxwriter")
writer2 = pd.ExcelWriter("Dispatch.xlsx", engine="xlsxwriter")

df_load_schedule.to_excel(writer1)
df_unmet.to_excel(writer2)

writer1.save()
writer2.save()
