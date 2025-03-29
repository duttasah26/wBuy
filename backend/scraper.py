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

            # Check if CONNECTIONS are succesful
            try:
                # subreddit connection check
                subreddit = self.reddit.subreddit("python")
                list(subreddit.hot(limit=1))
                print("Reddit API connection successful!")
            except Exception as e:
                print(f"Reddit API connection test failed: {e}")
                raise
        except Exception as e:
            print(f"Failed to initialize Reddit API: {e}")
            raise

        try:
            # Initialize MongoDB connection
            mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGO_DB_NAME', 'reddit_data')

            self.mongo_client = MongoClient(mongo_uri)
            self.db = self.mongo_client[db_name]

            # Verify MongoDB connection
            server_info = self.mongo_client.server_info()
            print(f"MongoDB connection successful! Version: {server_info.get('version', 'unknown')}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def search_reddit(self, topic, limit=10, sort='relevance', time_filter='all'):
        collection = self.db['posts']

        # Creating index for faster searches
        collection.create_index([('post_id', pymongo.ASCENDING)], unique=True)

        posts_count = 0
        search_query = topic

        print(f"Searching Reddit for: '{search_query}'")

        try:
            # Search for posts
            search_results = self.reddit.subreddit('all').search(
                search_query,
                sort=sort,
                time_filter=time_filter,
                limit=limit
            )

            # Process each post
            for i, post in enumerate(search_results):
                # Convert post data to dictionary
                post_data = {
                    'post_id': post.id,
                    'title': post.title,
                    'author': str(post.author) if post.author else '[deleted]',
                    'subreddit': post.subreddit.display_name,
                    'created_utc': datetime.fromtimestamp(post.created_utc),
                    'score': post.score,
                    'upvote_ratio': post.upvote_ratio,
                    'url': post.url,
                    'permalink': f"https://www.reddit.com{post.permalink}",
                    'selftext': post.selftext,
                    'num_comments': post.num_comments,
                    'is_original_content': post.is_original_content,
                    'retrieved_at': datetime.now(),
                    'search_topic': topic
                }

                #Get comments
                post_data['comments'] = self.get_comments(post)

                #Insert into MongoDB (upsert to avoid duplicates)
                try:
                    collection.update_one(
                        {'post_id': post_data['post_id']},
                        {'$set': post_data},
                        upsert=True
                    )
                    posts_count += 1
                except pymongo.errors.DuplicateKeyError:
                    pass

                # Reddit API rate limit
                time.sleep(0.5)

            print(f"Successfully processed {posts_count} posts.")

        except Exception as e:
            print(f"Error searching Reddit: {e}")
            import traceback
            traceback.print_exc()

        return posts_count

    def get_comments(self, post, limit=100):
        #getting comments from posts
        comments_data = []

        try:
            post.comments.replace_more(limit=10)
            comment_list = post.comments.list()[:limit]

            for comment in comment_list:
                comment_data = {
                    'comment_id': comment.id,
                    'author': str(comment.author) if comment.author else '[deleted]',
                    'body': comment.body,
                    'created_utc': datetime.fromtimestamp(comment.created_utc),
                    'score': comment.score,
                    'is_submitter': comment.is_submitter,
                    'parent_id': comment.parent_id
                }

                comments_data.append(comment_data)

        except Exception as e:
            print(f"Error fetching comments: {e}")
            import traceback
            traceback.print_exc()

        return comments_data

    def get_data_for_perplexity(self, topic=None):
       #Retrieve all posts and comments for a topic to send to
        posts_collection = self.db['posts']

        query = {'search_topic': topic} if topic else {}

        # Get all posts with their comments
        posts = list(posts_collection.find(query))

        return posts

    def get_stats(self, topic=None):
        #Get statistics on collected data
        posts_collection = self.db['posts']

        query = {'search_topic': topic} if topic else {}

        # Count total comments
        pipeline = [
            {'$match': query},
            {'$project': {'comment_count': {'$size': {'$ifNull': ['$comments', []]}}}},
            {'$group': {'_id': None, 'total_comments': {'$sum': '$comment_count'}}}
        ]

        comments_result = list(posts_collection.aggregate(pipeline))
        total_comments = comments_result[0]['total_comments'] if comments_result else 0

        stats = {
            'total_posts': posts_collection.count_documents(query),
            'total_comments': total_comments,
            'subreddits': list(posts_collection.aggregate([
                {'$match': query},
                {'$group': {'_id': '$subreddit', 'count': {'$sum': 1}}},
                {'$sort': {'count': -1}},
                {'$limit': 10}
            ]))
        }

        return stats


#GOOGLE PLACES SCRAPER

class GooglePlacesScraper:
    def __init__(self, mongo_client=None):
        self.api_key = os.getenv('GOOGLE_API_KEY')

        # Set up MongoDB if not provided
        if mongo_client is None:
            mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
            db_name = os.getenv('MONGO_DB_NAME', 'reddit_data')
            self.mongo_client = MongoClient(mongo_uri)
            self.db = self.mongo_client[db_name]
        else:
            self.mongo_client = mongo_client
            self.db = mongo_client[os.getenv('MONGO_DB_NAME', 'reddit_data')]

        # Create collection for Google Places data
        self.places_collection = self.db['google_places']
        # Create index for faster searches
        self.places_collection.create_index([('place_id', pymongo.ASCENDING)], unique=True)
        self.places_collection.create_index([('search_query', pymongo.ASCENDING)])

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
            return None

    def get_reviews(self, place_id, search_query=None):
        """Fetch reviews for a place using the Place ID and store in MongoDB"""
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

            # Prepare data for MongoDB
            place_info = {
                'place_id': place_id,
                'name': result.get('name', ''),
                'address': result.get('formatted_address', ''),
                'rating': result.get('rating', 0),
                'total_ratings': result.get('user_ratings_total', 0),
                'types': result.get('types', []),
                'google_maps_url': result.get('url', ''),
                'search_query': search_query,
                'retrieved_at': datetime.now(),
            }

            # Add reviews
            reviews = []
            for review in result.get('reviews', []):
                reviews.append({
                    'author': review.get('author_name', ''),
                    'rating': review.get('rating', 0),
                    'text': review.get('text', ''),
                    'time': datetime.fromtimestamp(review.get('time', 0)),
                    'relative_time': review.get('relative_time_description', '')
                })

            place_info['reviews'] = reviews

            # Store in MongoDB
            try:
                self.places_collection.update_one(
                    {'place_id': place_id},
                    {'$set': place_info},
                    upsert=True
                )
                print(f"Stored data for place: {place_info['name']}")
                return place_info
            except Exception as e:
                print(f"Error storing place data: {e}")
                return None
        else:
            print(f"Error fetching place details: {response.status_code}")
            return None

    def search_and_store_places(self, search_query, location=None):
        """Search for places and store their details and reviews"""
        if location:
            full_query = f"{search_query} in {location}"
        else:
            full_query = search_query

        places = self.search_place_id(full_query)
        results = []

        if places:
            print(f"Found {len(places)} places for query: {full_query}")
            for place in places[:10]:
                place_data = self.get_reviews(place['place_id'], search_query=full_query)
                if place_data:
                    results.append(place_data)
                time.sleep(0.5)  # Respect API rate limits

        return results

    def get_data_for_perplexity(self, search_query=None):
        """Retrieve places data for a search query"""
        query = {'search_query': {"$regex": search_query, "$options": "i"}} if search_query else {}
        places = list(self.places_collection.find(query))
        return places




