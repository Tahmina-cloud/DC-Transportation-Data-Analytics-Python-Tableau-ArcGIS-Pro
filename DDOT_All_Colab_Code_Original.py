# DDOT — COMPLETE ORIGINAL GOOGLE COLAB CODE (FAITHFUL EXPORT)
# Every nonempty code cell from Untitled4(2).ipynb appears below, in original order.
# This is an archival copy of Colab code, NOT a Windows runnable script.
# Colab-only files.upload(), files.download(), display(), and cell dependencies remain.
# Use DDOT_full_analysis_windows.py to reproduce the complete analysis on Windows.


# NOTEBOOK SECTION: # data processing


# ===== ORIGINAL COLAB CODE CELL 2 =====
import pandas as pd
from google.colab import files

uploaded = files.upload()

data = pd.read_csv(next(iter(uploaded)))

print(data.shape)
data.head()


# ===== ORIGINAL COLAB CODE CELL 4 =====
data["ApplicationDate"] = pd.to_datetime(data["ApplicationDate"])
data["IssueDate"] = pd.to_datetime(data["IssueDate"])

data["ApplicationTime"] = data["ApplicationDate"].dt.time
data["IssueTime"] = data["IssueDate"].dt.time

data["ApplicationDate"] = data["ApplicationDate"].dt.date
data["IssueDate"] = data["IssueDate"].dt.date

data[["ApplicationDate", "ApplicationTime", "IssueDate", "IssueTime"]].head()


# ===== ORIGINAL COLAB CODE CELL 6 =====
uploaded = files.upload()

data = pd.read_csv(next(iter(uploaded)))

print(data.shape)
data.head()

# NOTEBOOK SECTION: # **2026 permit filter by application or issued date **


# ===== ORIGINAL COLAB CODE CELL 8 =====
data["ApplicationDate"] = pd.to_datetime(data["ApplicationDate"])
data["IssueDate"] = pd.to_datetime(data["IssueDate"])

data_2026 = data[
    (data["ApplicationDate"] >= "2026-01-01") |
    (data["IssueDate"] >= "2026-01-01")
].copy()

print(len(data_2026))

# NOTEBOOK SECTION: type of permit filter


# ===== ORIGINAL COLAB CODE CELL 10 =====
data_filtered = data_2026[
    data_2026["EventTypeDescription"].isin([
        "Construction Staging Area",
        "Mobile Crane Work Zone"
    ])
].copy()

print(len(data_filtered))

# NOTEBOOK SECTION: companies


# ===== ORIGINAL COLAB CODE CELL 12 =====
companies = "DCWater|Pepco|Potomac Electric|Wash Gas"

data_utility = data_filtered[
    data_filtered["ApplicantCompany"].str.contains(
        companies, case=False, na=False
    )
].copy()

print(len(data_utility))


# ===== ORIGINAL COLAB CODE CELL 13 =====


data_utility.to_csv("DDOT_Filtered_Permits.csv", index=False)

files.download("DDOT_Filtered_Permits.csv")

# NOTEBOOK SECTION: **dataset filter done**

# NOTEBOOK SECTION: unique permit filter


# ===== ORIGINAL COLAB CODE CELL 17 =====
print(data_utility[
    ["TrackingNumber", "Latitude", "Longitude"]
].head(10))

print("Unique permits:", data_utility["TrackingNumber"].nunique())


# ===== ORIGINAL COLAB CODE CELL 18 =====

###test code

import requests

url = "https://rh.dcgis.dc.gov/dcgis/rest/services/DDOT/RoadwayBlocks/MapServer/exts/DdotLrsExtensions/getPointOnSubBlock"

params = {
    "x": data_utility.iloc[0]["Longitude"],
    "y": data_utility.iloc[0]["Latitude"],
    "inSR": 4326,
    "outSR": 4326,
    "routeType": "Street",
    "searchRadius": 100,
    "returnNearestMatchOnly": "true",
    "f": "json"
}

result = requests.get(url, params=params).json()

print(result)


# ===== ORIGINAL COLAB CODE CELL 19 =====
###test code

road_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/162/query"

key = result["pointOnSubBlocks"][0]["subBlockKey"]

params = {
    "where": f"SUBBLOCKKEY='{key}'",
    "outFields": "STREETNAME,FHWAFUNCTIONALCLASS",
    "returnGeometry": "false",
    "f": "json"
}

road = requests.get(road_url, params=params).json()

print(road)


# ===== ORIGINAL COLAB CODE CELL 20 =====
#### test code



import requests

# Two DDOT URLs
lrs_url = "https://rh.dcgis.dc.gov/dcgis/rest/services/DDOT/RoadwayBlocks/MapServer/exts/DdotLrsExtensions/getPointOnSubBlock"

road_url = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/162/query"

# First permit location
row = data_utility.iloc[0]

# Find nearest street
r = requests.get(lrs_url, params={
    "x": row["Longitude"],
    "y": row["Latitude"],
    "inSR": 4326,
    "outSR": 4326,
    "routeType": "Street",
    "searchRadius": 100,
    "returnNearestMatchOnly": "true",
    "f": "json"
}, timeout=30).json()

# Get street information
street = r["pointOnSubBlocks"][0]

print("Street:", street["routeName"])
print("SubBlockKey:", street["subBlockKey"])


# ===== ORIGINAL COLAB CODE CELL 21 =====
### test code


key = street["subBlockKey"]

r2 = requests.get(road_url, params={
    "where": f"SUBBLOCKKEY='{key}'",
    "outFields": "FHWAFUNCTIONALCLASS",
    "returnGeometry": "false",
    "f": "json"
}, timeout=30).json()

fhwa = r2["features"][0]["attributes"]["FHWAFUNCTIONALCLASS"]

print("FHWA Class:", fhwa)


# ===== ORIGINAL COLAB CODE CELL 23 =====
import pandas as pd
import requests

locations = data_utility[
    ["Latitude", "Longitude"]
].drop_duplicates()

print("Unique locations:", len(locations))

results = []

for i, (_, row) in enumerate(locations.iterrows()):

    road_name = None
    fhwa = None

    try:

        url1 = "https://rh.dcgis.dc.gov/dcgis/rest/services/DDOT/RoadwayBlocks/MapServer/exts/DdotLrsExtensions/getPointOnSubBlock"

        p1 = {
            "x": row["Longitude"],
            "y": row["Latitude"],
            "inSR": 4326,
            "outSR": 4326,
            "routeType": "Street",
            "searchRadius": 100,
            "returnNearestMatchOnly": "true",
            "f": "json"
        }

        r1 = requests.get(url1, params=p1, timeout=15).json()
        street = r1["pointOnSubBlocks"][0]

        road_name = street["routeName"]
        key = street["subBlockKey"]


        url2 = "https://maps2.dcgis.dc.gov/dcgis/rest/services/DCGIS_DATA/Transportation_WebMercator/MapServer/162/query"

        p2 = {
            "where": f"SUBBLOCKKEY='{key}'",
            "outFields": "FHWAFUNCTIONALCLASS",
            "returnGeometry": "false",
            "f": "json"
        }

        r2 = requests.get(url2, params=p2, timeout=15).json()
        fhwa = r2["features"][0]["attributes"]["FHWAFUNCTIONALCLASS"]

    except (KeyError, IndexError, requests.RequestException, ValueError):
        pass

    results.append([
        row["Latitude"],
        row["Longitude"],
        road_name,
        fhwa
    ])


    if (i + 1) % 100 == 0:
        print("Completed:", i + 1)

        pd.DataFrame(
            results,
            columns=["Latitude", "Longitude", "RoadName", "FHWAClass"]
        ).to_csv("Road_Progress.csv", index=False)


road_results = pd.DataFrame(
    results,
    columns=["Latitude", "Longitude", "RoadName", "FHWAClass"]
)

data_utility = data_utility.drop(
    columns=["RoadName", "FHWAClass", "HighestPriorityClass"],
    errors="ignore"
)

data_utility = data_utility.merge(
    road_results,
    on=["Latitude", "Longitude"],
    how="left"
)


data_utility["FHWAClass"] = pd.to_numeric(
    data_utility["FHWAClass"], errors="coerce"
)

data_utility["HighestPriorityClass"] = (
    data_utility.groupby("TrackingNumber")["FHWAClass"]
    .transform("min")
)


data_utility.to_csv("DDOT_Final_Enriched.csv", index=False)

print("Finished!")
print("Total rows:", len(data_utility))

data_utility[
    ["TrackingNumber", "RoadName", "FHWAClass", "HighestPriorityClass"]
].head(10)


# ===== ORIGINAL COLAB CODE CELL 24 =====


files.download("DDOT_Final_Enriched.csv")


# ===== ORIGINAL COLAB CODE CELL 25 =====
import pandas as pd
from google.colab import files

uploaded = files.upload()

data_utility = pd.read_csv("DDOT_Final_Enriched.csv")

print("Total records:", len(data_utility))
print("Missing FHWA:", data_utility["FHWAClass"].isna().sum())

data_utility.head()

# NOTEBOOK SECTION: missing FHWA


# ===== ORIGINAL COLAB CODE CELL 27 =====
print("Total rows:", len(data_utility))
print("Missing FHWA:", data_utility["FHWAClass"].isna().sum())
print("Missing RoadName:", data_utility["RoadName"].isna().sum())

# NOTEBOOK SECTION: mising information


# ===== ORIGINAL COLAB CODE CELL 29 =====
missing = data_utility[
    data_utility["FHWAClass"].isna() |
    data_utility["RoadName"].isna()
]

missing[
    ["TrackingNumber", "Latitude", "Longitude",
     "RoadName", "FHWAClass"]
]

# NOTEBOOK SECTION: alley check( no )


# ===== ORIGINAL COLAB CODE CELL 31 =====
alley_check = data_utility[
    data_utility["RoadName"].fillna("").str.contains(
        r"\bALLEY\b", case=False, regex=True
    )
]

print("Road names containing ALLEY:", len(alley_check))

display(
    alley_check[
        ["TrackingNumber", "RoadName", "FHWAClass"]
    ].head(10)
)


# ===== ORIGINAL COLAB CODE CELL 32 =====
print(
    data_utility[
        ["TrackingNumber", "RoadName", "FHWAClass"]
    ].head(10)
)


# ===== ORIGINAL COLAB CODE CELL 33 =====
print("Records with AlleyLength > 0:",
      (pd.to_numeric(data_utility["AlleyLength"], errors="coerce") > 0).sum())

print("Records with AlleyWidth > 0:",
      (pd.to_numeric(data_utility["AlleyWidth"], errors="coerce") > 0).sum())


# ===== ORIGINAL COLAB CODE CELL 34 =====
alley_records = data_utility[
    pd.to_numeric(data_utility["AlleyLength"], errors="coerce") > 0
]

print("Alley-related records:", len(alley_records))

display(
    alley_records[
        ["TrackingNumber", "RoadName", "FHWAClass",
         "AlleyLength", "AlleyWidth"]
    ].head(10)
)
