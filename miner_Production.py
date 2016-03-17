
# coding: utf-8

# In[ ]:

from __future__ import division
import tweepy
import time
import datetime as datetime
from xlwt import Workbook
from collections import Counter
import numpy as np

## API Keys, protect!
## Can be left here or referenced in a separate file
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
names = ['WESTLINN_ASB', 'SamLim44']

startTimeHour = 9
endTimeHour = 16 # 24 hour clock - 1, so 16 = 3pm

# Define function for mining all statuses
def getAllTweets(name):
    
    # Initialise a list to hold all Tweets
    alltweets = []

    # Make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = name, count=200)

    # Manage rate limit
    time.sleep(5)
    
    # Save most recent tweets
    alltweets.extend(new_tweets)

    # Save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # Keep minig tweets until there are no tweets left to mine
    while len(new_tweets) > 0:
        
        # All subsiquent requests use max_id param to prevent duplicates
        new_tweets = api.user_timeline(screen_name = name, count=200, max_id=oldest)

        # Manage rate limit
        time.sleep(5)
        
        # Save most recent tweets
        alltweets.extend(new_tweets)

        # Update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        
    return alltweets

# Initialise loop through names to mine
for name in names:
    
    # Initialise objects
    bk1 = Workbook()
    bk2 = Workbook()
    creCnt = Counter()
    tgs = Counter()
    totfvs = 0
    maxfts = 0
    maxFTt = ''
    plcs = Counter()
    maxRTt = ''
    totrts = 0
    maxrts = 0
    creList = []
    
    # Add Sheet to workbooks
    res1 = bk1.add_sheet('MinerResults')
    res2 = bk2.add_sheet('MinerStatistics')
    
    # Write headers row
    res1.write(0,0,'Created')
    res1.write(0,1,'Coordinates')
    res1.write(0,2,'Favourite')
    res1.write(0,3,'Place')
    res1.write(0,4,'Retweeted')
    res1.write(0,5,'Text')
    
    # Set up counters for xlwt and logging
    rowNum = 0
    
    # Call getAllTweets Function
    alltweets = getAllTweets(name)
    
    # Write results to Workbook
    for tweet in alltweets:
        # Counter
        rowNum += 1
        # Write to xls
        res1.write(rowNum,0,tweet.created_at.isoformat())
        res1.write(rowNum,1,tweet.coordinates)
        if len(tweet.entities['hashtags']) > 0:
            res1.write(rowNum,2,tweet.entities['hashtags'][0]['text'])
        else:
            res1.write(rowNum,2,'')
        if tweet.place is None:
            res1.write(rowNum,3,'')
        else:
            res1.write(rowNum,3,tweet.place.full_name)
        res1.write(rowNum,4,tweet.retweet_count)
        res1.write(rowNum,5,tweet.text)

        # Analysis
        
        # Time to tweet
        creTime = tweet.created_at
        creCnt[tweet.created_at.hour] += 1
        inSeconds = datetime.timedelta(hours = creTime.time().hour, minutes = creTime.time().minute,
                                       seconds = creTime.time().second).total_seconds()
        creList.append(inSeconds)
        
        # Hashtags
        if len(tweet.entities['hashtags']) > 0:
            if len(tweet.entities['hashtags']) > 1:
                for x in range(len(tweet.entities['hashtags'])):
                    tgs[(tweet.entities['hashtags'][x]['text'])] += 1
            else:
                tgs[tweet.entities['hashtags'][0]['text']] += 1
                
        # Favourite Count
        ftc = tweet.favorite_count
        totfvs += ftc
        if ftc > maxfts:
            maxfts = ftc
            maxFTt = tweet.text
        
        # Places Count
        if tweet.place is None:
            pass
        else:
            plcs[tweet.place.full_name] += 1

        
        # Re-tweets
        rtc = tweet.retweet_count
        totrts += rtc
        if rtc > maxrts:
            maxrts = rtc
            maxRTt = tweet.text
            
    # Analysis
    
    # Number of tweets in each hour of day
    res2.write(0,0,'Hour')
    res2.write(0,1,'Number of Tweets')
    hrRowNum = 1
    for hourTweet in creCnt.keys():
        res2.write(hrRowNum,0,hourTweet)
        res2.write(hrRowNum,1,creCnt[hourTweet])
        hrRowNum += 1

    res2.write(0,3,'Popular Hour to Tweet')
    res2.write(0,4,creCnt.most_common()[0][0])
    res2.write(1,3,'Number of Tweets at this time')
    res2.write(1,4,creCnt.most_common()[0][1])
    
    a = np.array(creList)
    p = np.percentile(a, 95) # 95% of tweets, can change to 98 etc to get higher cut off
    m, s = divmod(p, 60)
    h, m = divmod(m, 60)
    dt = datetime.datetime.strptime('{0}:{1}:{2}'.format(int(h),int(m),int(s)), '%H:%M:%S').time().isoformat()
    
    res2.write(2,3,'Usual time to stop Tweeting')
    res2.write(2,4,dt)
    
    tweetsInTime = 0
    for trng in range(startTimeHour,endTimeHour):
        tweetsInTime += creCnt[trng]
        
    res2.write(3,3,'Tweets in selected time period')
    res2.write(3,4,tweetsInTime)
    
    # Popular Hashtags
    res2.write(5,3,'Top Hashtags')
    tgRow = 6
    if len(tgs) > 5:
        for top5tgs in range(0,5):
            res2.write(tgRow,3,tgs.most_common()[top5tgs][0])
            tgRow += 1
    else:
        for toptgs in range(len(tgs)):
            res2.write(tgRow,3,tgs.most_common()[toptgs][0])
            tgRow += 1

    # Favorites
    res2.write(12,3,'Average Number of Favorites/Tweet')
    res2.write(12,4,round(totfvs / len(alltweets),2))
    
    # Re-tweets
    res2.write(13,3,'Average Number of re-tweets/Tweet')
    res2.write(13,4,round(totrts / len(alltweets),2))
    
    # Places to Tweet from
    res2.write(15,3,'Places to Tweet from')
    plcRow = 16
    if len(plcs) > 5:
        for top5plcs in range(0,5):
            res2.write(plcRow,3,plcs.most_common()[top5plcs][0])
            plcRow += 1
    elif len(plcs) == 0:
        res2.write(plcRow,3,'No places')
    else:
        for topplcs in range(len(plcs)):
            res2.write(plcRow,3,plcs.most_common()[topplcs][0])
            plcRow += 1

    
    res2.write(27,0,'Tweet with most Favourites')
    res2.write(28,0,maxFTt)
    
    res2.write(29,0,'Tweet with most re-tweets')
    res2.write(30,0,maxRTt)
    
    # Save workbooks
    bk1.save('TwitterMiner_{0}.xls'.format(name))
    bk2.save('TwitterMinerStats_{0}.xls'.format(name))

