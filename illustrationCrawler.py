# -*- coding: utf-8 -*-

# illustrationCrawler.py
# sammy310

import tweepy
from tweepy import OAuthHandler
import json
import wget
import os
from dotenv import load_dotenv
import datetime


SINCE_ID_PATH = 'since_id.txt'
LAST_ID_PATH = 'last_id.txt'
ILLUST_PATH = 'illust'

TWEET_PATH = 'tweet'

ERR_PATH = 'err.txt'


load_dotenv()
CONSUMER_KEY = os.getenv('API_KEY')
CONSUMER_SECRET = os.getenv('API_SCRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')


auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)


getCount = 200

sinceID = None
if os.path.exists(SINCE_ID_PATH):
    with open(SINCE_ID_PATH, 'r') as f:
        sinceID = int(f.readline())

latestID = None
lastID = None

illustration = []
tweetCount = 0


if not os.path.exists(TWEET_PATH):
    os.mkdir(TWEET_PATH)


while True:
    tweets = None
    try:
        print(f'\n\nsince : {sinceID}, max : {lastID}\n\n')

        if sinceID is not None and lastID is not None:
            tweets = api.home_timeline(count=getCount, exclude_replies=False, since_id=(sinceID+1), max_id=(lastID-1))
        elif sinceID is not None:
            tweets = api.home_timeline(count=getCount, exclude_replies=False, since_id=(sinceID+1))
        elif lastID is not None:
            tweets = api.home_timeline(count=getCount, exclude_replies=False, max_id=(lastID-1))
        else:
            tweets = api.home_timeline(count=getCount, exclude_replies=False)
    except tweepy.TweepError as e:
        print(e)
        break

    
    if tweets is None or not tweets or len(tweets) == 0:
        break

    if latestID == None:
        latestID = tweets[0].id

    tweetCount += len(tweets)
    

    for t in tweets:
        print(f'USER : {t.user.name}')
        print(f'ID : {t.id}')
        print(f'MSG : {t.text}')
        createAt = t.created_at + datetime.timedelta(hours=9)
        print(f'create : {createAt}')
        formatedDate = createAt.strftime("%Y%m%d_%H%M%S")

        tweetDictKey = f'{t.id}_{formatedDate}'
        tweet = {tweetDictKey: {'user_name': t.user.name, 'screen_name': t.user.screen_name, 'created': str(createAt)}}
        if hasattr(t, 'full_text'):
            tweet[tweetDictKey]['message'] = t.full_text
        else:
            tweet[tweetDictKey]['message'] = t.text

        if hasattr(t, 'extended_entities'):
            tweet[tweetDictKey]['illust'] = list()
            for media in t.extended_entities['media']:
                if media['type'] == 'photo':
                    illustration.append([formatedDate, media['media_url']])
                    print(f'pic : {media["media_url"]}')
                    tweet[tweetDictKey]['illust'].append(media['media_url'])
        print('-----\n')

        createdDate = createAt.strftime("%Y%m%d")
        tweetPath = f'{TWEET_PATH}/{createdDate[:6]}'
        if not os.path.exists(tweetPath):
            os.mkdir(tweetPath)

        tweetPath += f'/{createdDate[:8]}.json'
        if not os.path.exists(tweetPath):
            with open(tweetPath, 'w', -1, 'utf-8') as f:
                json.dump(tweet, f, indent=4, ensure_ascii=False)
        else:
            with open(tweetPath, 'r+', -1, 'utf-8') as f:
                data = json.load(f)
                data.update(tweet)
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)

    lastID = tweets[-1].id


print(f'\nTotal : {tweetCount}\n')
print(f'Illust : {len(illustration)}\n\n')


if not os.path.exists(ILLUST_PATH):
    os.mkdir(ILLUST_PATH)


for illust in illustration:
    try:
        illustName = illust[0]
        illustURL = illust[1]
        savePath = f'{ILLUST_PATH}/{illustName[:6]}'
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        savePath += f'/{illustName[:8]}'
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        ext = os.path.splitext(illustURL)[1]
        savePath += f'/{illustName}'

        if os.path.exists(f'{savePath}{ext}'):
            dupCount = 1
            while True:
                if not os.path.exists(f'{savePath}_{dupCount}{ext}'):
                    savePath += f'_{dupCount}'
                    break
                else:
                    dupCount += 1

        savePath += ext

        # print(f'{savePath} : {illustURL}')
        wget.download(illustURL, savePath)
    except:
        with open(ERR_PATH, 'a+') as f:
            f.write(f'{illust[0]} - {illust[1]}')


if latestID is not None:
    savedLatestID = None
    if os.path.exists(SINCE_ID_PATH):
        with open(SINCE_ID_PATH, 'r') as f:
            savedLatestID = int(f.readline())

    if savedLatestID is not None and savedLatestID < latestID:
        with open(SINCE_ID_PATH, 'w') as f:
            f.write(str(latestID))

if lastID is not None:
    savedLastID = None
    if os.path.exists(LAST_ID_PATH):
        with open(LAST_ID_PATH, 'r') as f:
            savedLastID = int(f.readline())
    
    if savedLastID is not None and savedLastID > lastID:
        with open(LAST_ID_PATH, 'w') as f:
            f.write(str(lastID))
