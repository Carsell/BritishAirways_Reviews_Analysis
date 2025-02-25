# 04_Exploratory_Analysis.py

# ----
# 1) Imports
# ----
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# (If you want bigram analysis separately)
from sklearn.feature_extraction.text import CountVectorizer

# ----
# 2) Load data (with star ratings or whichever stage you like)
# ----
df_raw = pd.read_csv("raw_ba_reviews_with_star_ratings.csv")

# ==========================================
# PART A: Topic modeling (LDA)
# ==========================================
vectorizer = CountVectorizer(stop_words="english", max_features=1000)
X = vectorizer.fit_transform(df_raw["content"].dropna())

lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(X)

feature_names = vectorizer.get_feature_names_out()
for topic_idx, topic in enumerate(lda.components_):
    print(f"Topic {topic_idx}:")
    print(" ".join(
        [feature_names[i] for i in topic.argsort()[:-10 - 1:-1]]
    ))
    print("")

# ==========================================
# PART B: Bigram analysis
# ==========================================
bigram_vectorizer = CountVectorizer(
    ngram_range=(2,2),
    stop_words="english",
    max_features=20
)
X2 = bigram_vectorizer.fit_transform(df_raw["content"].dropna())
bigrams = bigram_vectorizer.get_feature_names_out()
print("Top bigrams:")
print(bigrams)

# ==========================================
# PART C: WordCloud
# ==========================================
text = " ".join(str(review) for review in df_raw["content"].dropna())
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)

plt.figure(figsize=(10,5))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
