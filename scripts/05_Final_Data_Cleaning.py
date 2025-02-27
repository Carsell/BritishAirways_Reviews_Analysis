import pandas as pd
import numpy as np
import airportsdata

# ----
# 1) Imports & Setup
# ----
# Load city coordinates from worldcities.csv
city_data = pd.read_csv("worldcities.csv")
city_coords = {(row["city"], row["iso2"]): (row["lat"], row["lng"]) 
               for _, row in city_data.dropna(subset=["iso2"]).iterrows()}

# Load IATA airport data for conversion
iata_dict = airportsdata.load("IATA")

def iata_to_city(iata_code):
    """Convert IATA code to city name and country code."""
    if not iata_code or len(str(iata_code)) != 3 or not str(iata_code).isupper():
        return (iata_code, None)
    airport = iata_dict.get(iata_code, {})
    return (airport.get("city", iata_code), airport.get("country", None))

def get_location(city_name, country_code=None):
    """Retrieve latitude and longitude using city name and country code."""
    if not city_name or city_name == "Unknown Route":
        return (None, None)
    
    # Normalize city name
    city_name = city_name.strip().title()
    
    # Map airport-specific names to cities
    airport_mappings = {
        "Heathrow": "London",
        "London City": "London",
        "London Heat": "London"  # Add if seen in your data
    }
    city_name = airport_mappings.get(city_name, city_name)
    
    # Match with country code if provided
    if country_code and (city_name, country_code) in city_coords:
        return city_coords[(city_name, country_code)]
    # Fallback: match city name alone
    for (city, cc), coords in city_coords.items():
        if city == city_name:
            return coords
    # Fallback for missing cities (e.g., manual mappings)
    custom_mappings = {
        "Rio De Janeiro": ("BR", -22.9068, -43.1729),  # Approximate coordinates
        "Las Vegas": ("US", 36.1699, -115.1398)         # Approximate coordinates
    }
    if city_name in custom_mappings:
        country, lat, lon = custom_mappings[city_name]
        return (lat, lon)
    return (None, None)

# ----
# 2) Load Review Data
# ----
df = pd.read_csv("raw_ba_reviews_with_star_ratings.csv")

# Check for place column and print sample values for debugging
if "place" in df.columns:
    print("Place column exists. Sample values:")
    print(df["place"].head(10))
else:
    print("Place column does not exist.")

# ----
# 3) Data Cleaning
# ----
df["author"] = df["author"].fillna("Anonymous")
pred_cols = ["pred_aircraft", "pred_traveller_type", "pred_seat_type", "pred_route"]
df[pred_cols] = df[pred_cols].replace("Not specified", np.nan)
df["verified"] = df["verified"].map({"Verified": True, "Not Verified": False})
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df.dropna(subset=["content"], inplace=True)
df["overall_rating"] = df["overall_rating"].astype("category")
df["pred_star_ratings"] = df["pred_star_ratings"].str.extract(r'(\d)').astype(float)
df.drop_duplicates(subset=["content", "author", "date"], keep="first", inplace=True)

# ----
# 4) Convert IATA Codes and Extract Routes
# ----
df["route_city"] = df["pred_route"].fillna("Unknown Route")

def convert_route(route):
    if " to " not in route or route == "Unknown Route":
        return route, None, None
    origin, dest = route.split(" to ")
    origin_city, origin_country = iata_to_city(origin.strip())
    dest_city, dest_country = iata_to_city(dest.strip())
    return f"{origin_city} to {dest_city}", origin_country, dest_country

# Apply conversion and split country codes
df[["route_city", "origin_country_code", "dest_country_code"]] = pd.DataFrame(
    df["route_city"].apply(convert_route).tolist(), index=df.index
)

# Extract origin and destination cities
df["origin_city"] = df["route_city"].apply(lambda x: x.split(" to ")[0] if " to " in str(x) else None)
df["dest_city"] = df["route_city"].apply(lambda x: x.split(" to ")[1] if " to " in str(x) else None)

# Use place column for country codes if available, otherwise use IATA-derived codes
if "place" in df.columns:
    df["place_country_code"] = df["place"].apply(
        lambda x: x.split(",")[-1].strip().upper() if isinstance(x, str) and "," in x else None
    )
    # Prioritize place-derived country codes, fall back to IATA-derived
    df["origin_country_code"] = df["origin_country_code"].combine_first(df["place_country_code"])
    df["dest_country_code"] = df["dest_country_code"].combine_first(df["place_country_code"])

# Apply coordinate lookup with country codes
df["origin_coords"] = df.apply(lambda row: get_location(row["origin_city"], row["origin_country_code"]), axis=1)
df["dest_coords"] = df.apply(lambda row: get_location(row["dest_city"], row["dest_country_code"]), axis=1)

# Split coordinates into lat/lon
df["origin_lat"], df["origin_lon"] = zip(*df["origin_coords"])
df["dest_lat"], df["dest_lon"] = zip(*df["dest_coords"])

# ----
# 5) Save Final Dataset
# ----
df.to_csv("cleaned_ba_reviews_with_geodata.csv", index=False)

# Debugging output
print(df[["route_city", "origin_city", "dest_city", "origin_country_code", "dest_country_code", 
         "origin_lat", "origin_lon", "dest_lat", "dest_lon"]].head(10))

# ----
# 6) Check for Missing Cities in worldcities.csv
# ----
missing_cities = ["Rio De Janeiro", "Las Vegas"]
for city in missing_cities:
    found = any(city in c for c, _ in city_coords.keys())
    print(f"{city} found in worldcities.csv: {found}")