
# coding: utf-8

# In[ ]:

import tweepy
import time
import datetime as datetime
from xlwt import Workbook

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
# Can be just one or many accounts
names = ['WESTLINN_ASB', 'SamLim44']

# Initialise loop through names to crawl
for name in names:
    
    # Log output
    print 'Crawling:',name
    
    # Get user pai instance
    user = api.get_user(name)
    
    # Initialise Excel Workbook to save to, this will end up in same folder as working dir
    # To find working dir:
    # import os
    # os.getcwd()
    
    bk = Workbook()
    
    # Add Sheet to workbook
    res = bk.add_sheet('CrawlerResults')
    
    # Write headers row
    res.write(0,0,'Name')
    res.write(0,1,'Screen Name')
    res.write(0,2,'Location')
    res.write(0,3,'Created')
    res.write(0,4,'Description')
    res.write(0,5,'GEO Enabled')
    res.write(0,6,'Friends')
    res.write(0,7,'Tweets')
    
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
    
    # Loop through all followers
    for follower_cursor in follower_cursors.items():
        
        # Add counters
        counter += 1
        rowNum += 1
        
        # Extract details and write to Workbook
        res.write(rowNum,0,follower_cursor.name)
        res.write(rowNum,1,follower_cursor.screen_name)
        res.write(rowNum,2,follower_cursor.location)
        res.write(rowNum,3,follower_cursor.created_at.isoformat())
        res.write(rowNum,4,follower_cursor.description)
        res.write(rowNum,5,follower_cursor.geo_enabled)
        res.write(rowNum,6,follower_cursor.friends_count)
        res.write(rowNum,7,follower_cursor.statuses_count)
        
        # If counter / by 100 to 0 remainder, log counter and time
        if counter%100 == 0:
            print counter, datetime.datetime.now().time().isoformat()
        
        # Sleep for 5 seconds per follower to avoid Twitter API rate limit error
        # Limit = 180 per 15 mins
        # 15 mins * 60 seconds = 900
        # 900 / 180 = 5
        time.sleep(5)
    
    # Having finished scraping all followers for given name, save xls file with name of twitter account
    bk.save('TwitterCrawler_{0}.xls'.format(name))

