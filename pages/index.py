#import packages#####################################################
from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px

#preprocessing#########################################################
from preprocessing.setup import profiles, ref2021_data

#main page of app - user input and models##################################

page_1_layout = html.Div([

    #sidebar
    html.Div(children = [

        #inputs head
        html.H3("Scenario inputs"),
        #qr value
        dbc.Row([
            dbc.Label("Mainstream QR total", width = 5),
            dbc.Col(
                dbc.Input(id = "ms_qr", type = "number", min = 0, step = 1, required = True, value = 1_060_710_491),
                width = 7
            )
        ]),
        html.Br(),
        #panel weightings
        html.H4("Panel quality weights"),
        dbc.Row([
            dbc.Label("4*", width = 2),
            dbc.Col(
                dbc.Input(id = "panel4", type = "number", min = 0, required = True, value = 1),
                width = 10
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Label("3*", width = 2),
            dbc.Col(
                dbc.Input(id = "panel3", type = "number", min = 0, required = True, value = 1),
                width = 10
                )
        ]),
        html.Br(),
        #uoa weightings
        html.H4("UoA quality weights"),
        dbc.Row([
            dbc.Label("4*", width = 2),
            dbc.Col(
                 dbc.Input(id = "uoa4", type = "number", min = 0, required = True, value = 4),
                 width = 10
            )
        ]),
        html.Br(),
        dbc.Row([
            dbc.Label("3*", width = 2),
            dbc.Col(
                dbc.Input(id = "uoa3", type = "number", min = 0, required = True, value = 1),
                width = 10
            )
        ]),
        html.Br(),
        #filtering options
        html.H3("Filters"),
        #profile selector
        dbc.Row([
            dbc.Label("Profile"),
            dcc.Dropdown(profiles, value = profiles, multi = True, id = "profile_select")
        ]),
        html.Br(),
        #panel selector
        dbc.Row([
            dbc.Label("Main panel"),     
            dcc.Dropdown(["A", "B", "C", "D"], value = ["A", "B", "C", "D"], multi = True, id = "panel_select")
        ]),
        html.Br(),
        #uoa selector
        dbc.Row([
            dbc.Label("UoA number"),
            dcc.Dropdown(list(range(1, 35)), value = list(range(1, 35)),  multi = True, id = "uoa_select")
        ]),
        html.Br(),
        #download
        html.Label("Raw data"),
        html.Br(),
        html.Button("Download data", id = "download_button"),
        dcc.Download(id = "download_data"),
        #store data based on filters
        dcc.Store(id = "processed_data")
    ],
    style = {
        "position": "fixed", 
        "top": 0,
        "left": 0, "bottom": 0, 
        "width": "24rem", 
        "padding": "2rem 1rem", 
        "background-color": "#f5f5dc",
        "overflow": "scroll"
        } 
    ),

    #main page
    html.Div(children = [
        #h2 - plot
        html.H2("Plot of QR allocations"),
        #plot
        dcc.Graph(id = "hei_plot_filtered"),
        #h2 table
        html.H2("Table of QR allocations"),
        #table
        dash_table.DataTable(
            id = "hei_tbl",
            columns = [
                    {"name": "Main Panel", "id": "main_panel"},
                    {"name": "UoA number", "id": "unit_of_assessment_number"},
                    {"name": "UKPRN", "id": "institution_code_ukprn"},
                    {"name": "Institution", "id": "institution_name"},
                    {"name": "Profile", "id": "profile"},
                    {"name": "Mainstream QR allocation", "id": "hei_allocation", "type": "numeric", "format": dict(specifier = ",.0f")}
                    ],
            filter_action = "native",
            sort_action = "native",
            filter_options = {"case": "insensitive"}
                    )
                ],
        style = {"margin-left": "26rem", "padding": "2rem 1rem"}
        )

])

#callbacks##########################################################################

#process data
@callback(
    Output("processed_data", "data"),
    Input("ms_qr", "value"),
    Input("panel4", "value"),
    Input("panel3", "value"),
    Input("uoa4", "value"),
    Input("uoa3", "value")
)
def create_dataset(ms_qr, panel4, panel3, uoa4, uoa3):

    #set df
    df = ref2021_data

    #profile allocations
    outputs_total = ms_qr * 0.6
    impact_total = ms_qr * 0.25
    environment_total = ms_qr * 0.15

    #put profile totals into a dictionary
    profile_allocation_dict = {
            "profile": ["Outputs", "Impact", "Environment"], 
                "profile_allocation": [outputs_total, impact_total, environment_total]
                }

    profile_allocation_df = pd.DataFrame(profile_allocation_dict)

    #change ref2021 3/4* grade profiles to string
    df[["3", "4"]] = df[["3", "4"]].astype(str)

    #replace -s with 0s
    df[["3", "4"]] = df[["3", "4"]].replace("-", "0")

    #...and convert back to numeric
    df[["3", "4"]] = df[["3", "4"]].astype(float)

    #add quality and cost weightings
    df["panel_qw_fte"] = (df["3"]*panel3 + df["4"]*panel4) * df["fte_of_submitted_staff"] * df["c_weight"]
    df["uoa_qw_fte"] = (df["3"]*uoa3 + df["4"]*uoa4) * df["fte_of_submitted_staff"] * df["c_weight"]

    #calculate panel allocations#####################################################
    
    # #remove 'overall' profile as not used
    # #group at main panel and profile level
    # #calc total panel_qw_fte
    panel_allocations = (df.
                        query("profile != 'Overall'").
                        groupby(["main_panel", "profile"], as_index = False).
                        agg({"panel_qw_fte": "sum"})
                        )

    #add on pane % total for each profile
    panel_allocations["panel_pct"] = 100 * panel_allocations["panel_qw_fte"] / panel_allocations.groupby("profile")["panel_qw_fte"].transform("sum")

    #merge in total allocations
    panel_allocations = pd.merge(panel_allocations, profile_allocation_df, how = "inner", on = "profile")

    #work out the allocations to each panel
    panel_allocations["panel_allocation"] = panel_allocations["profile_allocation"] * (panel_allocations["panel_pct"] / 100)

    #calculate uoa allocations###########################################################

    #remove 'overall' profile as not used
    #group at main panel and profile level
    #calc total panel_qw_fte
    uoa_allocations = (df.
                        query("profile != 'Overall'").
                        groupby(["main_panel", "unit_of_assessment_number", "profile"], as_index = False).
                        agg({"uoa_qw_fte": "sum"})
                    )

    #add on pane % total for each profile
    uoa_allocations["uoa_pct"] = 100 * uoa_allocations["uoa_qw_fte"] / uoa_allocations.groupby(["profile", "main_panel"])["uoa_qw_fte"].transform("sum")

    #merge in panel allocations
    uoa_allocations = pd.merge(uoa_allocations, panel_allocations, how = "inner", on = ["main_panel", "profile"])

    #work out the allocations to each panel
    uoa_allocations["uoa_allocation"] = uoa_allocations["panel_allocation"] * (uoa_allocations["uoa_pct"] / 100)

    #drop unnecessary columns
    uoa_allocations = uoa_allocations.drop(labels = ["uoa_qw_fte"], axis = 1)

    #calculate hei allocations######################################################

    #remove 'overall' profile as not used
    #group at main panel and profile level
    #calc total panel_qw_fte
    hei_allocations = (df.
                        query("profile != 'Overall'").
                        groupby(["main_panel", "unit_of_assessment_number", "institution_code_ukprn", "institution_name","profile"], as_index = False).
                        agg({"uoa_qw_fte": "sum"})
                    )

    #add on pane % total for each profile
    hei_allocations["hei_pct"] = 100 * hei_allocations["uoa_qw_fte"] / hei_allocations.groupby(["profile", "main_panel", "unit_of_assessment_number"])["uoa_qw_fte"].transform("sum")

    #merge in uoa allocations
    hei_allocations = pd.merge(hei_allocations, uoa_allocations, how = "inner", on = ["main_panel", "profile", "unit_of_assessment_number"])

    #work out the allocations to each hei
    hei_allocations["hei_allocation"] = hei_allocations["uoa_allocation"] * (hei_allocations["hei_pct"] / 100)

    #prepare allocations for display
    hei_allocations["hei_allocation"] = round(hei_allocations["hei_allocation"], 0)
    hei_allocations = hei_allocations.drop(
            labels = ["uoa_qw_fte", "hei_pct", "uoa_pct", "panel_qw_fte", "profile_allocation", "panel_allocation", "uoa_allocation"],
            axis = 1
                )

    return hei_allocations.to_json(orient = "split")


#controlling plot
@callback(
    Output('hei_plot_filtered', 'figure'),
    Input("processed_data", "data"),
    Input("profile_select", "value"),
    Input("panel_select", "value"),
    Input("uoa_select", "value")
)
def update_plot(processed_data, profile_select, panel_select, uoa_select):

    #read in stored data
    df = pd.read_json(processed_data, orient = "split")

    #filter according to user selections
    df = df.loc[
        df.profile.isin(profile_select) &
        df.main_panel.isin(panel_select) &
        df.unit_of_assessment_number.isin(uoa_select)
        ]

    #plot
    figure = px.histogram(
        df,
        x = "institution_name",
        y = "hei_allocation", 
        color = "profile",
        color_discrete_sequence = px.colors.qualitative.G10,
        title = "",
        barmode = "stack",
        labels ={"hei_allocation": "Mainstream QR allocation (£M)"}
        )
        
    figure.update_xaxes(visible = False)
    figure.update_layout(xaxis = {"categoryorder": "total descending"})

    return figure

#controlling table
@callback(
    Output("hei_tbl", "data"),
    Input("processed_data", "data"),
    Input("profile_select", "value"),
    Input("panel_select", "value"),
    Input("uoa_select", "value")
)
def update_tbl(processed_data, profile_select, panel_select, uoa_select):

    #read in stored data
    df = pd.read_json(processed_data, orient = "split")

    df = df.loc[
        df.profile.isin(profile_select) &
        df.main_panel.isin(panel_select) &
        df.unit_of_assessment_number.isin(uoa_select)
        ]

    return df.to_dict("records")

#download data
@callback(
    Output("download_data", "data"),
    Input("download_button", "n_clicks"),
    State("processed_data", "data"),
    State("profile_select", "value"),
    State("panel_select", "value"),
    State("uoa_select", "value"),
    prevent_initial_call = True
) 
def download_data(n_clicks, processed_data, profile_select, panel_select, uoa_select):

    #read in stored data
    df = pd.read_json(processed_data, orient = "split")

    df = df.loc[
        df.profile.isin(profile_select) &
        df.main_panel.isin(panel_select) &
        df.unit_of_assessment_number.isin(uoa_select)
        ]

    return dcc.send_data_frame(df.to_csv, "qr_scenario_data.csv")


