# RealTweetOrNotBot
The Reddit Tweet Finder Bot

[![N|Solid](http://files.softicons.com/download/social-media-icons/flat-social-media-icons-by-uiconstock/png/128x128/reddit.png)](https://www.reddit.com/r/realtweetornotbot/)


RealTweetOrNotBot is a python script that analyzes a twitter screenshot to find the link to the tweets inside. It is written in [Python3] using the following modules:

  - [PRAW] - Python Reddit API Wrapper
  - [Pytesseract] - Python Tesseract Wrapper (OCR image analysis)
  - [GetOldTweets3] - Python module to search for tweets

# Running the Bot
The bot needs [Python3] and the Libraries to run. Since this is opensource, the PRAW Secret Data as well as the login information is stored in Environment Variables which need to be set on your Operating System.

The Bot is configured to be running on [Heroku] but can be run just as well on any Operating System supporting Python.


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [Python3]: <https://www.python.org/>
   [PRAW]: <https://praw.readthedocs.io/en/latest/>
   [GetOldTweets3]: <https://github.com/Mottl/GetOldTweets3>
   [Pytesseract]: <https://github.com/madmaze/pytesseract>
