from flask import Flask, request, jsonify
from dotenv import load_dotenv
from scraper import RedditScraper, GooglePlacesScraper
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize scrapers
reddit_scraper = RedditScraper(debug=True)
google_places_scraper = GooglePlacesScraper()

@app.route('/api/reddit', methods=['GET'])
def scrape_reddit():
    try:
        # Get parameters from request
        query = request.args.get('query', '')
        location = request.args.get('location', '')

        if not query:
            return jsonify({"error": "Query parameter is required"}), 400

        # Format search query
        search_term = f"Best {query} in {location}" if location else query

        posts = reddit_scraper.search_reddit(search_term, limit=10)


        # If no posts were found, try a more generic search
        if len(posts) == 0:
            return jsonify({"message": "Error."})
        
        return jsonify({"message": f"Found {len(posts)} posts", "data": posts})

    except Exception as e:
        app.logger.error(f"Error in Reddit scraping: {str(e)}")
        return jsonify({"error": f"Failed to scrape Reddit: {str(e)}"}), 500


@app.route('/api/google-places', methods=['GET'])
def scrape_google_places():
    # Get parameters from request
    query = request.args.get('query', '')
    location = request.args.get('location', '')

    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    # Create search query
    search_query = f"{query} in {location}" if location else query

    # Clear existing data for this query
    db['google_places'].delete_many({'search_query': search_query})

    # Perform scraping
    google_places_scraper.search_and_store_places(query, location)

    # Get top 5 places with all data
    places = list(db['google_places'].find({'search_query': search_query}).sort('rating', -1).limit(5))

    # Convert ObjectId to string for JSON serialization
    for place in places:
        place['_id'] = str(place['_id'])

    return jsonify(places)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
