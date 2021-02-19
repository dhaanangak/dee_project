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

df = transforms.df
end_date = df["date"].max()
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4('Data Source', className='mb-4', id='about'),
            html.Span("Data aggregated from "),
            html.Span('Github', style={'fontWeight': '700', 'fontFamily': 'campaign,sans-serif'}),
            html.Span(' repository: '),
            html.A('COVID-19_Data', href='https://github.com/M3IT/COVID-19_Data',
                   target='_blank'),
            html.P(' '),
            html.Span('The data in the repository is compiled from '),
            html.A('www.covid19data.com.au', href='https://www.covid19data.com.au/data-notes',
                   target='_blank'),
            html.P(' '),
            html.Span('Per capita calculations use population data as of 31 March 2020. Source: '),
            html.A('ABS', href='https://www.abs.gov.au/AUSSTATS/abs@.nsf/Latestproducts/3101.0Main%20Features3Dec%202019?opendocument&tabname=Summary&prodno=3101.0&issue=Dec%202019&num=&view=',
                   target='_blank'),
            html.P(' '),
            html.Span('Latest data extract as of: '),
            html.Span(str(end_date.strftime('%d %b %Y')),
                      style={'fontWeight': '700', 'fontFamily': 'campaign,sans-serif'}),
        ], className='col-12 col-md-8 col-xl-9'),
    ], className='m-4', align="center", style={'height': '30vh'}),

], fluid=True, id='footer_section', className='border-top bg-white', style={'borderColor': '#666666'})