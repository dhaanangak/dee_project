import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from app import app
from database import transforms
import pandas as pd
import numpy as np

df = transforms.df
min_p = df.confirmed.min()
max_p = df.confirmed.max()

layout = html.Div([

    dbc.Row([dbc.Col(
        html.Div([
            html.H2('Filters'),
            dcc.Checklist(id='show_national', options=[{'label': 'Show National Data', 'value': 'Y'}]),
            html.Div([html.P(),
                      html.H5('Confirmed Cases'),
                      dcc.RangeSlider(id='cases-slider', min=min_p, max=max_p,
                                      marks={i: str(i // 1000) + 'k' for i in range(0, max_p, 10000)},
                                      value=[min_p, max_p + 100]
                                      )
                      ]),
            html.Div([html.P(),
                      html.H5('Date range'),
                      dcc.DatePickerRange(
                          id='datepickerrange',
                          start_date=df['date'].min(),
                          end_date=df['date'].max(),
                          min_date_allowed=df['date'].min(),
                          max_date_allowed=df['date'].max(),
                          display_format='D MMM YYYY'
                      ),

                      dcc.RangeSlider(
                          id='rangeslider',
                          min=0,
                          max=df['date'].nunique() - 1,
                          value=[0, df['date'].nunique() - 1],
                          allowCross=False
                      ),
                      ]),
            html.Div([
                html.P(),
                html.H5('State'),
                dcc.Dropdown(id='state-drop',
                             options=[{'label': i, 'value': i} for i in df.State.unique()[1:]],
                             value=[i for i in df.State.unique()[1:]],
                             multi=True)
            ]),
            html.Div([
                html.P(),
                html.H5('Data type'),
                dcc.Dropdown(id='data-type-drop',
                             options=[{'label': i, 'value': i} for i in df.columns],
                             value=["state_abbrev", "date", "confirmed", "deaths", "hosp", "icu", "vent"],
                             multi=True)
            ])
        ], style={'marginBottom': 50, 'marginTop': 25, 'marginLeft': 15, 'marginRight': 15}),  # end div
        width=3),  # End col
        dbc.Col(html.Div([
            dcc.Tabs(id="section_data", value='tab-2', children=[
                dcc.Tab(label='Time Series Plot', value='tab-2'),
                dcc.Tab(label='Data Table', value='tab-1'),
            ])
            , html.Div(id='section_data-content')
        ]), width=9)
    ])  # end row

])  # end div
pd.Series()

@app.callback(Output('datepickerrange', 'start_date'),
              [Input('rangeslider', 'value')])
def update_daterangestart(rangeslider_value):
    return np.sort(df['date'].dt.date.unique())[rangeslider_value[0]]


@app.callback(Output('datepickerrange', 'end_date'),
              [Input('rangeslider', 'value')])
def update_daterangeend(rangeslider_value):
    return np.sort(df['date'].dt.date.unique())[rangeslider_value[1]]

# @app.callback(Output('variety-drop', 'options'),
#               [Input('province-drop', 'value')])
# def set_variety_options(province):
#     # if province is None:
#     #     provinces = []
#
#     if len(province) > 0:
#         provinces = province
#         return [{'label': i, 'value': i} for i in sorted(set(df['variety'].loc[df['province'].isin(provinces)]))]
#
#     else:
#         provinces = []
#         return [{'label': i, 'value': i} for i in sorted(set(df['variety'].loc[df['province'].isin(provinces)]))]
