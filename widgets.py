import ipywidgets
from data_ingestion import mat_data as data
import numpy as np

# TODO: append id to sub labels
sub_name_dropdown_labels = list(zip(data['group'] + " " + data['subjects'], data['subjects']))
sub_name_dropdown = ipywidgets.Dropdown(options=sub_name_dropdown_labels)
group_name_dropdown = ipywidgets.Dropdown(options=np.unique(data['group']))



block_start_slider = ipywidgets.SelectionSlider(
    options=list(range(1,34+1)),
    description='block',
    value=1,
    layout={'width': '500px'})

block_end_slider=ipywidgets.SelectionSlider(options=[False]+list(range(1,34+1)),
                          description='block end',
                          value=False,
                          layout={'width': '500px'})

trial_start_slider = ipywidgets.SelectionSlider(
    options=list(range(1,10+1)),
    description='trial',
    value=1)

trial_end_slider=ipywidgets.SelectionSlider(options=[False]+list(range(1,10+1)),
                          description='trial end',
                          value=False)

