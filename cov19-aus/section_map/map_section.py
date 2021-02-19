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

with open('./database/states.geojson.json') as geo:
    geojson = json.load(geo)

df = transforms.df
begin_date = df['date'].min()
end_date = df['date'].max()
no_days = (end_date - begin_date).days
df['Timeline'] = df['date'].dt.strftime('%b %d')
seq = list()
slider_marks = {}
for i in range(0, df['date'].nunique()):
    if (begin_date + timedelta(days=i)).day == 1 or i == 0:
        slider_marks[i] = (begin_date + timedelta(days=i)).strftime('%b')
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
                    {'value': "vent", 'label': "In Ventilator "},
                    {'value': "population", 'label': "Population "}]

layout = dbc.Container([
    dbc.Row([
        html.Div(id='output-clientside', style={'height': '5vh'}),
        dbc.Col(dcc.Graph(id='map_plot', config=config, style={'height': '78vh'}), width=12),
    ]),

    dbc.Row(
        dbc.Col(
            dbc.Select(id='map_data', options=map_data_options, className='position-relative',
                       style={'left': '3vw', 'top': '-75vh', 'width': '240px'}, value='confirmed')
            , className='col-12')
        , id='timeline', style={'height': '0px'}),

    html.Div(
        dcc.Slider(min=0, max=no_days, step=1, value=no_days, id='date_slider', updatemode='mouseup',
                   marks=slider_marks,
                   className='pl-0')
        , className='position-relative', style={'left': '3vw', 'bottom': '-2vh', 'width': '94vw', 'height': '0px'}),

    dbc.Card([
        dbc.CardHeader(
            html.H2("", id='stat_card_header', className='m-0',
                    style={'color': '#508caf'}), style={'backgroundColor': 'rgba(255,255,255,0.5)'}),

        dbc.CardBody(id='card_body',
                     style={'backgroundColor': 'rgba(255,255,255,0.5)', 'padding': '10px 5px 10px 20px'})
    ], style={'backgroundColor': 'rgba(255,255,255,0.5)', 'left': '3vw', 'top': '-50vh', 'width': '270px'}),

], fluid=True, id='map_section', style={'height': '90vh'})


@app.callback([Output('map_plot', 'figure'), Output('stat_card_header', 'children'), Output('card_body', 'children')],
              [Input('map_data', 'value'), Input('date_slider', 'value')])
def update_map(map_data, sel_day):
    sel_date = begin_date + timedelta(days=sel_day)
    selected_date = str(sel_date.month_name()) + " " + str(sel_date.day)

    # dff = dff.loc[dff['State'].isin(states)]
    dff = transforms.df_states.loc[(transforms.df_states['date'] == sel_date)]
    dff = dff[["State", map_data]]

    dff_prev = transforms.df_states.loc[transforms.df_states['date'] == sel_date - timedelta(days=1)]
    dff_prev = dff_prev[["State", map_data]]

    if map_data == 'population':
        dff = dff.groupby(['State'])[map_data].mean().reset_index()
        dff_prev = dff_prev.groupby(['State'])[map_data].mean().reset_index()
    else:
        dff = dff.groupby(['State'])[map_data].sum().reset_index()
        dff_prev = dff_prev.groupby(['State'])[map_data].sum().reset_index()

    fig = px.choropleth(
        dff, geojson=geojson, color=map_data,
        locations="State", featureidkey="properties.STATE_NAME",
        projection="mercator", range_color=[0, dff[map_data].max()],
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin=dict(l=60, r=60, t=50, b=50))

    dff = transforms.df_states.loc[(transforms.df_states['date'] == sel_date)]
    dff = dff[["State", map_data, 'population']] if map_data != "population" else dff[["State", map_data]]
    per_capita = []
    for s in dff.State.unique():
        text = s + " : " + human_format(
            dff.loc[dff["State"] == s][map_data].iloc[0] * 1e6 / dff.loc[dff["State"] == s]['population'].iloc[0] * 1.0)
        per_capita.append(html.Pre(text, id='lbl_per_capita' + s, style={'color': '#555555'}))

    tot_sel = dff[map_data].sum() * 1.0
    tol_pre = dff_prev[map_data].sum() * 1.0
    total_label = ["Total : " + human_format(tot_sel),
                   dbc.Badge(str('{:+.0%}'.format((tot_sel - tol_pre) / tot_sel)),
                             className="mr-3 position-relative float-right",
                             id='badge_case',
                             style={'backgroundColor': '#508caf', 'width': '50px'}),
                   dbc.Tooltip("Variance over previous day", target="badge_case")
                   ]
    card_body = [html.H3(total_label, id='lbl_total', style={'color': '#666666'}),
                 html.H5("Data per 1M", id='lbl_total', style={'color': '#666666'})
                 ] + per_capita
    return fig, selected_date, card_body


def human_format(num):
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    # add more suffixes if you need them
    return '%.1f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
