# 02_Fuzzy_Keyword_Matching.py

# ----
# 1) Imports
# ----
import pandas as pd
from rapidfuzz import fuzz

# ----
# 2) Load "keyword" dataset and raw reviews
# ----
# This assumes you have a CSV with known keywords for aircraft, traveler_type, seat_type, route
df_keywords = pd.read_csv("ba_reviews.csv")  
df_raw = pd.read_csv("raw_ba_reviews.csv")  # from the scraping notebook

# Build your lists of keywords
aircraft_list = list(df_keywords['aircraft'].dropna().unique())
traveller_list = list(df_keywords['traveller_type'].dropna().unique())
seat_list = list(df_keywords['seat_type'].dropna().unique())
route_list = list(df_keywords['route'].dropna().unique())

# ----
# 3) Prepare the raw data
# ----
# Lowercase the content for consistent matching
df_raw["content"] = df_raw["content"].str.lower().str.strip()

# Create new columns to store predictions
df_raw["pred_aircraft"] = "Not specified"
df_raw["pred_traveller_type"] = "Not specified"
df_raw["pred_seat_type"] = "Not specified"
df_raw["pred_route"] = "Not specified"

# ----
# 4) Define a fuzzy matching function
# ----
def find_best_fuzzy_match(text: str, candidates: list, threshold=70) -> str:
    """
    Returns the highest scoring candidate via partial fuzzy match
    if its score >= threshold, else None.
    """
    if not isinstance(text, str) or not text.strip():
        return None

    best_candidate = None
    best_score = 0
    text_lower = text.lower()

    for kw in candidates:
        kw_lower = kw.lower()
        score = fuzz.partial_ratio(kw_lower, text_lower)
        if score > best_score:
            best_score = score
            best_candidate = kw

    if best_score >= threshold:
        return best_candidate
    return None

# ----
# 5) Apply fuzzy matching to each row
# ----
for i, row in df_raw.iterrows():
    content_text = row["content"]  # already lower/stripped

    found_aircraft  = find_best_fuzzy_match(content_text, aircraft_list)
    found_traveller = find_best_fuzzy_match(content_text, traveller_list)
    found_seat      = find_best_fuzzy_match(content_text, seat_list)
    found_route     = find_best_fuzzy_match(content_text, route_list)

    if found_aircraft:
        df_raw.at[i, "pred_aircraft"] = found_aircraft
    if found_traveller:
        df_raw.at[i, "pred_traveller_type"] = found_traveller
    if found_seat:
        df_raw.at[i, "pred_seat_type"] = found_seat
    if found_route:
        df_raw.at[i, "pred_route"] = found_route

# ----
# 6) Save the updated dataset
# ----
df_raw.to_csv("raw_ba_reviews_with_fuzzy_matches.csv", index=False)

# Quick preview
print(df_raw.head(10))
