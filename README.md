### 🛫 British Airways Trustpilot Review Analysis

A Comprehensive Data Pipeline for Scraping, Processing, and Analyzing British Airways Customer Reviews
This repository contains a structured Python pipeline for collecting and analyzing British Airways Trustpilot reviews. The project leverages Selenium for web scraping, Natural Language Processing (NLP), and fuzzy matching techniques to extract meaningful insights from customer feedback.

## 📂 Project Structure
Each script is modularized for clarity and ease of use.

## File	Description
01_scrape_reviews.py	Scrapes customer reviews from Trustpilot using Selenium and saves them to CSV.
02_fuzzy_matching.py	Uses fuzzy string matching to extract key details (e.g., aircraft, traveler type, seat type, and routes).
03_sentiment_analysis.py	Applies sentiment analysis (positive/negative) and star rating prediction using a transformer-based NLP model.
04_exploratory_analysis.py	Extracts topics using LDA, finds frequent bigrams, and generates a word cloud of customer sentiment.
05_final_data_cleaning.py	Cleans and standardizes the dataset, including route standardization using IATA airport codes.
requirements.txt	List of Python dependencies needed for the project.

## 📂 Data Files

| File Name | Description |
|-----------|-------------|
| `raw_ba_reviews.csv` | Scraped reviews from Trustpilot |
| `raw_ba_reviews_with_fuzzy_matches.csv` | Reviews with extracted keywords (aircraft, route, etc.) |
| `raw_ba_reviews_with_sentiment.csv` | Reviews with sentiment labels (positive/negative) |
| `raw_ba_reviews_with_star_ratings.csv` | Reviews with predicted star ratings |
| `cleaned_ba_reviews_final.csv` | Fully cleaned dataset for analysis |


## 🚀 Setup & Installation

1️⃣ Clone the repository
git clone https://github.com/Carsell/BritishAirways_Reviews_Analysis.git
cd BritishAirways_Reviews_Analysis

2️⃣ Install dependencies
Make sure you have Python 3.8+ installed. Then, install required libraries:
pip install -r requirements.txt

Alternatively, if using conda, create an environment:
conda create --name ba_reviews python=3.9
conda activate ba_reviews
pip install -r requirements.txt

3️⃣ Ensure ChromeDriver is installed
This project uses Selenium for web scraping, so you need Google Chrome and ChromeDriver installed.

Download ChromeDriver
Add it to your system PATH, or specify its location in webdriver.Chrome(executable_path="path/to/chromedriver")

## 🛠️ How to Run the Scripts
Each script should be run in sequence.

1️⃣ Scrape the Reviews
python 01_scrape_reviews.py
Output: raw_ba_reviews.csv (raw scraped reviews)

2️⃣ Extract Aircraft, Seat Type, and Routes via Fuzzy Matching
python 02_fuzzy_matching.py
Input: raw_ba_reviews.csv
Output: raw_ba_reviews_with_fuzzy_matches.csv (with aircraft, traveler type, seat, route extracted)

3️⃣ Perform Sentiment & Star Rating Analysis
python 03_sentiment_analysis.py
Input: raw_ba_reviews_with_fuzzy_matches.csv
Output: raw_ba_reviews_with_star_ratings.csv

4️⃣ Run Exploratory Data Analysis
python 04_exploratory_analysis.py
Input: raw_ba_reviews_with_star_ratings.csv
Output: Generates LDA topics, bigrams, and a word cloud visualization.

5️⃣ Clean & Standardize the Data
python 05_final_data_cleaning.py
Input: raw_ba_reviews_with_star_ratings.csv
Output: cleaned_ba_reviews_final.csv (fully processed and structured dataset)

## 📊 Key Features

✅ Automated Web Scraping – Uses Selenium to collect reviews dynamically.
✅ Natural Language Processing (NLP) – Uses transformer-based models for sentiment & star rating predictions.
✅ Fuzzy Matching – Extracts keywords (routes, seat types, aircraft) from text.
✅ Topic Modeling (LDA) – Identifies recurring themes in customer feedback.
✅ Data Cleaning & Standardization – Converts IATA airport codes to city names, removes duplicates, and handles missing values.

## 📌 Example Insights

🔹 What are customers most unhappy about?
🔹 Which aircraft types receive the worst reviews?
🔹 How do business class vs economy class experiences compare?
🔹 What routes generate the most complaints?
🔹 How accurate is Trustpilot’s star rating compared to NLP-based rating predictions?

## ✨ Future Enhancements

📈 Automate daily scraping using a scheduled script
🤖 Train a custom sentiment model for airline reviews
🌍 Expand to other airlines for industry-wide comparison
🗺️ Geographical analysis of customer reviews based on airport locations
🤝 Contributing
🔹 Fork the repository
🔹 Create a feature branch (git checkout -b new-feature)
🔹 Commit changes (git commit -m "Added feature")
🔹 Push to branch (git push origin new-feature)
🔹 Open a Pull Request 🚀

## 📜 License

This project is licensed under the MIT License – feel free to use and modify.

📧 Contact

If you have any questions, feel free to reach out!

Olaoluwa Olukoya

📧 Email: carsellolukoya@gmail.com

🔗 LinkedIn: https://www.linkedin.com/in/olaoluwa-olukoya-msc-0a1778140/

