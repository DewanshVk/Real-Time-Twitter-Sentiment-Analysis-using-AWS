SELECT * FROM twitter_sentiment_db.tweets Limit 10;

# 1. Sentiment-wise Tweet Count
SELECT sentiment, COUNT(*) AS tweet_count FROM twitter_sentiment_db.tweets
GROUP BY sentiment
ORDER BY tweet_count DESC;

# 2. Hourly Sentiment Trend
SELECT
  date_format(from_iso8601_timestamp(created_at), '%Y-%m-%d %H:00:00') AS hour,
  sentiment,
  COUNT(*) AS count
FROM twitter_sentiment_db.tweets
GROUP BY 1, sentiment
ORDER BY hour, sentiment;

# 3. Top Positive Tweets
SELECT id, created_at, text, sentiment FROM twitter_sentiment_db.tweets
WHERE sentiment = 'POSITIVE'
ORDER BY created_at DESC
LIMIT 10;

# 4. Top Negative Tweets
SELECT id, created_at, text, sentiment FROM twitter_sentiment_db.tweets
WHERE sentiment = 'NEGATIVE'
ORDER BY created_at DESC
LIMIT 10;

# 5. Sentiment Distribution Percentage
WITH total AS (
  SELECT COUNT(*) AS total_count FROM twitter_sentiment_db.tweets
)
SELECT sentiment,
       COUNT(*) AS count,
       ROUND(COUNT(*) * 100.0 / t.total_count, 2) AS percentage
FROM twitter_sentiment_db.tweets, total t
GROUP BY sentiment, t.total_count;

# 6. Most Active Users
SELECT user_id, COUNT(*) AS tweet_count FROM twitter_sentiment_db.tweets
GROUP BY user_id
ORDER BY tweet_count DESC
LIMIT 10;