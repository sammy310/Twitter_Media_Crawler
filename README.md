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
│  LICENSE
│  README.md
│  
└─data
    │  last_id.txt
    │  since_id.txt
    │  
    ├─download_data
    │  └─202202
    │          20220205.txt
    │          20220206.txt
    │          
    ├─photo
    │  └─202202
    │      ├─20220205
    │      │      20220205_000001_FKwS1mjVkAcilwz.png
    │      │      20220205_120002_FKyWy81aIAIzXVo.jpg
    │      │      20220205_120026_FKzRl4JaMAIQ0ag.jpg
    │      │      20220205_120107_FKzRvxFVUAAWuDA.jpg
    │      │      20220205_200001_FJ6-uBRaMAABMib.jpg
    │      │      
    │      └─20220206
    │              20220206_000001_FJ7r0HnaMAEIXab.jpg
    │              20220206_120000_FJDXG_QVEAEkIgF.jpg
    │              20220206_120001_FJ6-uBRaMAABMib.jpg
    │              
    ├─photo_data
    │  └─14
    │      ├─148
    │      │      1489.json
    │      │      
    │      └─149
    │              1490.json
    │              
    ├─tweet
    │  └─202202
    │          20220205.json
    │          20220206.json
    │          
    ├─video
    │  └─202202
    │      └─20220205
    │              20220205_170033_F4nJLkAe2nt6uAo1.mp4
    │              20220205_180001_gxo03NriEMPsG7RF.mp4
    │              20220205_180029_aKDIG-u1pa-R7qag.mp4
    │              
    └─video_data
        └─14
                148.json
```
> Used [Unicode Tree Generator](https://github.com/sammy310/Tree-Creater)

---

## Environment
- Python 3.8.3 :: Anaconda
- python-dotenv==0.14.0
- tweepy==3.10.0
- wget==3.2
