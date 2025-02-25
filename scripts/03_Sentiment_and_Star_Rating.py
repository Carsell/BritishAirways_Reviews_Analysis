# 03_Sentiment_and_Star_Rating.ipynb

# ----
# 1) Imports
# ----
import pandas as pd
from transformers import pipeline

# ----
# 2) Load the data with fuzzy matches
# ----
df_raw = pd.read_csv("raw_ba_reviews_with_fuzzy_matches.csv")

# ==========================================
# PART A: Simple (binary) sentiment analysis
# ==========================================
sentiment_pipeline = pipeline("sentiment-analysis")

binary_sentiments = []
for text in df_raw["content"]:
    # Truncate text if extremely long (avoid model token limit issues)
    result = sentiment_pipeline(text[:512])[0]
    binary_sentiments.append(result["label"])  # "POSITIVE" or "NEGATIVE"

df_raw["pred_sentiment"] = binary_sentiments

# Save intermediate
df_raw.to_csv("raw_ba_reviews_with_sentiment.csv", index=False)
print("Saved binary sentiment predictions to 'raw_ba_reviews_with_sentiment.csv'.")

# ==========================================
# PART B: Star-rating prediction
# ==========================================
star_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

star_ratings = []
for text in df_raw["content"]:
    # Again truncate
    result = star_pipeline(text[:512])[0]
    star_ratings.append(result["label"])  # e.g. "4 stars"

df_raw["pred_star_ratings"] = star_ratings

# ----
# 3) Save final result with star ratings
# ----
df_raw.to_csv("raw_ba_reviews_with_star_ratings.csv", index=False)
print("Saved star ratings to 'raw_ba_reviews_with_star_ratings.csv'.")

# Quick check
print(df_raw[["content", "pred_sentiment", "pred_star_ratings"]].head(10))
