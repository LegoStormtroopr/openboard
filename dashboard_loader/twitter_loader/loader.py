import decimal
import random
import httplib
import oauth2 as oauth
import json

from django.conf import settings

from dashboard_loader.loader_utils import clear_statistic_list, add_statistic_list_item, call_in_transaction

# Refresh every 40 seconds
refresh_rate = 40

def update_data(loader, verbosity=0):
    messages = []
    messages = call_in_transaction(get_tweets,messages, verbosity)
    return messages

def get_tweets(messages, verbosity):
    url = "https://api.twitter.com/1.1/statuses/home_timeline.json"
    consumer = oauth.Consumer(key=settings.TWITTER_API_KEY, 
                    secret=settings.TWITTER_API_SECRET)
    token = oauth.Token(key=settings.TWITTER_ACCESS_TOKEN,
                    secret=settings.TWITTER_ACCESS_TOKEN_SECRET)
    client = oauth.Client(consumer, token)
    resp, content = client.request(url, method="GET")
    data = json.loads(content)
    tweets = []
    for d in data:
        tweets.append({"user": d["user"]["name"], "tuser": "@" + d["user"]["screen_name"], "tweet": d["text"]})
    random.shuffle(tweets)
    if verbosity > 5:
        print json.dumps(tweets, indent=4)
    clear_statistic_list("tweets", "nsw", "rt", "tweets")
    sort_order = 1
    for t in tweets:
        add_statistic_list_item("tweets", "nsw", "rt", "tweets",
                        t["tweet"], sort_order=sort_order,
                        label=t["tuser"])
        if sort_order >= 5:
            break
        sort_order += 1
    if verbosity > 1:
        messages.append("Stored %d tweets" % sort_order)
    return messages

