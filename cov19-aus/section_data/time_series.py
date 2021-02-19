import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import pandas as pd
from pandas.api.types import is_numeric_dtype
import plotly.graph_objs as go
import plotly.express as px
from dash.dependencies import Input, Output
import dash_table
from app import app
from database import transforms
import numpy as np
df = transforms.df

layout = html.Div(children=[dcc.Graph(id='time-series-plot')],
                  id='table-paging-with-graph-container',
                  className="five columns"
                  )


@app.callback(
    Output(component_id='time-series-plot', component_property='figure'),

    [
        Input('show_national', 'value'),
        Input('cases-slider', 'value'),
        Input('state-drop', 'value'),
        Input('data-type-drop', 'value'),
        Input('datepickerrange', 'start_date'),
        Input('datepickerrange', 'end_date')
    ]
)
def update_graph(nationalcheck, confirmed, states, data_types, start, end):
    if states is None:
        states = []
    if data_types is None:
        data_types = []
    if 'date' not in data_types:
        data_types.append('date')
    if 'State' not in data_types:
        data_types.append('State')
    low = confirmed[0]
    high = confirmed[1]
    if nationalcheck == ['Y']:
        dff = transforms.df
    else:
        dff = transforms.df_states
    dff = dff.loc[(dff['confirmed'] >= low) & (dff['confirmed'] <= high)]
    dff = dff.loc[(dff['date'] >= start) & (dff['date'] <= end)]

    if nationalcheck == ['Y']:
        dff = dff.loc[(dff['State'].isin(states)) | dff['State'].isna()]
    else:
        dff = dff.loc[dff['State'].isin(states)]

    dff = dff[data_types]
    dff["State"] = dff["State"].fillna("National")

    cols = []
    data_types.remove('date')
    for dt in data_types:
        if is_numeric_dtype(dff[dt]):
            cols.append(dt)

    if nationalcheck != ['Y'] and len(states) == 0:
        new_row = {c:0 for c in cols}
        dff = dff.append(new_row,ignore_index=True)
        trace1 = px.line(dff, x='date', y=cols)
        trace1.add_annotation(x=2, y=0,
                           text="No data selected",
                           showarrow=False,
                              )
    else:
        trace1 = px.line(dff, x='date', y=cols, color='State')
    return trace1
