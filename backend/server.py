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

    if not query:
            return jsonify({"error": "Query parameter is required"}), 400
    
    # Format search query
    search_term = f"Best {query} in {location}" if location else query

    if category == "food":
        results = scrape_reddit(search_term)
        analysis = perplexity_analysis(results)
        return analysis

    elif category == "service":
        results = scrape_google_places(query, location)
        analysis = perplexity_analysis(results)
        return analysis

def scrape_reddit(search_term):
    try:
        posts = reddit_scraper.search_reddit(search_term, limit=10)

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
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "Return the top 3 most relevant comments."},
            {"role": "user", "content": json.dumps(comments)}
        ]
    }

    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)

    print(response.json()["choices"][0]["message"]["content"])

    return "ok"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
