# 05_Final_Data_Cleaning.py

# ----
# 1) Imports
# ----
import pandas as pd
import numpy as np
import airportsdata

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

# ----
# 6) Save final data
# ----
df_raw.to_csv("cleaned_ba_reviews_final.csv", index=False)
print("✅ Final cleaned data saved to 'cleaned_ba_reviews_final.csv'.")
