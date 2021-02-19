import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from app import app
from database import transforms
from datetime import timedelta
import plotly.express as px
import json
import numpy as np
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_model import ARIMA
import pmdarima as pm

dff = transforms.df_reg
config = {'modeBarButtonsToRemove': ['pan2d', 'select2d', 'lasso2d', 'zoomOut2d', 'zoomIn2d', 'hoverClosestCartesian',
                                     'zoom2d', 'autoScale2d', 'hoverCompareCartesian', 'zoomInGeo', 'zoomOutGeo',
                                     'hoverClosestGeo', 'hoverClosestGl2d', 'toggleHover',
                                     'zoomInMapbox', 'zoomOutMapbox', 'toggleSpikelines'],
          'displaylogo': False}

map_data_options = [{'value': "confirmed", 'label': "Confirmed cases "},
                    {'value': "deaths", 'label': "Deaths "},
                    {'value': "tests", 'label': "Number of Tests "},
                    {'value': "positives", 'label': "Positives "},
                    {'value': "recovered", 'label': "Recovered "},
                    {'value': "hosp", 'label': "Hospitalized "},
                    {'value': "icu", 'label': "In ICU "},
                    {'value': "vent", 'label': "In Ventilator "}]
region_options = [{'value': 'National', 'label': 'National'}] + [{'value': i, 'label': i} for i in
                                                                 dff.region.unique()[1:]]

layout = dbc.Container([
    dbc.Card([
        dbc.CardHeader([
            html.H4('Prediction Model', className='d-inline', id='prediction-model'),

        ]),

        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('State', html_for='proj_dd_region'),
                    dcc.Dropdown(options=region_options, id='proj_dd_region', value="National",
                                 multi=False, style={'fontSize': '100%'}, placeholder='Optional Region'),
                ], className='col-12 col-md-6 col-xl-3'),

                html.Div(id='proj_first_time', children=True, style={'display': 'none'}),
            ], className='mb-4'),
            dbc.Row([
                dbc.Col(dbc.Spinner(
                    dcc.Graph(id='proj_split_1', config=config, style={'height': '50vh'}), color='secondary', size='lg')
                    , className='col-12 col-xl-6'),
                dbc.Col(dbc.Spinner(
                    dcc.Graph(id='proj_split_2', config=config, style={'height': '50vh'}), color='secondary', size='lg')
                    , className='col-12 col-xl-6'),
            ], id='proj_split_row', className='mt-4', style={'minHeight': '47vh'}),

            dbc.Row([
                dbc.Col([

                    html.P(' '),
                    html.Span('The companion python Jupyter notebook is available '),
                    html.A('here', href='https://cov19-aus.herokuapp.com/assets/DataProcessing.ipynb',
                           target='_blank'),
                ], className='ml-4'),
            ], className='mt-4'),
        ]),
    ], style={'minHeight': '80vh'}),

    # bottom of screen
    dbc.Row([], style={'minHeight': '15vh'}),
], fluid=True, id='projection_section')


@app.callback(
    [Output('proj_split_1', 'figure'),
     Output('proj_split_2', 'figure')],
    [Input('proj_dd_region', 'value')])
def update_timeline_plots(region):
    data_type = 'log_inc_smooth'#'log(% increase)' #
    tmp = dff.loc[dff['region'] == region].reset_index()[data_type]
    print(tmp.isna().sum(), tmp)
    split = int(len(tmp) * 0.8)
    train = tmp[:split]
    test = tmp[split:]

    model_fit = pm.auto_arima(train, start_p=0, start_q=0,
                              test='adf',  # use adftest to find optimal 'd'
                              max_p=3, max_q=3,  # maximum p and q
                              m=1,  # frequency of series
                              d=None,  # let model determine 'd'
                              seasonal=False,  # No Seasonality
                              start_P=0,
                              D=0,
                              trace=True,
                              error_action='ignore',
                              suppress_warnings=True,
                              stepwise=True)

    # model = ARIMA(train, order=(2, 2, 1))
    # model_fit = model.fit(disp=0)
    print(model_fit.summary())

    # Forecast
    fc, conf = model_fit.predict(len(test), alpha=0.05, return_conf_int=True)  # 95% conf

    # Make as pandas series
    fc_series = pd.Series(fc, index=test.index)
    lower_series = pd.Series(conf[:, 0], index=test.index)
    upper_series = pd.Series(conf[:, 1], index=test.index)

    # Plot
    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=train.index,
            y=train.values,
            mode="lines",
            name='training',
            line=go.scatter.Line(color="blue"),
            showlegend=True)
    )
    fig1.add_trace(
        go.Scatter(
            x=test.index,
            y=test.values,
            mode="lines",
            name='actual',
            line=go.scatter.Line(color="green"),
            showlegend=True)
    )
    fig1.add_trace(
        go.Scatter(
            x=fc_series.index,
            y=fc_series.values,
            mode="lines",
            name='forecast',
            line=dict(color='rgba(10,10,10,1)'),
            showlegend=True)
    )

    fig1.add_trace(
        go.Scatter(
            x=lower_series.index,
            y=lower_series,
            line=dict(color='rgba(50,50,50,0.5)'),
            name='confidence upper bound',
        ))

    fig1.add_trace(
        go.Scatter(
            x=upper_series.index,
            y=upper_series,
            line=dict(color='rgba(50,50,50,0.5)'),
            fill='tonexty',
            name='confidence lower bound'
        ))
    fig1.update_layout(
        title=f"Forecasting of {data_type}",
        xaxis_title="Development",
        yaxis_title=f"{data_type}",
        legend_title="Legend",
        font=dict(
            family="Arial",
            size=18,
            color="RebeccaPurple"
        )
    )

    # transform back to original data
    tmp = dff.loc[dff['region'] == region].reset_index()['confirmed']
    train = tmp[:split]
    test = tmp[split:]

    log_per_inc = fc
    per_inc = np.exp(log_per_inc)
    inc_fac = per_inc + 1
    fc = [train.values[-1]]
    for i in inc_fac:
        fc.append(fc[-1] * i)
    fc_series = pd.Series(fc[1:], index=test.index)

    # Plot
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=train.index,
            y=train.values,
            mode="lines",
            name='training',
            line=go.scatter.Line(color="blue"),
            showlegend=True)
    )
    fig.add_trace(
        go.Scatter(
            x=test.index,
            y=test.values,
            mode="lines",
            name='actual',
            line=go.scatter.Line(color="green"),
            showlegend=True)
    )
    fig.add_trace(
        go.Scatter(
            x=fc_series.index,
            y=fc_series.values,
            mode="lines",
            name='forecast',
            line=dict(color='rgba(10,10,10,1)'),
            showlegend=True)
    )
    fig.update_layout(
        title=f"Forecasting of Covid19 Cases",
        xaxis_title="Development",
        yaxis_title=f"Confirmed Cases",
        legend_title="Legend",
        font=dict(
            family="Arial",
            size=18,
            color="RebeccaPurple"
        )
    )
    return fig1, fig
