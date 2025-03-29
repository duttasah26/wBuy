from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
from bson import ObjectId

# Import your scraper classes
from scraper import RedditScraper, GooglePlacesScraper

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize MongoDB connection
mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
db_name = os.getenv('MONGO_DB_NAME', 'reddit_data')
mongo_client = MongoClient(mongo_uri)
db = mongo_client[db_name]

# Perplexity API configuration
PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def format_reddit_data(posts):
    """Format Reddit data for Perplexity API input"""
    if not posts:
        return "No Reddit data available."

    formatted_data = "REDDIT DATA:\n\n"

    for i, post in enumerate(posts[:10]):  # Limit to 10 posts to avoid token limits
        formatted_data += f"Post {i + 1}: {post.get('title', 'No title')}\n"
        formatted_data += f"Subreddit: r/{post.get('subreddit', 'unknown')}\n"
        formatted_data += f"Score: {post.get('score', 0)}, Comments: {post.get('num_comments', 0)}\n"

        # Add post content if available
        if post.get('selftext') and len(post['selftext']) > 0:
            # Truncate long posts
            selftext = post['selftext']
            if len(selftext) > 500:
                selftext = selftext[:500] + "... [truncated]"
            formatted_data += f"Content: {selftext}\n"

        # Add top comments
        formatted_data += "Top comments:\n"
        for j, comment in enumerate(post.get('comments', [])[:5]):  # Limit to 5 comments per post
            comment_text = comment.get('body', '')
            if comment_text:
                if len(comment_text) > 200:
                    comment_text = comment_text[:200] + "... [truncated]"
                formatted_data += f"- {comment_text} (Score: {comment.get('score', 0)})\n"

        formatted_data += "\n" + "-" * 50 + "\n\n"

    return formatted_data


def format_google_places_data(places):
    """Format Google Places data for Perplexity API input"""
    if not places:
        return "No Google Places data available."

    formatted_data = "GOOGLE PLACES DATA:\n\n"

    for i, place in enumerate(places[:5]):  # Limit to 5 places
        formatted_data += f"Place {i + 1}: {place.get('name', 'Unknown place')}\n"
        formatted_data += f"Address: {place.get('address', 'No address')}\n"
        formatted_data += f"Rating: {place.get('rating', 'N/A')}/5 ({place.get('total_ratings', 0)} ratings)\n"

        # Add reviews
        formatted_data += "Reviews:\n"
        for j, review in enumerate(place.get('reviews', [])[:5]):  # Limit to 5 reviews per place
            review_text = review.get('text', '')
            if review_text:
                if len(review_text) > 200:
                    review_text = review_text[:200] + "... [truncated]"
                formatted_data += f"- Rating {review.get('rating', 'N/A')}/5: {review_text}\n"

        formatted_data += "\n" + "-" * 50 + "\n\n"

    return formatted_data


def perplexity_analyze(query, data_text, analysis_type, location=None):
    """Send data to Perplexity AI for analysis"""

    # Create location context if provided
    location_context = f" in {location}" if location else ""

    # Build the system prompt based on analysis type
    if analysis_type in ['product', 'service']:
        system_prompt = f"""You are an expert product analyst. Analyze the provided data about {query} and create a comprehensive analysis. 
Focus on extracting insights from actual user reviews and comments. Include:
1. A brief summary of overall sentiment (positive/negative/neutral)
2. Top 5 most frequently mentioned features or aspects
3. At least 5s DIRECT QUOTES from reviewers (both positive and negative)
4. Related products that were mentioned
5. Common issues or complaints
6. Standout positive feedback

Format your response as valid JSON with these fields: 
summary, top_features, positive_quotes, negative_quotes, related_products, common_issues, positive_highlights.
Each quote must be a direct quote from the provided data and include the source (Reddit or Google Places).
Only use information from the provided data."""

    else:  # place, restaurant, location
        system_prompt = f"""You are an expert place reviewer. Analyze the provided data about {query}{location_context} and create a comprehensive analysis.
Focus on extracting insights from actual reviews and comments. Include:
1. A brief summary of overall sentiment (positive/negative/neutral)
2. Top 5 most frequently mentioned features or aspects
3. At least 5 DIRECT QUOTES from reviewers (both positive and negative)
4. Similar or related places that were mentioned
5. Common issues or complaints
6. Standout positive feedback

Format your response as valid JSON with these fields:
summary, top_features, positive_quotes, negative_quotes, related_places, common_issues, positive_highlights.
Each quote must be a direct quote from the provided data and include the source (Reddit or Google Places).
Only use information from the provided data."""

    # Create the user content with data
    user_content = f"Here is data about {query}{location_context} from multiple sources:\n\n{data_text}\n\nAnalyze this data according to the instructions."

    # Create Perplexity API payload
    # Create Perplexity API payload
    payload = {
        "model": "sonar",
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        "max_tokens": 1500,
        "temperature": 0.2,
        "top_p": 0.9,
        "search_domain_filter": [""],
        "return_images": False,
        "return_related_questions": False,
        "stream": False,
        "presence_penalty": 0,
        "frequency_penalty": 1,
        "response_format": {"type": "json_object"},
        "web_search_options": {"search_context_size": "high"}
    }

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(PERPLEXITY_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        perplexity_response = response.json()

        # Extract the response content
        if 'choices' in perplexity_response and perplexity_response['choices']:
            analysis_json = perplexity_response['choices'][0]['message']['content']

            # Try to parse the JSON response
            try:
                analysis = json.loads(analysis_json)
                return analysis
            except json.JSONDecodeError:
                # If it's not valid JSON, return the raw text
                return {"error": "Failed to parse Perplexity response as JSON", "raw_response": analysis_json}
        else:
            return {"error": "Invalid response format from Perplexity API"}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error connecting to Perplexity API: {str(e)}"}


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint to analyze reviews based on query, location and type"""
    data = request.json

    if not data:
        return jsonify({"error": "No data provided"}), 400

    query = data.get('query')
    location = data.get('location')
    analysis_type = data.get('type', 'product').lower()

    if not query:
        return jsonify({"error": "Query is required"}), 400

    # Gather data from MongoDB
    all_data_text = ""

    # Get Reddit data
    reddit_scraper = RedditScraper(debug=False)

    # Adjust search query based on type and location
    if analysis_type in ['place', 'restaurant', 'location'] and location:
        reddit_search_term = f"{query} {location}"
    else:
        reddit_search_term = query

    reddit_posts = reddit_scraper.get_data_for_perplexity(topic=reddit_search_term)
    reddit_data_text = format_reddit_data(reddit_posts)
    all_data_text += reddit_data_text + "\n\n"

    # Get Google Places data for place types or if location is provided
    if analysis_type in ['place', 'restaurant', 'location'] or location:
        places_scraper = GooglePlacesScraper(mongo_client)

        if location:
            places_search_term = f"{query} in {location}"
        else:
            places_search_term = query

        places = places_scraper.get_data_for_perplexity(places_search_term)
        places_data_text = format_google_places_data(places)
        all_data_text += places_data_text

    # If no data found, return error
    if all_data_text.strip() == "":
        return jsonify({
            "error": "No data found for this query in MongoDB. Please run the scrapers first."
        }), 404

    # Send data to Perplexity for analysis
    analysis = perplexity_analyze(query, all_data_text, analysis_type, location)

    # Create response
    response = {
        "query": query,
        "location": location,
        "type": analysis_type,
        "timestamp": datetime.now().isoformat(),
        "sources": {
            "reddit": {
                "posts_count": len(reddit_posts),
                "comments_count": sum(len(post.get('comments', [])) for post in reddit_posts)
            }
        },
        "analysis": analysis
    }

    # Add Google Places stats if applicable
    if analysis_type in ['place', 'restaurant', 'location'] or location:
        response["sources"]["google_places"] = {
            "places_count": len(places) if 'places' in locals() else 0,
            "reviews_count": sum(len(place.get('reviews', [])) for place in places) if 'places' in locals() else 0
        }

    # Save the analysis to MongoDB for future reference
    analysis_collection = db['perplexity_analyses']
    analysis_collection.insert_one(response)

    # Convert ObjectId to string before returning
    response = dict(response)
    for key, value in response.items():
        if isinstance(value, ObjectId):
            response[key] = str(value)
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, ObjectId):
                    value[k] = str(v)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, ObjectId):
                            item[k] = str(v)

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)