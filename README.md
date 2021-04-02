# RealTweetOrNotBot
The [Reddit](https://www.reddit.com/r/realtweetornotbot/) Tweet Finder Bot

The bot is currently (13th of December 2019) ranked as the number one bot on Reddit by the unofficial [Reddit bot Ranking](https://botrank.pastimes.eu/)! 

RealTweetOrNotBot is a Reddit Bot, that analyzes image posts in given SubReddits and - if it detects a twitter
 screenshot - posts a link to it in the comments. It is written in [Python3].

# Setup
To function you need to install the required modules from the requirements.txt using:
```sh
pip install requirements.txt
```


Once that's done, you need to set certain environment variables to keep sensitive information out of the code. 

| Environment Variable     | Description |
| -------------   | ------------- |
| REDDIT_CLIENT_ID          | Reddit API Client ID  |
| REDDIT_CLIENT_SECRET  | Reddit API Client Secret  |
| REDDIT_USER_AGENT  | Reddit API User Agent  |
| REDDIT_FETCH_COUNT  | Numeric Value representing how many posts are fetched with every cycle  |
| REDDIT_SUMMON_COUNT  | Numeric value of username summons to be fetched every cycle  |
| REDDIT_USERNAME  | Username of the Bot's Reddit account  |
| REDDIT_PASSWORD  | Password of the Bot's Reddit account  |
| REDDIT_POST_MAX_AGE_DAYS  | Numeric value of how old a fetched post can be at max  |
| REDDIT_SUBREDDITS | List of subreddits joined by a + symbol e.g. "me_irl+whitepeopletwitter+meirl+2meirl4meirl"|
| DATABASE_URL  | URL to your PostGres Database  |
| DATABASE_USER  | User to log into the Database  |
| DATABASE_PASSWORD  | Password to log into the Database  |


## Database Setup
To use the bot a database is needed. It can be a local database or a remote one specified in the Environment Variables of the Operating System. Use the following Queries to create the needed tables:

```sh
CREATE TABLE seen_posts (
    "id" SERIAL PRIMARY KEY,
    "post_id" VARCHAR (255),
    "found_tweet" VARCHAR (255)
);
```

```sh
CREATE TABLE summary (
    "id" SERIAL PRIMARY KEY,
    "time" timestamp DEFAULT CURRENT_TIMESTAMP,
    "posts_seen" integer,
    "tweets_found" integer,
    "last_post_id" integer
);
```

# Running the Bot
The Bot is configured to be running on [Heroku] but can be run just as well on any Operating System supporting Python.
To run the bot, use:

```sh
python src/main.py
```

[//]: # 

   [Python3]: <https://www.python.org/>
   [PRAW]: <https://praw.readthedocs.io/en/latest/>
   [GetOldTweets3]: <https://github.com/Mottl/GetOldTweets3>
