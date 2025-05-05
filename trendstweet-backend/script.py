from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from uuid import uuid4
from datetime import datetime
from pymongo import MongoClient
from flask import Flask, request, jsonify
import time
from flask_cors import CORS
import requests

# Load environment variables
load_dotenv()

# Get environment variables
PROXY = os.getenv('PROXY_URL')
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
TWITTER_UNAME = os.getenv('TWITTER_UNAME')

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://trendstwitt-selenium-wbaj.vercel.app"}})

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["Trendingtweets"]
trends_collection = db["trends"]

# Function to get current IP address
def get_current_ip():
    try:
        response = requests.get("https://httpbin.org/ip")
        return response.json()['origin']
    except requests.RequestException as e:
        print(f"Error fetching IP: {e}")
        return "Could not fetch IP"

# Script to scrape trends from Twitter
def runscript():
    # Set up Edge WebDriver
    options = EdgeOptions()

    # Set the location for Microsoft Edge WebDriver on your machine
    options.use_chromium = True  # Since Edge is Chromium-based
    options.add_argument("--headless")  # Use headless mode if needed
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")  # Disable GPU for headless mode

    # Optional: Use proxy if provided
    if PROXY:
        options.add_argument(f'--proxy-server={PROXY}')

    # Specify the path to your Edge WebDriver (adjust this path if needed)
    driver_path = r"C:\path\to\msedgedriver.exe"  # Replace with your actual path to msedgedriver.exe

    # Initialize the Edge WebDriver
    driver = webdriver.Edge(service=EdgeService(driver_path), options=options)

    try:
        # Open Twitter login page
        driver.get('https://x.com/i/flow/login')
        print("Waiting for login form to load...")

        # Wait for the username input field
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'text')))

        # Input login credentials
        username_field = driver.find_element(By.NAME, 'text')
        username_field.send_keys(TWITTER_USERNAME)

        next_button = driver.find_element(By.XPATH, '//button[@role="button" and .//span[text()="Next"]]')
        next_button.click()

        # Input login Uname (if the username field is present)
        username_present = WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'text')))

        if username_present:
            username = driver.find_element(By.NAME, 'text')
            username.send_keys(TWITTER_UNAME)
            next_button = driver.find_element(By.XPATH, '//button[@role="button" and .//span[text()="Next"]]')
            next_button.click()
        else:
            print("Username field not found. Skipping to password entry.")

        # Wait for the password input field
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.NAME, 'password')))
        password_field = driver.find_element(By.NAME, 'password')
        password_field.send_keys(TWITTER_PASSWORD, Keys.RETURN)

        print("Waiting for the home page to load...")
        driver.get("https://twitter.com/explore/tabs/trending")

        time.sleep(5)

        # Use BeautifulSoup to parse the HTML
        soup = BeautifulSoup(driver.page_source, "html.parser")
        trending_topics_text = []

        try:
            # Find all sections with the class "css-175oi2r"
            trending_sections = soup.find_all("div", class_="css-175oi2r")
            if not trending_sections:
                print("No trending topics found.")
            else:
                # Iterate through each section to find "span" elements with the class "r-18u37iz"
                for section in trending_sections:
                    spans = section.find_all("span", class_="r-18u37iz")
                    trending_topics_text.extend([span.get_text() for span in spans])

                topics = []

                # Print the top 5 trending topics
                current_ip = get_current_ip()
                if trending_topics_text:
                    print("Top 5 Trending Topics:")
                    for idx, topic in enumerate(trending_topics_text[:5], start=1):
                        topics.append(topic)
                        print(f"{idx}. {topic}")
                    data = {
                        "_id": str(uuid4()),  # Use uuid for unique ID
                        "Trend1": topics[0],
                        "Trend2": topics[1],
                        "Trend3": topics[2],
                        "Trend4": topics[3],
                        "Trend5": topics[4],
                        "IP": current_ip,
                        "Date": datetime.now().isoformat()
                    }
                    result = trends_collection.insert_one(data)
                    print(f"Data inserted with ID: {result.inserted_id}")
                    return topics
                else:
                    print("No text found for trending topics.")

        except Exception as e:
            print(f"Error while extracting trending topics: {e}")

    except Exception as e:
        print(f"Error during script execution: {e}")

    finally:
        driver.quit()

# Route to execute the script
@app.route('/runscript', methods=['GET'])
def run_script():
    try:
        # Get credentials from query parameters
        username = request.args.get('username')
        uname = request.args.get('uname')
        password = request.args.get('password')

        # Update environment variables for runtime (not storing in .env file)
        os.environ["TWITTER_USERNAME"] = username
        os.environ["TWITTER_UNAME"] = uname
        os.environ["TWITTER_PASSWORD"] = password

        result = runscript()
        return jsonify({"data": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to fetch trending topics from MongoDB
@app.route('/fetchtopic', methods=['GET'])
def fetchtopic():
    try:
        # Fetch trends sorted by date
        results = trends_collection.find().sort("Date", -1)

        topics = []
        for result in results:
            result.pop('_id', None)  # Remove _id from results
            topics.append(result)

        return jsonify({"data": topics}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Start Flask app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
