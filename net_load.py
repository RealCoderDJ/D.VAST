import pandas as pd
import os


def net_load(schedule, solar, nuclear, wind, hydro, biomass, power_purchase, year,
             load_growth, solar_growth, wind_growth, src):
    directory = os.path.join(src, "Working Files")
    os.chdir(directory)

    if year == 3:
        print("hello")
    schedule = schedule * (load_growth ** year)
    solar = solar * (solar_growth ** year)
    wind = wind * (wind_growth ** year)
    net_schedule = schedule.copy()

    # Subtracting the RE generation from implemented schedule
    net_schedule -= (nuclear + hydro + solar + wind + biomass)

    writer = pd.ExcelWriter("Net_Schedule_" + str(year + 1) + ".xlsx", engine="xlsxwriter")
    net_schedule.to_excel(writer, sheet_name="Sheet1")
    writer.save()

    return net_schedule
