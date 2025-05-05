from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from dotenv import load_dotenv, set_key
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
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(proxy={"server": PROXY} if PROXY else None)
        page = context.new_page()

    try:
        # Open Twitter login page
        page.goto('https://x.com/i/flow/login')
        print("Waiting for login form to load...")

        # Wait for the username input field
        page.wait_for_selector('input[name="text"]', timeout=60000)
        username_field = page.locator('input[name="text"]')
        username_field.fill(TWITTER_USERNAME)

        next_button = page.locator('button[role="button"] span:text("Next")')
        next_button.click()

        # Wait for and enter uname (if asked)
        try:
            page.wait_for_selector('input[name="text"]', timeout=5000)
            uname_field = page.locator('input[name="text"]')
            uname_field.fill(TWITTER_UNAME)
            next_button.click()
        except:
            print("No secondary username prompt.")

        # Enter password
        page.wait_for_selector('input[name="password"]', timeout=60000)
        password_field = page.locator('input[name="password"]')
        password_field.fill(TWITTER_PASSWORD)
        password_field.press("Enter")

        print("Waiting for the home page to load...")
        page.wait_for_url('**/home', timeout=60000)

        page.goto("https://twitter.com/explore/tabs/trending")
        time.sleep(5)

        # BeautifulSoup parsing (same as your current logic)
        soup = BeautifulSoup(page.content(), "html.parser")
        trending_topics_text = []

        trending_sections = soup.find_all("div", class_="css-175oi2r")
        for section in trending_sections:
            spans = section.find_all("span", class_="r-18u37iz")
            trending_topics_text.extend([span.get_text() for span in spans])

        topics = []
        current_ip = get_current_ip()

        if trending_topics_text:
            print("Top 5 Trending Topics:")
            for idx, topic in enumerate(trending_topics_text[:5], start=1):
                topics.append(topic)
                print(f"{idx}. {topic}")
            data = {
                "_id": str(uuid4()),
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
        print(f"Error during script execution: {e}")

    finally:
        browser.close()

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
