import time
import random
import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from fake_useragent import UserAgent
from utils import wait_for_element
from database import pet_exists, save_pet  # Import the necessary functions

# Initialize WebDriver with random User-Agent for Dogs
def initialize_driver(pet_type="dog"):
    options = webdriver.ChromeOptions()
    ua = UserAgent()
    user_agent = ua.random  # Randomize user-agent
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--headless")  # Run browser in headless mode

    if pet_type == "dog":
        driver = webdriver.Chrome(options=options)
        driver.get('https://napaluchu.waw.pl/zwierzeta/znalazly-dom/?pet_breed=-1&pet_sex=0&pet_weight=0&pet_age=0&pet_date_from=&pet_date_to=&pet_name=&submit-form=')
    else:
        driver = webdriver.Chrome(options=options)
        driver.get('https://napaluchu.waw.pl/zwierzeta/znalazly-dom/?pet_page=1&pet_species=2&pet_weight=0&pet_age=0')
        
    return driver

# Function to get the current timestamp as a string
def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Function to check internet connection
def check_internet_connection(url='http://www.google.com/', timeout=5):
    try:
        requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False

# Safe function to handle retries and delays when loading pages
def safe_get(driver, url):
    while True:
        wait_time = 5  # Initial wait time in seconds
        while not check_internet_connection():
            print(f"[{get_timestamp()}] No internet connection, waiting for {wait_time} seconds...")
            time.sleep(wait_time)
            wait_time = min(wait_time * 2, 300)  # Double the wait time, max 5 minutes
            print(f"[{get_timestamp()}] Retrying connection...")

        try:
            driver.get(url)
            return True  # Successfully loaded the page
        except TimeoutException:
            print(f"[{get_timestamp()}] Timeout error, retrying...")
            time.sleep(random.uniform(10, 20))  # Random retry delay between 10 to 20 seconds
        except WebDriverException as e:
            if "net::ERR_NAME_NOT_RESOLVED" in str(e):
                print(f"[{get_timestamp()}] DNS error (net::ERR_NAME_NOT_RESOLVED), retrying...")
            else:
                print(f"[{get_timestamp()}] WebDriver error: {e}, retrying...")
            time.sleep(random.uniform(10, 20))  # Random retry delay between 10 to 20 seconds
        except Exception as e:
            print(f"[{get_timestamp()}] Unexpected error: {e}, retrying...")
            time.sleep(random.uniform(10, 20))  # Random retry delay between 10 to 20 seconds

# Scrape individual dog details from the dog page
def scrape_dog_details(dog_url):
    driver = initialize_driver(pet_type="dog")
    dog_details = {}

    # Visit individual dog page
    if not safe_get(driver, dog_url):
        print(f"[{get_timestamp()}] Failed to load {dog_url}")
        driver.quit()
        return None

    # Wait for the pet details block to load
    wait_for_element(driver, By.CSS_SELECTOR, '.petdetails')

    # Extract additional details from the individual page
    try:
        # Extracting dog id (from the <small> tag) and other details
        try:
            dog_details['id'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Nr')]/strong").text.strip()
        except Exception:
            dog_details['id'] = None

        # Extracting name from the h2 inside the auto-container div
        try:
            name_element = driver.find_element(By.XPATH, "//div[contains(@class, 'auto-container')]//h2")
            h2_text = name_element.text.strip() if name_element else ""
            dog_id = dog_details['id']
            dog_details['name'] = h2_text.replace(dog_id, "").strip() if dog_id and dog_id in h2_text else h2_text
        except Exception:
            dog_details['name'] = None
        
        # Extract breed, age, gender, weight, status, found date, admission and release date when available, (figure out how to do this in a better way)
        try:
            dog_details['breed'] = driver.find_element(By.XPATH, "//li[contains(text(), 'W typie rasy')]/strong").text.strip()
        except Exception:
            dog_details['breed'] = None
        
        try:
            dog_details['age'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Wiek')]/strong").text.strip()
        except Exception:
            dog_details['age'] = None

        try:
            dog_details['gender'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Płeć')]/strong").text.strip()
        except Exception:
            dog_details['gender'] = None

        try:
            dog_details['weight'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Waga')]/strong").text.strip()
        except Exception:
            dog_details['weight'] = None

        try:
            dog_details['status'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Status')]/strong").text.strip()
        except Exception:
            dog_details['status'] = None

        try:
            dog_details['found'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Znaleziony')]/strong").text.strip()
        except Exception:
            dog_details['found'] = None

        try:
            dog_details['admitted'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Przyjęty')]/strong").text.strip()
        except Exception:
            dog_details['admitted'] = None

        try:
            dog_details['released'] = driver.find_element(By.XPATH, "//li[contains(text(), 'Wydany')]/strong").text.strip()
        except Exception:
            dog_details['released'] = None

        # Extracting image URL
        try:
            img_element = driver.find_element(By.CSS_SELECTOR, "img.pet-detail-main-image")
            dog_details['image_url'] = img_element.get_attribute("src") if img_element else None
        except Exception:
            dog_details['image_url'] = None

    except Exception as e:
        print(f"[{get_timestamp()}] Error extracting details for {dog_url}: {e}")

    driver.quit()
    return dog_details

def scrape_dogs(max_pets=None, start_page=1):
    driver = initialize_driver(pet_type="dog")

    dogs = []
    page = start_page
    unique_pets_count = 0

    while max_pets is None or unique_pets_count < max_pets:
        print(f"[{get_timestamp()}] Scraping page {page}...")

        # Safe function call to handle page load with retries
        if not safe_get(driver, f'https://napaluchu.waw.pl/zwierzeta/znalazly-dom/?pet_page={page}&pet_species=1&pet_weight=0&pet_age=0'):
            print(f"[{get_timestamp()}] Failed to load page {page}, skipping.")
            page += 1
            continue

        # Wait for the pet blocks to load
        wait_for_element(driver, By.CSS_SELECTOR, '.pet-block')

        # Find all pet blocks
        dog_elements = driver.find_elements(By.CSS_SELECTOR, '.pet-block')
        total_dogs = len(dog_elements)

        # Extract dog details
        for index, dog in enumerate(dog_elements, start=1):
            while True:
                try:
                    # Extract ID
                    id = dog.find_element(By.CSS_SELECTOR, 'small').text.strip()

                    # Check if the pet ID already exists in the database
                    if pet_exists(id, "dog"):
                        print(f"[{get_timestamp()}] Pet with ID {id} already exists in the database, skipping.")
                        break

                    dog_url = dog.find_element(By.CSS_SELECTOR, '.pets-list-pet-name a').get_attribute('href')

                    # Call scrape_dog_details to get more info
                    dog_details = scrape_dog_details(dog_url)

                    if dog_details:  # Only add the dog to the list if the details were successfully extracted
                        dog_data = {
                            'id': id,
                            'species': 'dog',
                            **dog_details,  # Merge archive info with individual page details
                            'color': '',
                            'url': dog_url,
                        }
                        dogs.append(dog_data)

                        # Save the dog data to the database
                        save_pet(dog_data)
                        unique_pets_count += 1

                        print(f"[{get_timestamp()}] Scraping dog {unique_pets_count}/{max_pets} from page {page}...")

                        if max_pets is not None and unique_pets_count >= max_pets:
                            break

                    # Delay between individual pet requests
                    time.sleep(10)  # Respect crawl-delay of 10 seconds
                    break

                except Exception as e:
                    print(f"[{get_timestamp()}] Error processing dog element: {e}")
                    time.sleep(10)  # Wait before retrying
                    continue

        # Check if there's a next page
        next_button = driver.find_elements(By.LINK_TEXT, 'Następna')
        if next_button:
            page += 1
            time.sleep(10)  # Respect crawl-delay of 10 seconds
        else:
            print(f"[{get_timestamp()}] No more pages to scrape.")
            break

    driver.quit()
    return dogs