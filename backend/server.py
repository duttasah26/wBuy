from flask import Flask, request, jsonify
from dotenv import load_dotenv
from scraper import RedditScraper, GooglePlacesScraper
from flask_cors import CORS
import os, json, requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize scrapers
reddit_scraper = RedditScraper(debug=True)
google_places_scraper = GooglePlacesScraper()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"

@app.route('/api/analyze', methods=['GET'])
def analyze():
    category = request.args.get('category')
    query = request.args.get('query')
    location = request.args.get('location')

    if category == "food":
        # Format search query
        reddit_results = scrape_reddit(query, location)
        # google_results = scrape_google_places(query, location)
        analysis = perplexity_analysis(reddit_results)
        return analysis

    elif category == "product":
        results = scrape_reddit(query, location)
        analysis = perplexity_analysis(results)
        return analysis

    elif category == "location":
        reddit_results = scrape_reddit(query, location)
        google_results = scrape_google_places(query, location)
        analysis = perplexity_analysis(results)
        return analysis

def scrape_reddit(query, location):
    try:
        posts = reddit_scraper.search_reddit(query, location, limit=100)

        # If no posts were found, try a more generic search
        if len(posts) == 0:
            return {"message": "Error."}
        
        return {"message": f"Found {len(posts)} posts", "data": posts}

    except Exception as e:
        app.logger.error(f"Error in Reddit scraping: {str(e)}")
        return jsonify({"error": f"Failed to scrape Reddit: {str(e)}"}), 500


def scrape_google_places(query, location):
    # Perform scraping
    places = google_places_scraper.search_and_store_places(query, location)

    # Convert ObjectId to string for JSON serialization
    for place in places:
        place['_id'] = str(place['_id'])

    return places


def perplexity_analysis(comments):
    print(json.dumps(comments))

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": f"""Analyze this Reddit data and extract the most valuable information.

    Return a JSON object with this exact structure:
    {{
      "recommendations": [
        {{
          "name": "Product or service name",
          "link": "Direct purchase link if available",
          "quoted_reviews": [
            "Direct quote from Reddit comment 1",
            "Direct quote from Reddit comment 2",
            "Direct quote from Reddit comment 3",
            "Direct quote from Reddit comment 4",
            "Direct quote from Reddit comment 5"
          ],
          "sentiment": "positive/negative/mixed",
          "key_features": ["feature 1", "feature 2", "feature 3"]
        }}
      ]
    }}

    Important guidelines:
    
Only include products/services that are explicitly mentioned and reviewed
Use EXACT quotes from the Reddit comments, do not paraphrase
Include purchase links only if they appear in the data
Focus on the most frequently mentioned products/services
Ensure the JSON is properly formatted with no errors
             Return a maximum of 5 recommendations for the user."""},
            {"role": "user", "content": json.dumps(comments)}
        ]
    }

    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)

    print(response.json()["choices"][0]["message"]["content"])

    return "ok"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
