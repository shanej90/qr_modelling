from dash import Dash, html, dcc, dash_table, Input, Output, State, callback
import dash_bootstrap_components as dbc

from preprocessing.setup import cost_weights

page_2_layout = html.Div([ 
    html.H1("About"),
    html.Br(),
    dcc.Markdown(
    """
    ## What is QR funding?

    Mainstream QR (quality-related) research funding is funding allocated by the devolved governments of the United Kingdom to higher education providers (HEPs).

    The allocations are driven by the results of the Research Excellence Framework (REF). REF is an exercise held once every six-eight years to assess the 'quality' of research in the UK.

    Submissions are made by HEI. These are divided further into Main Panels (broad discipline areas) and then further into Units of Assessment (UoAs - more specific areas of research).

    Research is graded in star bands, from 4* ('internationally excellent') to 1* or even 'unclassified'.

    The results of the last exercise, REF2021, were released in May 2022. At the time of production (June 2022), the resultant QR allocation is yet to be declared.

    As such, this tool allows users to test different scenarios, depending on how Research England decides to fund HEIs.

    ## Funding allocation algorithm

    This app uses the mainstream QR funding allocation methodology as laid out in Research England's [How we fund HEPs document](https://www.ukri.org/wp-content/uploads/2021/08/RE-06082021-RE-How-we-fund-HEPs-FINAL.pdf) (pdf).

    Essentially, it follows these steps:

        - Split money across the REF profiles: Outputs 60%; Impact 25 %; Environment 15%.
        - Apply cost-weightings to discipline areas, so more expensive research receives higher levels of funding.
        - Weight all three and four star research equally (you can change this in the tool).
        - Multiply the proportions of three and four star research by the FTE submitted.
        - Work out the total 'quality (and cost)-weighted FTE' for each Panel (per profile).
        - Next, apply a 4x weighting to 4* star research and 1x to 3star (you can change this in the tool).
        - Quality (and cost-weight) the total FTE within each UoA to work what share of the panel allocation (per profile) they should get.
        - Use the same weighting for each individual submission within the UoA to work out allocations to individual HEIs.

    ## Data sources

    The REF 2021 results data is from the [REF results website](https://results2021.ref.ac.uk/).

    The default mainstream QR total is as per the 2021/22 total allocation (excluding London weighting).

    The default panel/UoA weightings are as per the last REF.

    I identified English HEIs manually.

    ## Limitations

    This tool is only for English HEPs.

    Some UoAs are new this time around, and thus assumptions have been made about the cost-weighting they will receive. The cost weightings used are detailed below.

    """
    ),
    #cost weights table
    html.H3("Cost-weightings"),
    html.Br(),
    dash_table.DataTable(
        id = "cost_weight_tbl",
        columns = [
            {"name": "UoA number", "id": "unit_of_assessment_number", "type": "numeric"},
            {"name": "Main panel", "id": "panel"},
            {"name": "Weighting", "id": "c_weight", "type": "numeric", "format": dict(specifier = ",.1f")}
            ],
        data = cost_weights.to_dict("records"),
        filter_action = "native",
        filter_options = {"case": "insensitive"}
    ),
    html.Br(),
    #about me markdown
    dcc.Markdown(
    """
    ## About me

    Hi! I'm Shane - at the time of writing I am a data analyst at the University of Exeter, working in the research office. 

    I am responsible for analysis of much of the university's research management information.

    Next month (July 2022) I'm moving to work for [Ripeta](https://ripeta.com/), part of the [Digital Science](https://www.digital-science.com/) portfolio.

    I have a  [GitHub profile](https://github.com/shanej90) which hosts the [source code for this app](https://github.com/shanej90/qr_modelling), amongst other projects.
    """
    )
],
style = {"margin-left": "10rem", "padding": "2rem 1rem"}
)