import GetOldTweets3 as got3
from datetime import datetime
from fuzzywuzzy import fuzz
from realtweetornotbot.ocr.imageprocessor import ImageProcessor
from realtweetornotbot.ocr.textprocessor import TextProcessor
from realtweetornotbot.result.result import SearchResult

TWEET_MAX_AMOUNT = 50000
MAX_RETRIES = 5


class TweetFinder:

    @staticmethod
    def find_tweet_results(comment, parameters):
        candidates = TweetFinder.__get_candidates(comment.submission.url, parameters)
        results = TweetFinder.__get_results(candidates)
        return results

    @staticmethod
    def __get_candidates(url, parameters):
        text = ImageProcessor.image_to_text(url)
        candidates = TextProcessor.find_candidates(text, parameters)
        return candidates

    @staticmethod
    def __get_results(candidates):
        tries = 0
        results = []
        while tries < MAX_RETRIES and len(results) == 0:
            results = list(map(TweetFinder.__search_tweet_for_candidate, candidates))
            results = list(filter(None, results))
            tries += 1
        return results

    @staticmethod
    def __search_tweet_for_candidate(candidate):
        got3_criteria = got3.manager.TweetCriteria() \
            .setMaxTweets(TWEET_MAX_AMOUNT)
        if candidate.date:
            got3_criteria.setSince(candidate.format_from_date()) \
                .setUntil(candidate.format_to_date())
        if candidate.user:
            got3_criteria.setUsername(candidate.user)
        if candidate.content:
            got3_criteria.setQuerySearch(candidate.format_content_to_or_query())

        try:
            tweets = got3.manager.TweetManager.getTweets(got3_criteria)
        except:
            tweets = []

        sorted_tweets = sorted(tweets, reverse=True, key=lambda tweet: TweetFinder.__score_result(tweet, candidate))

        if len(sorted_tweets) > 0:
            tweet = sorted_tweets[0]
            return SearchResult(candidate, tweet, TweetFinder.__score_result(tweet, candidate))
        else:
            return []

    @staticmethod
    def __score_result(tweet, candidate):
        score = fuzz.token_sort_ratio(tweet.text, candidate.content)
        return score

    @staticmethod
    def __format_date(date_string):
        try:
            return datetime.strptime(date_string, "%Y-%m-%d")
        finally:
            return ""
