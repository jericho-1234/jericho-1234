import praw
from datetime import datetime

reddit = praw.Reddit(
    client_id="ufzJ6zOL3o8CPP2ebkVLOw",
    client_secret="w6CfWbdMjFS2vLIDEbE3MdAeOz6pGQ",
    user_agent="script:RedditDataMiner:1.0 (by /u/Natural-Loquat-4982)",
    username="Natural-Loquat-4982",
    password="Hzy20040901"
)

subreddit = reddit.subreddit('all')
queries = ["AI tools PPT", "AI tools deck", "AI tool for voice clone"]
time_filter = "week"
results = []

for query in queries:
    search_results = subreddit.search(query, time_filter=time_filter, limit=10)
    for submission in search_results:
        post_info = {
            "title": submission.title,
            "posted_on": datetime.utcfromtimestamp(submission.created_utc).isoformat(),
            "text": submission.selftext,
            "score": submission.score,
            "url": submission.url
            }
        results.append(post_info)

print(results)
