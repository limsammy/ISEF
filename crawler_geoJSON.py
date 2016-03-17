
# coding: utf-8

# In[ ]:

import tweepy
import time
import datetime as datetime
import json
from geopy import geocoders

consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
access_token = 'access_token'
access_token_secret = 'access_token_secret'

# Set up OAuth Protocol
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Initialise PAI
api = tweepy.API(auth)

# List of twitter accounts to crawl
name = 'BeoLeeds'

# Log output
print 'Crawling:',name

# Get user pai instance
user = api.get_user(name)

# Set up counters for xlwt and logging
rowNum = 0
counter = 0

# Initialise instance of twitter Cursor
# Using the cursor allows us to return all followers, not just default recent 20
follower_cursors = tweepy.Cursor(api.followers, id = name)

# Log how many followers account has
print 'Total Followers to Crawl:',user.followers_count

# Start counter, log
print counter, datetime.datetime.now().time().isoformat()

# Creat List
listForJSON = []

# Initialise Google geo encoder
g = geocoders.GoogleV3()

# Loop through all followers
for follower_cursor in follower_cursors.items():

    # Add counters
    counter += 1
    rowNum += 1

    # Create new dict for data
    followerDict = {}
    
    loc = follower_cursor.location
    # Try geo encode
    if loc is not None:
        try:
            place, (lat, lng) = g.geocode(str(loc))
            followerDict['placeName'] = place
            followerDict['coordinates'] = [lat, lng]
        except:
            followerDict['placeName'] = 'No Location'
            followerDict['coordinates'] = [0, 0]
    else:
        followerDict['placeName'] = 'No Location'
        followerDict['coordinates'] = [0, 0]
    
    followerDict['location'] = loc
    followerDict['profileName'] = follower_cursor.name
    followerDict['created'] = follower_cursor.created_at.isoformat()
    followerDict['geo'] = follower_cursor.geo_enabled
    followerDict['friends'] = follower_cursor.friends_count
    followerDict['tweets'] = follower_cursor.statuses_count

    # Append dict to list
    listForJSON.append(followerDict)
    # If counter / by 100 to 0 remainder, log counter and time
    if counter%100 == 0:
        print counter, datetime.datetime.now().time().isoformat()

    # Sleep for 5 seconds per follower to avoid Twitter API rate limit error
    # Limit = 180 per 15 mins
    # 15 mins * 60 seconds = 900
    # 900 / 180 = 5
    time.sleep(5)
    
    
geo_str = json.dumps(listForJSON)

f = open('cData.json', 'a')
f.write(geo_str + "\n")
f.close()

