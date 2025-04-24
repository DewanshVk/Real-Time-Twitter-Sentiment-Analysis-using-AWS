import json
import boto3
import tweepy
import os
from datetime import datetime

# Fetch Twitter API credentials from AWS Secrets Manager
def get_twitter_keys():
    secret_name = "TwitterAPIKeys"
    region_name = "ap-south-1"  # AWS Mumbai Region

    client = boto3.client('secretsmanager', region_name=region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Load Twitter credentials from AWS Secrets Manager
twitter_keys = get_twitter_keys()

# Twitter API authentication using Tweepy V2
client = tweepy.Client(bearer_token=twitter_keys["TWITTER_BEARER_TOKEN"])

# AWS Clients
s3 = boto3.client('s3')
comprehend = boto3.client('comprehend', region_name="ap-south-1")  # AWS Comprehend

# S3 bucket and folder configuration
BUCKET_NAME = "hydra-sentiment-bucket"
FOLDER_NAME = "tweets/"

def lambda_handler(event, context):
    try:
        # Define the Twitter search query
        query = "#AWS -is:retweet lang:en"
        
        # Fetch recent tweets based on the query
        tweets = client.search_recent_tweets(
            query=query, max_results=10, tweet_fields=["created_at", "text", "author_id"]
        )
        
        # Process and structure tweet data
        tweet_data = []
        if tweets.data:
            for tweet in tweets.data:
                sentiment_response = comprehend.detect_sentiment(
                    Text=tweet.text,
                    LanguageCode="en"
                )
                sentiment = sentiment_response["Sentiment"]  # POSITIVE, NEGATIVE, NEUTRAL, MIXED

                tweet_data.append({
                    "id": tweet.id,
                    "created_at": tweet.created_at.isoformat(),
                    "text": tweet.text,
                    "user_id": tweet.author_id,
                    "sentiment": sentiment  # Sentiment
                })

        # Generate a unique JSON file name
        file_name = f"{FOLDER_NAME}tweets_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        # Convert tweet data to newline JSON format
        json_data = "\n".join([json.dumps(tweet) for tweet in tweet_data])

        # Upload JSON file to S3
        s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=json_data, ContentType="application/json")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "File uploaded successfully", "file_name": file_name})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }