import pandas as pd
#
# This script standardizes the input data in /data/CX_Task_Portfolio_Summary.xlsx to a csv
# for API queries
#

# Use relative path
fn = "../data/CX_Task_Portfolio_Summary_modified.xlsx"
df = pd.read_excel(fn, sheet_name="Upload")

### Fix minor data issues
# Per instructions, these are UK locations, standardize country code as "UK"
df["Country"] = "UK"

### Now format a .csv for API query input.
# Set required columns, in order to match template in API documentation pdf
required_cols = [
    "Id",
    "Country",
    "City",
    "Street",
    "Post Code",
    "Building Number",
    "and/or",
    "Building Name",
    "Unit or Flat",
    "Latitude",
    "Longitude",
    "Property Identifier",
    "Building Polygon",
    "Replacement Cost",
    "Premise Area",
    "Floor Count",
    "Asset Use",
    "Asset Type",
    "Age Category",
    "Structure Category",
    "Roof Type",
    "Wall Type",
    "Roof Shape",
    "Fortified Foundations",
    "Flood Elevation Structure Height",
    "Basement Presence",
    "Outdoor Space",
]

# Rename UPRN to match template
df.rename(columns={"UPRN": "Property Identifier"}, inplace=True)

# Create lists of missing and extra columns in .xlsx data, drop and add
missing_cols = [col for col in required_cols if col not in df.columns]
extra_cols = [col for col in df.columns if col not in required_cols]
df.drop(columns=extra_cols, inplace=True)
for col in missing_cols:
    df[col] = pd.NA

# Reorder to match template order
df = df[required_cols]

# Save to .csv to use for API data pull
df.to_csv("../data/api_csv_input.csv", index=False)
