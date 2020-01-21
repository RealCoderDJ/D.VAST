import pygal
from pygal.style import DarkGreenBlueStyle
from graph_style_sheet import custom_style
import os
import pandas as pd


def sensitivity_graph():

    sizes = [i for i in range(1, 51)]
    graph = pygal.Line(include_x_axis=True, style=custom_style, x_title='BESS Cost / MW (₹ crores)',
                       y_title='NPV / MW (₹ crores)', dots_size=1.5, stroke_style={'width': 2})
    graph.title = 'Load vs Generation'

    # df = sensitivity_analysis_cost_roe(input_values, list_unmet_df, size, src)
    os.chdir(r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2\Working Files')
    df = pd.read_excel('Demand.xlsx')
    graph.x_labels = df['Date'].tolist()
    cols = ['Demand', 'Generation']
    for c in cols:
        npv_list = df[c].tolist()
        graph.add(c, npv_list)

    graph.render_to_file(r'C:\Users\dimitra\Documents\BRPL\Toolkit\D.VAST v0.1.2\Working Files/chart_demand.svg')


sensitivity_graph()