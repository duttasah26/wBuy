import praw
import pymongo
from datetime import datetime
from pymongo import MongoClient
import time
import os
from dotenv import load_dotenv
import sys
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from dotenv import load_dotenv
import json


load_dotenv()

# REDDIT SCRAPER

class RedditScraper:
    def __init__(self, debug=True):
        self.debug = debug

        try:
            # Initialize Reddit API
            self.reddit = praw.Reddit(
                client_id=os.getenv('REDDIT_CLIENT_ID'),
                client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
                user_agent=os.getenv('REDDIT_USER_AGENT', 'ProductResearchScraper v1.0')
            )

            # Check if connection is successful
            subreddit = self.reddit.subreddit("python")
            list(subreddit.hot(limit=1))
            print("Reddit API connection successful!")

        except Exception as e:
            print(f"Failed to initialize Reddit API: {e}")
            raise


#THIS IS WHAT WE USE TO RUN REDDIT SCRAPPER
    def search_reddit(self, query, location, limit=10, sort='relevance', time_filter='all'):
        search_query = f"Best {query} in {location}"
        print(f"Searching Reddit for: '{search_query}'")

        posts_data = []

        try:
            # Search for posts
            search_results = self.reddit.subreddit('all').search(
                search_query,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )

            # Process each post
            for post in search_results:
                if (query.lower() not in post.title.lower()) and (location.lower() not in post.title.lower()):
                    continue  # Skip irrelevant posts

                post_data = {
                    'post_id': post.id,
                    'title': post.title,
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'num_comments': post.num_comments,
                    'search_topic': search_query,
                    'comments': self.get_comments(post)
                }

                posts_data.append(post_data)

                # Reddit API rate limit
                time.sleep(0.5)

            print(f"Successfully processed {len(posts_data)} posts.")

        except Exception as e:
            print(f"Error searching Reddit: {e}")

        return posts_data

    def get_comments(self, post, limit=100):
        comments_data = []

        try:
            post.comments.replace_more(limit=10)
            comment_list = post.comments.list()[:limit]

            for comment in comment_list:
                comment_data = {
                    'comment_id': comment.id,
                    'body': comment.body,
                    'score': comment.score,
                }

                comments_data.append(comment_data)

        except Exception as e:
            print(f"Error fetching comments: {e}")

        return comments_data

    def get_data_for_perplexity(self, topic, limit=10):
        return self.search_reddit(topic, limit=limit)

#GooglePlaces SCRAPER

class GooglePlacesScraper:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')

        if not self.api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")

    def search_place_id(self, search_query):
        """Search for places using a query and return their Place IDs"""
        google_places_search_url = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
        params = {
            'key': self.api_key,
            'query': search_query
        }

        # Send the request to the Places Search API
        response = requests.get(google_places_search_url, params=params)

        if response.status_code == 200:
            places_data = response.json()
            place_ids = []
            for result in places_data.get('results', []):
                place_ids.append({
                    'name': result.get('name'),
                    'place_id': result.get('place_id')
                })
            return place_ids
        else:
            print(f"Error fetching Place IDs: {response.status_code}")
            return []

    def get_reviews(self, place_id, search_query=None):
        """Fetch reviews for a place using the Place ID"""
        google_places_details_url = 'https://maps.googleapis.com/maps/api/place/details/json'
        params = {
            'key': self.api_key,
            'placeid': place_id,
            'fields': 'name,rating,formatted_address,review,user_ratings_total,types,photos,url'
        }

        # Send the request to the Places Details API
        response = requests.get(google_places_details_url, params=params)

        if response.status_code == 200:
            place_data = response.json()
            result = place_data.get('result', {})

            # Prepare data for return
            place_info = {
                'place_id': place_id,
                'name': result.get('name', ''),
                'formatted_address': result.get('formatted_address', ''),
                'rating': result.get('rating', 0),
                'user_ratings_total': result.get('user_ratings_total', 0),
                'types': result.get('types', []),
                'google_maps_url': result.get('url', ''),
                'search_query': search_query,
                'retrieved_at': datetime.now().isoformat(),
            }

            # Add reviews
            reviews = []
            for review in result.get('reviews', []):
                reviews.append({
                    'author_name': review.get('author_name', ''),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', ''),
                    'time': review.get('time', 0),
                    'relative_time_description': review.get('relative_time_description', '')
                })

            place_info['reviews'] = reviews
            return place_info
        else:
            print(f"Error fetching place details: {response.status_code}")
            return None


# THIS IS WHAT WE USE TO RUN THIS SCRAPER
    def search_and_store_places(self, search_query, location=None):
        """Search for places and return their details and reviews"""
        if location:
            full_query = f"{search_query} in {location}"
        else:
            full_query = search_query

        places = self.search_place_id(full_query)
        results = []

        if places:
            print(f"Found {len(places)} places for query: {full_query}")
            for place in places[:10]:  # Limit to 10 places
                place_data = self.get_reviews(place['place_id'], search_query=full_query)
                if place_data:
                    results.append(place_data)
                time.sleep(0.5)  # Respect API rate limits

        return results

    def get_data_for_perplexity(self, search_query, location=None):
        """Search for places and return their data for analysis"""
        return self.search_and_store_places(search_query, location)