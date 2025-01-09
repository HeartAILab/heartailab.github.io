# fetch_tweets.py
import os
import sys
import tweepy
from dotenv import load_dotenv

# For YAML output
import yaml

# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET, BEARER_TOKEN]):
    print("Error: Missing one or more required Twitter credentials in .env")
    sys.exit(1)

client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)

def fetch_latest_tweets(user_id, max_results=5):
    """
    Fetch latest tweets from a given Twitter numeric user ID 
    and return the raw Tweepy Response object.
    """
    response = client.get_users_tweets(
        id=user_id,
        max_results=max_results,
        expansions=[
            "author_id",
            "attachments.media_keys",
            "referenced_tweets.id"
        ],
        tweet_fields=[
            "created_at",
            "text",
            "public_metrics",
            "author_id",
            "attachments",
            "referenced_tweets"
        ],
        user_fields=[
            "id",
            "name",
            "username",
            "profile_image_url",
            "verified"
        ],
        media_fields=[
            "type",
            "url",
            "preview_image_url",
            "public_metrics"
        ]
    )
    return response

def normalize_tweet_data(t):
    """
    Given a Tweepy Tweet object, return a dictionary
    with a consistent set of keys.
    """
    d = t.data.copy()
    return {
        "id": d.get("id", ""),
        "text": d.get("text", ""),
        "created_at": d.get("created_at", ""),
        "author_id": d.get("author_id", ""),
        "attachments": d.get("attachments", {}),
        "referenced_tweets": d.get("referenced_tweets", []),
        "public_metrics": d.get("public_metrics", {})
    }

def normalize_include_data(include_key, objects_list):
    """
    Convert each object in response.includes[include_key] into
    a dict with consistent keys.
    """
    normalized = []
    for obj in objects_list:
        data = obj.data.copy()

        if include_key == "users":
            normalized.append({
                "id": data.get("id", ""),
                "name": data.get("name", ""),
                "username": data.get("username", ""),
                "profile_image_url": data.get("profile_image_url", ""),
                "verified": data.get("verified", False)
            })
        elif include_key == "media":
            normalized.append({
                "media_key": data.get("media_key", ""),
                "type": data.get("type", ""),
                "url": data.get("url", ""),
                "preview_image_url": data.get("preview_image_url", ""),
                "public_metrics": data.get("public_metrics", {})
            })
        elif include_key == "tweets":
            normalized.append({
                "id": data.get("id", ""),
                "text": data.get("text", ""),
                "created_at": data.get("created_at", ""),
                "author_id": data.get("author_id", ""),
                "attachments": data.get("attachments", {}),
                "referenced_tweets": data.get("referenced_tweets", []),
                "public_metrics": data.get("public_metrics", {})
            })
        else:
            # fallback: store as-is
            normalized.append(data)

    return normalized

def main():
    handle = "ramseywehbemd"  # Replace with your handle
    user_lookup = client.get_user(username=handle)
    if not user_lookup.data:
        print(f"Could not find user: {handle}")
        sys.exit(1)

    user_id = user_lookup.data.id

    response = fetch_latest_tweets(user_id, max_results=5)

    # Normalize main tweets
    tweets_data = []
    if response.data:
        for t in response.data:
            tweets_data.append(normalize_tweet_data(t))

    # Prepare includes dict with defaults
    includes_dict = {
        "users": [],
        "media": [],
        "tweets": []
    }
    if response.includes:
        for key, objects_list in response.includes.items():
            if key in includes_dict:
                includes_dict[key] = normalize_include_data(key, objects_list)
            else:
                includes_dict[key] = [obj.data for obj in objects_list]

    full_output = {
        "tweets": tweets_data,
        "includes": includes_dict
    }

    # Write YAML
    with open("/_data/tweets.yaml", "w", encoding="utf-8") as f:
        # Note: sort_keys=False keeps the order we defined in full_output
        yaml.dump(full_output, f, sort_keys=False, allow_unicode=True)

    print("Saved tweets to tweets.yaml")

if __name__ == "__main__":
    main()