import argparse
import requests
import json
import time
import os
from dotenv import load_dotenv

# Import your scraper classes
from scraper import RedditScraper, GooglePlacesScraper  # Adjust import based on your file structure

load_dotenv()


def run_scrapers(query, location=None, data_type='product', limit=100):
    """Run scrapers based on query, location and type"""
    print(f"\n{'=' * 50}")
    print(f"Step 1: Running scrapers for: {query}")
    if location:
        print(f"Location: {location}")
    print(f"Type: {data_type}")
    print(f"{'=' * 50}\n")

    # Initialize MongoDB connection
    from pymongo import MongoClient
    mongo_uri = os.getenv('MONGO_CONNECTION_STRING', 'mongodb://localhost:27017/')
    db_name = os.getenv('MONGO_DB_NAME', 'reddit_data')
    mongo_client = MongoClient(mongo_uri)

    results = {
        'reddit': 0,
        'google_places': 0
    }

    # Run Reddit scraper for all types
    try:
        print("\nRunning Reddit scraper...")
        reddit_scraper = RedditScraper(debug=True)

        # For products, search the product name
        # For places, search the place name + location
        if data_type in ['place', 'restaurant', 'location'] and location:
            search_term = f"{query} {location}"
        else:
            search_term = query

        posts_count = reddit_scraper.search_reddit(search_term, limit=limit)
        results['reddit'] = posts_count
        print(f"Collected {posts_count} Reddit posts")
    except Exception as e:
        print(f"Error running Reddit scraper: {e}")

    # Run Google Places scraper for place/restaurant/service types or if location is provided
    if data_type in ['place', 'restaurant', 'location', 'service'] or location:
        try:
            print("\nRunning Google Places scraper...")
            places_scraper = GooglePlacesScraper(mongo_client)
            places = places_scraper.search_and_store_places(query, location)
            results['google_places'] = len(places)
            print(f"Collected data for {len(places)} places from Google")
        except Exception as e:
            print(f"Error running Google Places scraper: {e}")

    print(f"\nScraping complete!")
    return results


def analyze_data(query, location=None, data_type='product'):
    """Send a request to the Perplexity analyzer API and get results"""
    print(f"\n{'=' * 50}")
    print(f"Step 2: Analyzing data for: {query}")
    if location:
        print(f"Location: {location}")
    print(f"Type: {data_type}")
    print(f"{'=' * 50}\n")

    url = "http://localhost:5000/api/analyze"

    payload = {
        "query": query,
        "type": data_type
    }

    if location:
        payload["location"] = location

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        results = response.json()

        print("\nAnalysis completed successfully!")

        # Save results to a file
        filename = f"{query.replace(' ', '_')}_{data_type}_analysis.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {filename}")

        # Print a summary
        print("\nSummary:")
        if "analysis" in results and "summary" in results["analysis"]:
            print(f"- {results['analysis']['summary']}")

        print("\nTop features/aspects:")
        if "analysis" in results and "top_features" in results["analysis"]:
            for feature in results["analysis"]["top_features"]:
                print(f"- {feature}")

        print("\nSample quotes:")
        if "analysis" in results and "positive_quotes" in results["analysis"]:
            print("Positive:")
            for quote in results["analysis"]["positive_quotes"][:2]:
                print(f'  "{quote}"')

        if "analysis" in results and "negative_quotes" in results["analysis"]:
            print("\nNegative:")
            for quote in results["analysis"]["negative_quotes"][:2]:
                print(f'  "{quote}"')

        return results

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to API: {e}")
        return None


def full_process(query, location=None, data_type='product', limit=100):
    """Run the full process: scraping and analysis"""
    # Run scrapers
    run_scrapers(query, location, data_type, limit)

    # Wait a bit for MongoDB to update
    print("\nWaiting a few seconds for database to update...")
    time.sleep(3)

    # Run analysis
    analyze_data(query, location, data_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the full process of scraping and analyzing data')
    parser.add_argument('--query', '-q', required=True, help='Search query (product or place name)')
    parser.add_argument('--location', '-l', help='Location (city, state, etc.)')
    parser.add_argument('--type', '-t', choices=['product', 'place', 'restaurant', 'service'],
                        default='product', help='Type of search')
    parser.add_argument('--limit', type=int, default=10, help='Limit for Reddit posts')
    parser.add_argument('--analyze-only', action='store_true', help='Skip scraping and only run analysis')

    args = parser.parse_args()

    if args.analyze_only:
        analyze_data(args.query, args.location, args.type)
    else:
        full_process(args.query, args.location, args.type, args.limit)