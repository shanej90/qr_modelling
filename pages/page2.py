from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

page_2_layout = html.Div([ 
    dcc.Textarea(id = "about", value = "Lorem ipsum")
])