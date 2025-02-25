# 01_Scrape_BA_Reviews.py

# ----
# 1) Imports
# ----
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import pandas as pd
import time
from datetime import datetime
import random

# ----
# 2) Optional debug flag and debug function
# ----
DEBUG = True

def debug_print(message):
    if DEBUG:
        print(f"DEBUG: {message}")

# ----
# 3) Set up Selenium driver
# ----
debug_print("Initializing Chrome options...")
chrome_options = Options()
# chrome_options.add_argument('--headless')  # Uncomment if you want headless browsing
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/120.0.6099.216 Safari/537.36'
)

try:
    driver = webdriver.Chrome(options=chrome_options)
    debug_print("Chrome driver initialized successfully.")
except Exception as e:
    debug_print(f"Failed to initialize Chrome driver: {e}")
    raise

# ----
# 4) Global variables and lists
# ----
base_url = "https://www.trustpilot.com/review/www.britishairways.com"
debug_print(f"Navigating to {base_url}...")
driver.get(base_url)

raw_reviews = []  # we’ll store each review as a dictionary

# ----
# 5) Scraping function
# ----
def scrape_page(url):
    global driver, raw_reviews
    
    try:
        debug_print(f"Scraping page: {url}")
        driver.get(url)

        # Wait for reviews to load
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, 'styles_reviewCardInner__UZk1x')
                )
            )
        except Exception as e:
            debug_print(f"Error waiting for reviews to load: {e}")
            return

        # Scroll to load all reviews
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        max_scrolls = 15
        while scroll_count < max_scrolls:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 6))  # random delay
            new_height = driver.execute_script("return document.body.scrollHeight")
            scroll_count += 1
            debug_print(f"Scroll attempt {scroll_count}, new height: {new_height}")
            if new_height == last_height:
                # Check how many reviews we have
                review_elements = driver.find_elements(By.CLASS_NAME, 'styles_reviewCardInner__UZk1x')
                if len(review_elements) >= 20:  # typically ~20 reviews per page
                    debug_print(f"Found {len(review_elements)} review elements, stopping scroll.")
                    break
                else:
                    debug_print("No additional reviews found, continuing scroll...")
            last_height = new_height

        # Parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        review_containers = soup.find_all('div', class_='styles_reviewCardInner__UZk1x')
        debug_print(f"Found {len(review_containers)} review containers on this page.")

        for review in review_containers:
            try:
                # --- Date of experience ---
                date_elem = review.find(
                    'p',
                    class_='typography_body-m__k2UI7 typography_appearance-default__t8iAq',
                    attrs={'data-service-review-date-of-experience-typography': 'true'}
                )
                if date_elem:
                    date_text = date_elem.text.strip()
                    if "Date of experience:" in date_text:
                        date_str = date_text.replace("Date of experience:", "").strip()
                    else:
                        date_str = date_text
                else:
                    time_elem = review.find('time', class_='data-service-review-date-time-ago')
                    if time_elem and 'datetime' in time_elem.attrs:
                        dt_str = time_elem['datetime'].split('T')[0]
                        date_str = datetime.strptime(dt_str, "%Y-%m-%d").strftime("%B %d, %Y")
                    else:
                        date_str = "Not specified"

                # --- Author name ---
                author_elem = review.find('span', class_='typography_heading-xxs__UmE9o typography_appearance-default__t8iAq')
                if author_elem:
                    author = author_elem.text.strip()
                else:
                    author_link = review.find('a', class_='link_internal__Eam_b link_wrapper__ahpyq styles_consumerDetails__DW9Hp')
                    if author_link:
                        author_span = author_link.find('span', class_='typography_heading-xxs__UmE9o')
                        author = author_span.text.strip() if author_span else "Unknown"
                    else:
                        author = "Unknown"

                # --- Location / place ---
                place_elem = review.find(
                    'div',
                    class_='typography_body-m__k2UI7 typography_appearance-subtle__PYOVM styles_detailsIcon__ch_FY'
                )
                if place_elem and place_elem.find('span'):
                    place = place_elem.find('span').text.strip()
                else:
                    place = "Not specified"

                # --- Review content ---
                content_elem = review.find(
                    'p',
                    class_='typography_body-l__v5JLj typography_appearance-default__t8iAq typography_color-black__wpn7m'
                )
                content = content_elem.text.strip() if content_elem else "No content"

                # --- Overall rating ---
                rating_elem = review.find('div', class_='star-rating_starRating__sdbkn star-rating_medium__Oj7C9')
                overall_rating = 0
                if rating_elem:
                    stars_img = rating_elem.find('img', alt=lambda x: x and 'star' in x.lower())
                    if stars_img and 'stars-' in stars_img['src']:
                        rating_str = stars_img['src'].split('stars-')[-1].split('.svg')[0]
                        overall_rating = int(rating_str)

                # --- Verified status ---
                verified = "Not Verified"
                if (review.find('div', class_='review-content-header__review-verified')
                    or review.find('span', class_='verified-badge')):
                    verified = "Verified"

                # Collect data
                raw_reviews.append({
                    "date": date_str,
                    "author": author,
                    "place": place,
                    "content": content,
                    "overall_rating": overall_rating,
                    "verified": verified
                })

            except Exception as e:
                debug_print(f"Error processing a review: {e}")
                continue

    except Exception as e:
        debug_print(f"Page scraping failed: {e}")
        # If you want to re-init the driver on crash, do so here
        # Otherwise, just pass or raise
        pass

# ----
# 6) Loop through pages
# ----
current_page = 1
max_pages = 555

while current_page <= max_pages:
    page_url = f"{base_url}?page={current_page}"
    scrape_page(page_url)

    # If we found no reviews, stop
    if len(raw_reviews) == 0:
        debug_print("No reviews found at all, stopping.")
        break

    # Attempt to find a "next" button
    try:
        next_button = driver.find_element(By.CLASS_NAME, 'pagination-link_next__NdSsd')
        if not next_button.is_enabled() or "disabled" in next_button.get_attribute("class"):
            debug_print("No more pages available, stopping.")
            break
    except Exception:
        debug_print("Pagination check failed, assuming no more pages.")
        break

    current_page += 1
    debug_print(f"Moving to page {current_page}...")
    time.sleep(random.uniform(5, 10))

# ----
# 7) Create a DataFrame from raw reviews and save
# ----
debug_print(f"Total raw reviews collected: {len(raw_reviews)}")
df_raw = pd.DataFrame(raw_reviews)

# Convert rating to int
df_raw['overall_rating'] = df_raw['overall_rating'].astype(int)

# Fill missing
df_raw.fillna("Not specified", inplace=True)

# Save
output_file = "raw_ba_reviews.csv"
df_raw.to_csv(output_file, index=False)
debug_print(f"Saved raw data to: {output_file}")

# ----
# 8) Clean up driver
# ----
driver.quit()
debug_print("Driver closed. Scraping done.")
