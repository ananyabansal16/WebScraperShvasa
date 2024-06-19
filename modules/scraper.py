import random
import time
import re
from datetime import datetime
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from classifier import is_question
from webdriver_manager.chrome import ChromeDriverManager

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36",
]

def init_webdriver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    options.add_argument('--verbose')

    driver_path = '/usr/local/bin/chromedriver'
    driver = webdriver.Chrome(service=Service(driver_path), options=options)
    driver.set_page_load_timeout(30)
    return driver

def get_questions_from_google(driver, website, keyword, num_questions=10):
    url = f"https://www.google.com/search?q=site:{website}.com+{keyword}"
    questions = []
    counter = 0
    start = 0
    retries = 3

    while counter < num_questions and retries > 0:
        try:
            driver.get(url)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.expected-class')))
            # time.sleep(random.uniform(3, 7))
            response = driver.page_source
            retries = 3
        except Exception as e:
            print(f"Error fetching the data: {e}")
            retries -= 1
            if retries == 0:
                print("Max retries reached. Exiting.")
                break
            print(f"Retrying... {retries} attempts left.")
            continue

        soup = BeautifulSoup(response, 'html.parser')
        all_data = soup.find_all("div", {"class": "g"})
        for data in all_data:
            link = data.find('a').get('href')
            title = data.find('h3', {"class": "DKV0Md"}).text

            description_data = data.find('div', {"class": "VwiC3b"})
            description = description_data.text if description_data else ""

            date_published = None
            if description:
                match = re.search(r"(\d{1,2} [A-Za-z]+ \d{4})|(\d{1,2} \w+ \d{4})|(\d{4})", description)
                if match:
                    date_str = match.group(0)
                    try:
                        if len(date_str) == 4:
                            date_published = datetime.strptime(date_str, '%Y').date()
                        else:
                            date_published = datetime.strptime(date_str, '%d %B %Y').date()
                    except ValueError:
                        try:
                            date_published = datetime.strptime(date_str, '%d %b %Y').date()
                        except ValueError:
                            date_published = None

            if is_question(title) and '...' not in title:
                questions.append({"title": title, "link": link, "description": description, "date_published": date_published})
                counter += 1

            if counter >= num_questions:
                break

        if counter >= num_questions:
            break

        start += 10
        url = f"https://www.google.com/search?q=site:{website}.com+{keyword}&start={start}"

    return questions



def test_scraper():
    driver = init_webdriver()
    website = "Quora"  # Replace with the website you want to scrape
    keyword = "Pink"  # Replace with the keyword you want to search for
    num_questions = 15
    questions = get_questions_from_google(driver, website, keyword, num_questions)  # Start from 0 questions extracted
    print(questions)

if __name__ == "__main__":
    test_scraper()
