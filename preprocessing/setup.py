#import##################################################
import pandas as pd

from preprocessing.functions import tidy_columns

#profiles##########################################
profiles = ["Environment", "Impact", "Outputs"]

#english ukprns####################################
english_ukprns = pd.read_excel(
    io = "data/qr_by_uoa.xlsx",
    engine = "openpyxl",
    usecols = "A"
)

english_ukprn_list = english_ukprns.ukprn.values.tolist()

#data import##########################################################

#cost weightings
cost_weights = pd.read_excel(
    io = "data/cost_weight.xlsx",
    engine = "openpyxl"
)

#import ref2021 results
ref2021_data = pd.read_excel(
    io = "data/REF 2021 Results - All - 2022-05-06.xlsx",
    header = 6,
    engine = "openpyxl"
)
    
#tidy up column names
ref2021_data.columns = [tidy_columns(c) for c in ref2021_data.columns.values.tolist()]

#drop null row at bottom of dataframe
ref2021_data = ref2021_data[ref2021_data["profile"].notnull()]

#only english heps
ref2021_data = ref2021_data.loc[ref2021_data.institution_code_ukprn.isin(english_ukprn_list)]

#join on cost weightings
ref2021_data = pd.merge(
    ref2021_data, 
    cost_weights, 
    how = "left",
    left_on = ["unit_of_assessment_number", "main_panel"],
    right_on = ["unit_of_assessment_number", "panel"]
    )