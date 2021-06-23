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



def GetNewFilePath(filePath, ext):
    if os.path.exists(f'{filePath}{ext}'):
        dupCount = 1
        while True:
            if not os.path.exists(f'{filePath}_{dupCount}{ext}'):
                filePath += f'_{dupCount}'
                break
            else:
                dupCount += 1

    return (filePath + ext)



SINCE_ID_PATH = 'since_id.txt'
LAST_ID_PATH = 'last_id.txt'
ILLUST_PATH = 'illust'
VIDEO_PATH = 'video'

TWEET_PATH = 'tweet'

ERR_PATH = 'err.txt'

CURRENT_DATE = datetime.datetime.today().strftime('%Y%m')
VIDEO_JSON_PATH = f'{VIDEO_PATH}/{CURRENT_DATE}/{CURRENT_DATE}.json'

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
video = []
tweetCount = 0


# Download Error

print('Error Check\n')
err_text = ""
with open(ERR_PATH, 'r') as f:
    for line in f.readlines():
        if not line:
            continue

        errData = line.split(' ')
        fileName = errData[0].strip()
        fileURL = errData[1].strip()
        try:
            savePath = None
            if (fileName[0] == '.'):
                fileName = fileName[1:]
                savePath = f'{VIDEO_PATH}/{fileName[:6]}/{fileName[:8]}/{fileName}'
            else:
                savePath = f'{ILLUST_PATH}/{fileName[:6]}/{fileName[:8]}/{fileName}'
            ext = os.path.splitext(fileURL)[-1]
            savePath = GetNewFilePath(savePath, ext)
            wget.download(fileURL, savePath)
        except:
            err_text += line

with open(ERR_PATH, 'w') as f:
    f.write(err_text)

print('-----\n')


# Crawling

if not os.path.exists(TWEET_PATH):
    os.mkdir(TWEET_PATH)


videoJson = None
if os.path.exists(VIDEO_JSON_PATH):
    with open(VIDEO_JSON_PATH, 'r', -1, 'utf-8') as f:
        videoJson = json.load(f)
else:
    videoJson = dict()

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
    
    tweetData = {}

    for t in tweets:
        print(f'ID : {t.id}')
        print(f'USER_ID : {t.user.id}')
        print(f'USER : {t.user.name}')
        print(f'MSG : {t.text}')
        createAt = t.created_at + datetime.timedelta(hours=9)
        print(f'create : {createAt}')
        formatedDate = createAt.strftime("%Y%m%d_%H%M%S")

        tweetDictKey = f'{t.id}_{formatedDate}'
        tweet = {tweetDictKey: {'user_id': t.user.id_str, 'user_name': t.user.name, 'screen_name': t.user.screen_name, 'created': str(createAt)}}
        if hasattr(t, 'full_text'):
            tweet[tweetDictKey]['message'] = t.full_text
        else:
            tweet[tweetDictKey]['message'] = t.text

        if hasattr(t, 'extended_entities'):
            for media in t.extended_entities['media']:
                if media['type'] == 'video':
                    maxBitrate = 0
                    videoURL = None
                    for info in media['video_info']['variants']:
                        if 'bitrate' in info:
                            if maxBitrate < info['bitrate']:
                                maxBitrate = info['bitrate']
                                videoURL = info['url']
                    videoURL = videoURL.split('?')[0]

                    print(f'video : {videoURL}')

                    # Video Check
                    if media['id_str'] in videoJson:
                        if not 'dup_media' in tweet[tweetDictKey]:
                            tweet[tweetDictKey]['dup_media'] = dict()
                        tweet[tweetDictKey]['dup_media'].update({media['id_str']: videoURL})
                    else:
                        video.append([formatedDate, videoURL])
                        if 'source_user_id' in media:
                            videoJson.update({media['id_str']: {'user_id': media['source_user_id'], 'user_name': media['additional_media_info']['source_user']['name'], 'user_screen_name': media['additional_media_info']['source_user']['screen_name'], 'created': str(createAt), 'media_url': media['media_url_https'], 'url': media['url'], 'expanded_url': media['expanded_url'], 'video_info': media['video_info']['variants']}})
                        else:
                            videoJson.update({media['id_str']: {'user_id': t.user.id, 'user_name': t.user.name, 'user_screen_name': t.user.screen_name, 'created': str(createAt), 'media_url': media['media_url_https'], 'url': media['url'], 'expanded_url': media['expanded_url'], 'video_info': media['video_info']['variants']}})

                        if not 'media' in tweet[tweetDictKey]:
                            tweet[tweetDictKey]['media'] = list()
                        tweet[tweetDictKey]['media'].append(videoURL)
                else:
                # if media['type'] == 'photo':
                    illustration.append([formatedDate, media['media_url']])
                    print(f'pic : {media["media_url"]}')
                    if not 'illust' in tweet[tweetDictKey]:
                        tweet[tweetDictKey]['illust'] = list()
                    tweet[tweetDictKey]['illust'].append(media['media_url'])

        print('-----\n')

        createdDate = createAt.strftime("%Y%m%d")
        if not createdDate in tweetData:
            tweetData[createdDate] = {}
        tweetData[createdDate].update(tweet)

    for tweetDate in tweetData.keys():
        tweetPath = f'{TWEET_PATH}/{tweetDate[:6]}'
        if not os.path.exists(tweetPath):
            os.mkdir(tweetPath)

        tweetPath += f'/{tweetDate}.json'
        if not os.path.exists(tweetPath):
            with open(tweetPath, 'w', -1, 'utf-8') as f:
                json.dump(tweetData[tweetDate], f, indent=4, ensure_ascii=False)
        else:
            with open(tweetPath, 'r+', -1, 'utf-8') as f:
                data = json.load(f)
                data.update(tweetData[tweetDate])
                f.seek(0)
                json.dump(data, f, indent=4, ensure_ascii=False)

    lastID = tweets[-1].id


print(f'\nTotal : {tweetCount}\n')
print(f'Illust : {len(illustration)}\n')
print(f'Video : {len(video)}\n\n')


# Download Illust

if not os.path.exists(ILLUST_PATH):
    os.mkdir(ILLUST_PATH)
if not os.path.exists(VIDEO_PATH):
    os.mkdir(VIDEO_PATH)


err_text = ""

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

        ext = os.path.splitext(illustURL)[-1]
        savePath += f'/{illustName}'

        savePath = GetNewFilePath(savePath, ext)

        # print(f'{savePath} : {illustURL}')
        wget.download(illustURL, savePath)
    except:
        err_text += f'{illust[0]} {illust[1]}\n'

for v in video:
    try:
        vName = v[0]
        vURL = v[1]
        savePath = f'{VIDEO_PATH}/{vName[:6]}'
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        savePath += f'/{vName[:8]}'
        if not os.path.exists(savePath):
            os.mkdir(savePath)

        ext = os.path.splitext(vURL)[-1]
        savePath += f'/{vName}'

        savePath = GetNewFilePath(savePath, ext)

        wget.download(vURL, savePath)
    except:
        err_text += f'.{v[0]} {v[1]}\n'


# Error

with open(ERR_PATH, 'a+') as f:
    f.write(err_text)


# Video Check Json

with open(VIDEO_JSON_PATH, 'w', -1, 'utf-8') as f:
    json.dump(videoJson, f, indent=4, ensure_ascii=False)


# ID Update

if latestID is not None:
    savedLatestID = None
    if os.path.exists(SINCE_ID_PATH):
        with open(SINCE_ID_PATH, 'r') as f:
            savedLatestID = int(f.readline())

    if savedLatestID is None or savedLatestID < latestID:
        with open(SINCE_ID_PATH, 'w') as f:
            f.write(str(latestID))

if lastID is not None:
    savedLastID = None
    if os.path.exists(LAST_ID_PATH):
        with open(LAST_ID_PATH, 'r') as f:
            savedLastID = int(f.readline())
    
    if savedLastID is None or savedLastID > lastID:
        with open(LAST_ID_PATH, 'w') as f:
            f.write(str(lastID))
