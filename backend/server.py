from flask import Flask, request, jsonify
from dotenv import load_dotenv
from scraper import RedditScraper, GooglePlacesScraper
from flask_cors import CORS
import os, json, requests, re

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

#route for api/analyze 
@app.route('/api/analyze', methods=['GET'])
def analyze():

    category = request.args.get('category')
    query = request.args.get('query')
    location = request.args.get('location')

#if category=food; then scrap both reddit and google, combine and analyze
#if category=product; then scrap only reddit, analyse
#if category=location; then scrap reddit&google, combine and analyse

    if category == "food":
        # Format search query
        reddit_results = scrape_reddit(query, location, category)
        google_results = scrape_google_places(query, location)
        combined_results = {
        "reddit": reddit_results,
        "google_places": google_results
            }
        analysis = perplexity_analysis_combined(combined_results)
        return analysis

    elif category == "product":
        results = scrape_reddit(query, location, category)
        analysis = perplexity_analysis(results)
        return analysis

    elif category == "location":
        reddit_results = scrape_reddit(query, location, category)
        google_results = scrape_google_places(query, location)
        combined_results = {
        "reddit": reddit_results,
        "google_places": google_results
            }
        analysis = perplexity_analysis_combined(combined_results)
        return analysis

def scrape_reddit(query, location, category):
    try:
        posts = reddit_scraper.search_reddit(query, location, category,limit=20)

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
    places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
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
            {"role": "system", "content": """Analyze this Reddit data and extract the most valuable information.

    Return a JSON object with this exact structure:
    {
      "recommendations": [
    {
      "name": "Place or product name",
      "link": "Direct link if available",
      "photo_url": "Find the location's photo url from GOOGLE PLACES JSON",
      "quotes": [
        "One of the comments, either from Reddit or Google, that you deem most valuable.",
        "Another one of the comments, either from Reddit or Google, that you deem most valuable.",
        "A third comment, either from Reddit or Google, that you deem most valuable."
      ],
      "rating": "Average rating if available (e.g., 4.5/5)",
      "key_features": ["feature 1", "feature 2", "feature 3"]
    }
  ]
    }

    Important guidelines:
- Only include items explicitly mentioned and reviewed
- Use EXACT quotes, do not paraphrase
- Prioritize REVIEWS, WE NEED REVIEWS FROM EITHER GOOGLE OR REDDIT
- Include links only if they appear in the data
- Include photo URLs from Google Places if available
- Include Google ratings when available
- Match Reddit comments to Google Places where possible
- Focus on the most frequently mentioned items
- Ensure the JSON is properly formatted
- Return a maximum of 5 recommendations
- Return ONLY a JSON object. No ```json at the start or anything like that."""},
            {"role": "user", "content": json.dumps(comments)}
        ]
    }

    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
    response_json = response.json()
    
    response_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")

    # Remove potential triple backticks and language identifiers
    cleaned_text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", response_text.strip())

    try:
        final_json = json.loads(cleaned_text)  # Now parse the cleaned JSON string
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API", "cleaned_response": cleaned_text}

    return final_json


def perplexity_analysis_combined(combined_data):
    print(json.dumps(combined_data))

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": """Analyze this data and extract the most valuable information.

Return a JSON object with this exact structure:
{
  "recommendations": [
    {
      "name": "Place or product name",
      "link": "Direct link if available",
      "photo_url": "Find the location's photo url from GOOGLE PLACES JSON",
      "quotes": [
        "One of the comments, either from Reddit or Google, that you deem most valuable.",
        "Another one of the comments, either from Reddit or Google, that you deem most valuable.",
        "A third comment, either from Reddit or Google, that you deem most valuable."
      ],
      "rating": "Average rating if available (e.g., 4.5/5)",
      "key_features": ["feature 1", "feature 2", "feature 3"]
    }
  ]
}

Important guidelines:
- Only include items explicitly mentioned and reviewed
- Use EXACT quotes, do not paraphrase
- Prioritize REVIEWS, WE NEED REVIEWS FROM EITHER GOOGLE OR REDDIT
- Include links only if they appear in the data
- Include photo URLs from Google Places if available
- Include Google ratings when available
- Match Reddit comments to Google Places where possible
- Focus on the most frequently mentioned items
- Ensure the JSON is properly formatted
- Return a maximum of 5 recommendations
- Return ONLY a JSON object. No ```json at the start or anything like that."""},
            {"role": "user", "content": json.dumps(combined_data)}
        ]
    }

    response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
    response_json = response.json()
    
    response_text = response_json.get("choices", [{}])[0].get("message", {}).get("content", "No response")

    # Remove potential triple backticks and language identifiers
    cleaned_text = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", response_text.strip())

    try:
        final_json = json.loads(cleaned_text)  # Now parse the cleaned JSON string
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from API", "cleaned_response": cleaned_text}

    return final_json


if __name__ == '__main__':
    app.run(debug=True, port=5000)
