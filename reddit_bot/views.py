from django.shortcuts import render

# Create your views here.

import praw
from datetime import datetime
from django.http import JsonResponse
from openai import OpenAI
from reddit_bot import keys
from .models import RedditPost, GeneratedResponse


model = 'gpt-4'

def get_completion(prompt):
    client = OpenAI(api_key=keys.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content


def get_posts(request):
    reddit = praw.Reddit(
        client_id=keys.REDDIT_CLIENT_ID,
        client_secret=keys.REDDIT_CLIENT_SECRET,
        user_agent=keys.REDDIT_USER_AGENT,
        username=keys.REDDIT_USERNAME,
        password=keys.REDDIT_PASSWORD,
    )

    subreddit = reddit.subreddit('all')
    query = "AI tools PPT"
    time_filter = "week"
    submissions = subreddit.search(query, time_filter=time_filter, limit=1)

    for submission in submissions:
        post, created = RedditPost.objects.get_or_create(
            post_id=submission.id,
            defaults={'title': submission.title, 'content': submission.selftext}
        )

        if created:
            text = submission.selftext
            prompt = f"""
                     '''{text}'''

                     "The text above is a post from Reddit. Based on the content of the post, and according to \
                     the following requirements, generate a reply that can be posted in the comments section \
                     below, around 50 words."

                     Requirements:
                     "Share your experience using ChatSlide.ai on Reddit. Describe how its AI-generated slides \
                     and voice cloning features have helped you in your work or personal projects. Focus on the \
                     convenience, time saved, and the professional quality of the outputs. Mention any specific \
                     scenarios where ChatSlide.ai made a significant difference."
                     """
            response_text = get_completion(prompt)
            GeneratedResponse.objects.create(
                post=post,
                response_text=response_text
            )

    return JsonResponse({"status": "done"})

