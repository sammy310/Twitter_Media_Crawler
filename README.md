# Twitter Media Crawler
### Get Media(Image, Gif, Video) From your Twitter's Timeline

---

- Using tweepy for Twitter API

---

## Must Create `.env` File!!
1. File name : `.env`
2. File contents :
```
API_KEY=
API_SCRET_KEY=
ACCESS_TOKEN=
ACCESS_TOKEN_SECRET=
```
> Get KEY and TOKEN From [Twitter Developer Potal](https://developer.twitter.com/en/portal/dashboard)

---

## Result
```
TwitterMediaCrawler
│  .env
│  .gitattributes
│  .gitignore
│  twitterMediaCrawler.py
│  last_id.txt
│  LICENSE
│  since_id.txt
│  
├─photo
│  └─202101
│      ├─20210111
│      │      20210111_000421.jpg
│      │      20210111_213513.jpg
│      │      20210111_233604.jpg
│      │      20210111_233604_1.jpg
│      │      20210111_233604_2.jpg
│      │      
│      └─20210112
│              20210112_002050.jpg
│              20210112_002140.jpg
│              20210112_002155.jpg
│              
└─tweet
    └─202101
            20210111.json
            20210112.json
```
> Used [Unicode Tree Generator](https://github.com/sammy310/Tree-Creater)

---

## Environment
- Python 3.8.3 :: Anaconda
- python-dotenv==0.14.0
- tweepy==3.10.0
- wget==3.2
