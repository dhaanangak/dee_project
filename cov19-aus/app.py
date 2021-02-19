import dash
import dash_bootstrap_components as dbc
import pathlib

app = dash.Dash(__name__,
                external_stylesheets=[dbc.themes.BOOTSTRAP,
                                      'https://use.fontawesome.com/releases/v5.11.2/css/all.css',
                                      {'href': 'https://fonts.googleapis.com/icon?family=Material+Icons',
                                       'rel': 'stylesheet'}],
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"},
                           {'name': 'description', 'content': 'COVID-19 ANALTICAL APP'},
                           {'property': 'og:title', 'content': 'COVID-19 CURVES'},
                           {'property': 'og:type', 'content': 'website'},
                           {'property': 'og:url:', 'content': 'https://covid19-curves.herokuapp.com/'},
                           {'property': 'og:image',
                            'content': 'https://covid19-curves.herokuapp.com/assets/covid-curve-app.png'},
                           {'property': 'og:image:secure_url',
                            'content': 'https://covid19-curves.herokuapp.com/assets/covid-curve-app.png'},
                           {'property': 'og:image:type', 'content': 'image/png'},
                           {'http-equiv': 'X-UA-Compatible', 'content': 'IE=edge'},
                           {'name': "author", 'content': "Alban Tranchard"},
                           {'charset': "UTF-8"},
                           ],

                )
app.config.suppress_callback_exceptions = True
app.title = 'COVID-19'
app.config.suppress_callback_exceptions = True

# # get relative data folder
# PATH = pathlib.Path(__file__).parent
# DATA_PATH = PATH.joinpath("data").resolve()
