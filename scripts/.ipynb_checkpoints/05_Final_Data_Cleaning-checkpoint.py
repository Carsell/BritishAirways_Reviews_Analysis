# 05_Final_Data_Cleaning.py

# ----
# 1) Imports
# ----
import pandas as pd
import numpy as np
import airportsdata
from geopy.geocoders import Nominatim
import time
# ----
# 2) Load the data from the star-ratings stage
# ----
df_raw = pd.read_csv("raw_ba_reviews_with_star_ratings.csv")

# ----
# 3) Basic cleanup
# ----
# a) Fill missing authors
df_raw["author"] = df_raw["author"].fillna("Anonymous")

# b) Convert "Not specified" -> NaN in these columns
pred_cols = ["pred_aircraft", "pred_traveller_type", "pred_seat_type", "pred_route"]
df_raw[pred_cols] = df_raw[pred_cols].replace("Not specified", np.nan)

# c) Verified to bool
df_raw["verified"] = df_raw["verified"].map({"Verified": True, "Not Verified": False})

# d) Convert date to datetime
df_raw["date"] = pd.to_datetime(df_raw["date"], errors="coerce")

# e) Drop rows if content is missing
df_raw = df_raw.dropna(subset=["content"])

# ----
# 4) Additional transformations
# ----
# Convert overall_rating to category
df_raw["overall_rating"] = df_raw["overall_rating"].astype("category")

# Convert "pred_star_ratings" from "5 stars" -> numeric
df_raw["pred_star_ratings"] = df_raw["pred_star_ratings"].str.extract(r'(\d)').astype(float)

# Drop duplicates
df_raw.drop_duplicates(subset=["content","author","date"], keep="first", inplace=True)

# Word count example
df_raw["word_count"] = df_raw["content"].apply(lambda x: len(str(x).split()))

# ----
# 5) Route standardization using IATA codes
# ----
# If your pred_route contains something like "LHR to JFK", convert to city names

# Replace empty strings with NaN
df_raw["pred_route"] = df_raw["pred_route"].str.strip().replace("", np.nan)
df_raw["pred_route"] = df_raw["pred_route"].fillna("Unknown Route")

iata_dict = airportsdata.load("IATA")

def convert_route(route):
    if pd.isna(route) or route == "Unknown Route":
        return "Unknown Route"
    try:
        origin_code, dest_code = route.split(" to ")
        origin_city = iata_dict.get(origin_code.strip(), {}).get("city", origin_code)
        dest_city   = iata_dict.get(dest_code.strip(), {}).get("city", dest_code)
        return f"{origin_city} to {dest_city}"
    except ValueError:
        return route

df_raw["pred_route"] = df_raw["pred_route"].apply(convert_route)

geolocator = Nominatim(user_agent="geoapiExercises")

def get_location(city_name):
    try:
        location = geolocator.geocode(city_name)
        if location:
            return (location.latitude, location.longitude)
        return (None, None)
    except:
        return (None, None)

# Convert routes to city names first
df["route_city"] = df["pred_route"].apply(convert_route)

# Get coordinates for each city
df["origin_coords"] = df["route_city"].apply(lambda x: get_location(x.split(" to ")[0]) if " to " in x else (None, None))
df["dest_coords"] = df["route_city"].apply(lambda x: get_location(x.split(" to ")[1]) if " to " in x else (None, None))

# Save the data
df.to_csv("cleaned_ba_reviews_with_geodata.csv", index=False)

# Preview
df[["route_city", "origin_coords", "dest_coords"]].head()
