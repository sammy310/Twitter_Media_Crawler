# -*- coding: utf-8 -*-

# twitterMediaCrawler.py
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
PHOTO_PATH = 'photo'
VIDEO_PATH = 'video'
DATA_PATH = 'data'
DOWNLOAD_DATA_LIST_PATH = 'download_data'

TWEET_PATH = 'tweet'

ERR_PATH = 'err.txt'

UTC_TIME = 9

UPDATE_KEY = 'update'
DATA_KEY = 'data'

MAX_SPLIT_DATA_SIZE = 17
PHOTO_KEY_GENERATE_SIZE = 15
VIDEO_KEY_GENERATE_SIZE = 16

# -----=====-----=====-----=====-----=====-----=====-----=====

load_dotenv()
CONSUMER_KEY = os.getenv('API_KEY')
CONSUMER_SECRET = os.getenv('API_SCRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')


auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

SINCE_ID_PATH = f'{DATA_PATH}/{SINCE_ID_PATH}'
LAST_ID_PATH = f'{DATA_PATH}/{LAST_ID_PATH}'

ERR_PATH = f'{DATA_PATH}/{ERR_PATH}'

TWEET_PATH = f'{DATA_PATH}/{TWEET_PATH}'
DOWNLOAD_DATA_LIST_PATH = f'{DATA_PATH}/{DOWNLOAD_DATA_LIST_PATH}'
PHOTO_PATH = f'{DATA_PATH}/{PHOTO_PATH}'
VIDEO_PATH = f'{DATA_PATH}/{VIDEO_PATH}'
PHOTO_DATA_PATH = f'{PHOTO_PATH}_{DATA_PATH}'
VIDEO_DATA_PATH = f'{VIDEO_PATH}_{DATA_PATH}'

class TwitterMediaCrawler:
    def __init__(self):
        self.getCount = 100

        self.sinceID = None
        self.latestID = None
        self.lastID = None

        self.photo = []
        self.video = []
        self.tweetCount = 0
        self.dupCount = 0

        self.photoData = {}
        self.videoData = {}


        if os.path.exists(SINCE_ID_PATH):
            with open(SINCE_ID_PATH, 'r') as f:
                self.sinceID = int(f.readline())
        
        if not os.path.exists(DATA_PATH):
            os.mkdir(DATA_PATH)

        if not os.path.exists(TWEET_PATH):
            os.mkdir(TWEET_PATH)
        
        if not os.path.exists(PHOTO_DATA_PATH):
            os.mkdir(PHOTO_DATA_PATH)
        if not os.path.exists(VIDEO_DATA_PATH):
            os.mkdir(VIDEO_DATA_PATH)


    def GetNewFilePath(self, filePath, ext):
        if os.path.exists(f'{filePath}{ext}'):
            dupCount = 1
            while True:
                if not os.path.exists(f'{filePath}_{dupCount}{ext}'):
                    filePath += f'_{dupCount}'
                    break
                else:
                    dupCount += 1

        return (filePath + ext)
    

    def StartCrawler(self, isDownloadMedia):
        self.ErrorCheck()
        self.GetTweet()
        
        if isDownloadMedia:
            self.DownloadPhotoData()
        self.SavePhotoData()
        self.SavePhotoDownloadDataList()

        if isDownloadMedia:
            self.DownloadVideoData()
        self.SaveVideoData()
        self.SaveVideoDownloadDataList()

        self.UpdateID()



    def ErrorCheck(self):
        print('Error Check\n')

        if not os.path.exists(ERR_PATH):
            return

        f = open(ERR_PATH, 'r')
        lines = f.readlines()
        f.close()

        os.remove(ERR_PATH)
        
        for line in lines:
            if not line:
                continue

            errData = line.split(' ')
            fileName = errData[0].strip()
            fileURL = errData[1].strip()

            if (fileName[0] == '.'):
                self.DownloadMediaFromURL(VIDEO_PATH, fileName[1:], fileURL)
            else:
                self.DownloadMediaFromURL(PHOTO_PATH, fileName, fileURL)

        print('-----\n')
    

    def GetTweet(self):
        tweetData = {}

        while True:
            tweets = None
            try:
                print(f'\n\nsince : {self.sinceID}, max : {self.lastID}\n\n')

                if self.sinceID is not None and self.lastID is not None:
                    tweets = api.home_timeline(count=self.getCount, exclude_replies=False, include_entities=True, tweet_mode='extended', since_id=(self.sinceID+1), max_id=(self.lastID-1))
                elif self.sinceID is not None:
                    tweets = api.home_timeline(count=self.getCount, exclude_replies=False, include_entities=True, tweet_mode='extended', since_id=(self.sinceID+1))
                elif self.lastID is not None:
                    tweets = api.home_timeline(count=self.getCount, exclude_replies=False, include_entities=True, tweet_mode='extended', max_id=(self.lastID-1))
                else:
                    tweets = api.home_timeline(count=self.getCount, exclude_replies=False, include_entities=True, tweet_mode='extended')
            except tweepy.TweepError as e:
                print(e)
                break

            
            if tweets is None or not tweets or len(tweets) == 0:
                break

            if self.latestID == None:
                self.latestID = tweets[0].id

            self.tweetCount += len(tweets)

            for t in tweets:
                tw = t
                if hasattr(t, 'retweeted_status'):
                    tw = t.retweeted_status
                if self.IsPhotoExists(tw.id_str) or self.IsVideoExists(tw.id_str):
                    self.dupCount += 1
                    continue

                print(f'ID : {tw.id}')
                print(f'USER_ID : {tw.user.id}')
                print(f'USER : {tw.user.name}')
                print(f'MSG : {tw.full_text}')
                createAt = self.GetTweetDate(tw.created_at)
                print(f'create : {createAt}')
                formatedDate = createAt.strftime("%Y%m%d_%H%M%S")

                tweetDate = self.GetTweetDate(t.created_at)
                print(f'tweetDate : {tweetDate}')

                tweetDictKey = f'{tw.id}_{formatedDate}'
                tweet = {tweetDictKey: {'user_id': tw.user.id_str, 'user_name': tw.user.name, 'screen_name': tw.user.screen_name, 'created': str(createAt), 'message': tw.full_text}}
                

                if hasattr(tw, 'extended_entities'):
                    isVideo = False
                    for media in tw.extended_entities['media']:
                        if media['type'] == 'video':
                            isVideo = True
                            maxBitrate = 0
                            videoURL = None
                            for info in media['video_info']['variants']:
                                if 'bitrate' in info:
                                    if maxBitrate < info['bitrate']:
                                        maxBitrate = info['bitrate']
                                        videoURL = info['url']
                            videoURL = videoURL.split('?')[0]

                            print(f'video : {videoURL}')
                            self.video.append([formatedDate, videoURL])

                            if not 'media' in tweet[tweetDictKey]:
                                tweet[tweetDictKey]['media'] = list()
                            tweet[tweetDictKey]['media'].append(videoURL)
                        else:
                            print(f'photo : {media["media_url"]}')
                            self.photo.append([formatedDate, media['media_url']])

                            if not 'photo' in tweet[tweetDictKey]:
                                tweet[tweetDictKey]['photo'] = list()
                            tweet[tweetDictKey]['photo'].append(media['media_url'])
                    
                    if isVideo:
                        self.UpdateVideoData(tw)
                    else:
                        self.UpdatePhotoData(tw)

                print('-----\n')

                createdDate = createAt.strftime("%Y%m%d")
                if not createdDate in tweetData:
                    tweetData[createdDate] = {}
                tweetData[createdDate].update(tweet)

            self.lastID = tweets[-1].id


        for tweetDate in tweetData.keys():
            tweetPath = f'{TWEET_PATH}/{tweetDate[:6]}'
            if not os.path.exists(tweetPath):
                os.mkdir(tweetPath)

            tweetPath += f'/{tweetDate}.json'
            if not os.path.exists(tweetPath):
                with open(tweetPath, 'w', -1, 'utf-8') as f:
                    json.dump(tweetData[tweetDate], f, indent=4, ensure_ascii=False)
            else:
                data = {}
                with open(tweetPath, 'r', -1, 'utf-8') as f:
                    data = json.load(f)
                data.update(tweetData[tweetDate])
                with open(tweetPath, 'w', -1, 'utf-8') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        print(f'\nTotal : {self.tweetCount}\n')
        print(f'Duplicated : {self.dupCount}\n')
        print(f'Photo : {len(self.photo)}\n')
        print(f'Video : {len(self.video)}\n\n')


    def DownloadMediaFromURL(self, rootPath, mediaName, mediaURL):
        try:
            savePath = f'{rootPath}/{mediaName[:6]}'
            if not os.path.exists(savePath):
                os.mkdir(savePath)

            savePath += f'/{mediaName[:8]}'
            if not os.path.exists(savePath):
                os.mkdir(savePath)

            fileName = mediaURL.split('/')[-1]
            savePath += f'/{mediaName}_{fileName}'

            if os.path.exists(savePath):
                return

            downloadURL = mediaURL
            if rootPath == PHOTO_PATH:
                frontURL, ext = os.path.splitext(mediaURL)
                downloadURL = f'{frontURL}?format={ext[1:]}&name=large'

            wget.download(downloadURL, savePath)
        except:
            err_text = ''
            if rootPath == PHOTO_PATH:
                err_text = f'{mediaName} {mediaURL}\n'
            else:
                err_text = f'.{mediaName} {mediaURL}\n'

            with open(ERR_PATH, 'a+') as f:
                f.write(err_text)

    def DownloadPhotoData(self):
        if not os.path.exists(PHOTO_PATH):
            os.mkdir(PHOTO_PATH)

        print("Start Photo Download")
        for image in self.photo:
            self.DownloadMediaFromURL(PHOTO_PATH, image[0], image[1])
    
    def DownloadVideoData(self):
        if not os.path.exists(VIDEO_PATH):
            os.mkdir(VIDEO_PATH)

        print("\n\nStart Video Download")
        for v in self.video:
            self.DownloadMediaFromURL(VIDEO_PATH, v[0], v[1])
    

    def SavePhotoDownloadDataList(self):
        if not os.path.exists(DOWNLOAD_DATA_LIST_PATH):
            os.mkdir(DOWNLOAD_DATA_LIST_PATH)
        
        dataList = ''

        for image in self.photo:
            dataList += f'{image[0]} {image[1]}\n'

        currentDate = datetime.datetime.now().strftime('%Y%m%d')

        downloadDataListPath = f'{DOWNLOAD_DATA_LIST_PATH}/{currentDate[:6]}'
        if not os.path.exists(downloadDataListPath):
            os.mkdir(downloadDataListPath)

        downloadDataListPath += f'/{currentDate}.txt'
        
        with open(downloadDataListPath, 'a+') as f:
            f.write(dataList)
    
    def SaveVideoDownloadDataList(self):
        if not os.path.exists(DOWNLOAD_DATA_LIST_PATH):
            os.mkdir(DOWNLOAD_DATA_LIST_PATH)
        
        dataList = ''

        for v in self.video:
            dataList += f'.{v[0]} {v[1]}\n'
        
        currentDate = datetime.datetime.now().strftime('%Y%m%d')

        downloadDataListPath = f'{DOWNLOAD_DATA_LIST_PATH}/{currentDate[:6]}'
        if not os.path.exists(downloadDataListPath):
            os.mkdir(downloadDataListPath)

        downloadDataListPath += f'/{currentDate}.txt'
        
        with open(downloadDataListPath, 'a+') as f:
            f.write(dataList)
    

    def UpdateID(self):
        if self.latestID is not None:
            savedLatestID = None
            if os.path.exists(SINCE_ID_PATH):
                with open(SINCE_ID_PATH, 'r') as f:
                    savedLatestID = int(f.readline())

            if savedLatestID is None or savedLatestID < self.latestID:
                with open(SINCE_ID_PATH, 'w') as f:
                    f.write(str(self.latestID))

        if self.lastID is not None:
            savedLastID = None
            if os.path.exists(LAST_ID_PATH):
                with open(LAST_ID_PATH, 'r') as f:
                    savedLastID = int(f.readline())
            
            if savedLastID is None or savedLastID > self.lastID:
                with open(LAST_ID_PATH, 'w') as f:
                    f.write(str(self.lastID))
    

    def GetTweetDate(self, created_at):
        return created_at + datetime.timedelta(hours=UTC_TIME)

    def GetPhotoKey(self, tweetID):
        return tweetID[:-PHOTO_KEY_GENERATE_SIZE]
    
    def GetPhotoDataPath(self, photoKey):
        photoDataPath = PHOTO_DATA_PATH
        for splitSize in range(MAX_SPLIT_DATA_SIZE - PHOTO_KEY_GENERATE_SIZE, 0, -1):
            photoDataPath += f'/{photoKey[:-splitSize]}'
            if not os.path.exists(photoDataPath):
                os.mkdir(photoDataPath)

        photoDataPath += f'/{photoKey}.json'
        return photoDataPath
    
    def IsPhotoExists(self, tweetID):
        photoKey = self.GetPhotoKey(tweetID)
        if not photoKey in self.photoData:
            self.photoData[photoKey] = {UPDATE_KEY: False, DATA_KEY: {}}

            photoDataPath = self.GetPhotoDataPath(photoKey)
            if os.path.exists(photoDataPath):
                with open(photoDataPath, 'r', -1, 'utf-8') as f:
                    self.photoData[photoKey][DATA_KEY] = json.load(f)
        
        return tweetID in self.photoData[photoKey][DATA_KEY]
    
    def UpdatePhotoData(self, tweet):
        photoKey = self.GetPhotoKey(tweet.id_str)
        data = {tweet.id_str: {'user_id': tweet.user.id, 'user_name': tweet.user.name, 'user_screen_name': tweet.user.screen_name, 'created': str(self.GetTweetDate(tweet.created_at))}}
        
        data[tweet.id_str]['url'] = tweet.extended_entities['media'][0]['url']
        data[tweet.id_str]['expanded_url'] = tweet.extended_entities['media'][0]['expanded_url']
        data[tweet.id_str]['media'] = []
        for media in tweet.extended_entities['media']:
            data[tweet.id_str]['media'].append({'media_id': media['id'], 'media_url': media['media_url_https']})
        
        if not photoKey in self.photoData:
            self.photoData[photoKey] = {UPDATE_KEY: False, DATA_KEY: {}}
        
        self.photoData[photoKey][UPDATE_KEY] = True
        self.photoData[photoKey][DATA_KEY].update(data)

    def GetVideoKey(self, tweetID):
        return tweetID[:-VIDEO_KEY_GENERATE_SIZE]
    
    def GetVideoDataPath(self, videoKey):
        videoDataPath = VIDEO_DATA_PATH
        for splitSize in range(MAX_SPLIT_DATA_SIZE - VIDEO_KEY_GENERATE_SIZE, 0, -1):
            videoDataPath += f'/{videoKey[:-splitSize]}'
            if not os.path.exists(videoDataPath):
                os.mkdir(videoDataPath)

        videoDataPath += f'/{videoKey}.json'
        return videoDataPath
    
    def IsVideoExists(self, tweetID):
        videoKey = self.GetVideoKey(tweetID)
        if not videoKey in self.videoData:
            self.videoData[videoKey] = {UPDATE_KEY: False, DATA_KEY: {}}

            videoDataPath = self.GetVideoDataPath(videoKey)
            if os.path.exists(videoDataPath):
                with open(videoDataPath, 'r', -1, 'utf-8') as f:
                    self.videoData[videoKey][DATA_KEY] = json.load(f)
        
        return tweetID in self.videoData[videoKey][DATA_KEY]
    
    def UpdateVideoData(self, tweet):
        videoKey = self.GetVideoKey(tweet.id_str)
        data = {tweet.id_str: {'user_id': tweet.user.id, 'user_name': tweet.user.name, 'user_screen_name': tweet.user.screen_name, 'created': str(self.GetTweetDate(tweet.created_at))}}
        
        media = tweet.extended_entities['media'][0]
        data[tweet.id_str]['media_id'] = media['id']
        data[tweet.id_str]['url'] = media['url']
        data[tweet.id_str]['expanded_url'] = media['expanded_url']
        data[tweet.id_str]['media_url'] = media['media_url_https']
        data[tweet.id_str]['video_info'] = media['video_info']['variants']

        if not videoKey in self.videoData:
            self.videoData[videoKey] = {UPDATE_KEY: False, DATA_KEY: {}}
        
        self.videoData[videoKey][UPDATE_KEY] = True
        self.videoData[videoKey][DATA_KEY].update(data)
        

    def SavePhotoData(self):
        for photoKey in self.photoData:
            if self.photoData[photoKey][UPDATE_KEY]:
                photoDataPath = self.GetPhotoDataPath(photoKey)
                with open(photoDataPath, 'w', -1, 'utf-8') as f:
                    json.dump(self.photoData[photoKey][DATA_KEY], f, indent=4, ensure_ascii=False)

    def SaveVideoData(self):
        for videoKey in self.videoData:
            if self.videoData[videoKey][UPDATE_KEY]:
                videoDataPath = self.GetVideoDataPath(videoKey)
                with open(videoDataPath, 'w', -1, 'utf-8') as f:
                    json.dump(self.videoData[videoKey][DATA_KEY], f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    TwitterMediaCrawler().StartCrawler(True)
