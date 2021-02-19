from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from app import app
from section_footer import footer
from section_data import data_view, table, time_series
from section_map import map_section
from section_prediction import prediction_section

header = html.Div(
    children=[
        html.P(children="😷", className="header-emoji"),
        html.H1(
            children="", className="header-title"
        ),
        html.P(
            children="Analyze the behavior of Covid19 cases in Australia between 2020-01-25 and 2021-02-06",
            className="header-description",
        ),
    ],
    className="header",
)

# top navbar
navbar_layout = dbc.Navbar([
    html.A(
        # Use row and col to control vertical alignment of logo / brand
        dbc.Row([
            # dbc.Col(html.Img(src=app.get_asset_url("logo.png"), height="60px", style={'stroke': '#508caf'})),
            dbc.Col(dbc.NavbarBrand("Covid19 Analytics - Australia", className="ml-2",
                                    style={'fontSize': '2em', 'fontWeight': '900', 'color': '#508caf'})),
        ], align="center", no_gutters=True),
        href='#'),

    dbc.NavbarToggler(id="navbar-toggler", className="ml-auto"),

    dbc.Collapse(
        dbc.Row([
            dbc.NavLink("MAP", href='#'),
            dbc.NavLink("DATA", href='#timeline', external_link=True),
            dbc.NavLink("PREDICTIONS", href='#prediction-model', external_link=True),
            dbc.NavLink("ABOUT", href='#about', external_link=True),
        ], no_gutters=True, className="ml-auto flex-nowrap mt-3 mt-md-0", align="center"),
        id="navbar-collapse", navbar=True),

], sticky="top", className='mb-4 bg-white', style={'WebkitBoxShadow': '0px 15px 15px 0px rgba(50, 50, 50, 0.1)', })


# add callback for toggling the collapse on small screens
@app.callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


@app.callback(Output('section_data-content', 'children'), [Input('section_data', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return table.layout
    elif tab == 'tab-2':
        return time_series.layout


server = app.server

app.layout = html.Div([
    navbar_layout,
    map_section.layout,
    data_view.layout,
    prediction_section.layout,
    footer.layout

]
)
if __name__ == '__main__':
    print("********************************RUNING")
    app.run_server(debug=True)#, host='0.0.0.0', port=8000)
