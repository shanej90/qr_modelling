#import packages#####################################################
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

###import local modules################################################
from pages import home
from pages import about

#app setup#############################################################
app = Dash(__name__, external_stylesheets = [dbc.themes.SANDSTONE], suppress_callback_exceptions = True)
server = app.server

#app layout##########################################################################
app.layout = html.Div([
    
    #vanigation
    html.Div(children = [
            dbc.NavbarSimple( 
                children = [
                    dbc.NavItem(dbc.NavLink("Scenario tool", href = "/")),
                    dbc.NavItem(dbc.NavLink("About", href = "/about"))
                    ],
            brand = "QR scenario tool"
        )
        ],
        style = {"margin-left": "26rem"}
        ),

    #main page
    html.Div([
        dcc.Location(id = "url", refresh = False),
        html.Div(id = "page-content")
        ])
])

#display callback###########################################
@callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname == '/':
        return home.page_1_layout
    if pathname == '/home':
        return home.page_1_layout
    elif pathname == '/about':
        return about.page_2_layout
    else:
        return '404, page does not exist'

#boilerplate setuo##########################################
if __name__ == "__main__":
    app.run_server(debug = True)