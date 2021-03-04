from django.shortcuts import render
from tweepy.error import TweepError
import pickle
import pandas as pd
from .consts import *
import tweepy
import datetime
import math

#consts.pyからTwitterAPIキーを取得
CONSUMER_KEY = consumer_key
CONSUMER_SECRET = consumer_secret
ACCESS_TOKEN = access_token
ACCESS_TOKEN_SECRET = access_token_secret

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth,wait_on_rate_limit = True)

with open("model.pickle", mode = "rb") as f:
    model = pickle.load(f)

def make_target(user):
    statuses_count = user.statuses_count
    default_profile = 1 if user.default_profile else 0
    default_profile_image = 1 if user.default_profile_image else 0
    friends_count = user.friends_count
    followers_count = user.followers_count
    favourites_count = user.favourites_count
    geo_enabled = 1 if (True if user.url else False) or (True if user.location else False) else 0
    listed_count = user.listed_count
    account_age_hours = (datetime.datetime.now() - user.created_at).days * 24
    listed_flag = 1 if listed_count else 0
    favourites_flag = 1 if favourites_count else 0
    follow_rate = friends_count / (followers_count + 1)
    favourite_rate = friends_count / (favourites_count + 1)
    target = pd.DataFrame([[statuses_count, default_profile, default_profile_image, friends_count, followers_count, favourites_count, geo_enabled, listed_count, account_age_hours, listed_flag, favourites_flag, follow_rate, favourite_rate]])
    return target

def index(request):
    if request.method == "GET":
        return render(
            request,
            "bot/home.html"
        )
    else:
        user_id = request.POST["user_id"]
        user_id = user_id.replace("@", "")
        try:
            user = api.get_user(user_id)
            target = make_target(user)
            prediction = math.ceil(model.predict(target)[0] * 2 * 100)
            return render(
                request,
                "bot/home.html",
                {
                    "pred": prediction,
                    "user_name": user_id,
                }
                
            )
        except TweepError:
            return render(
                request,
                "bot/home.html",
                {"pred": -1}
            )
