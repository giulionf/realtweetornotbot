import GetOldTweets3 as got3
from datetime import datetime
from fuzzywuzzy import fuzz
from realtweetornotbot.ocr.imageprocessor import ImageProcessor
from realtweetornotbot.ocr.textprocessor import TextProcessor
from realtweetornotbot.result.result import SearchResult

TWEET_MAX_AMOUNT = 50000
MAX_RETRIES = 5
MIN_SCORE = 65


class TweetFinder:

    @staticmethod
    def find_tweet_results(url):
        candidates = TweetFinder.__get_candidates(url)
        results = TweetFinder.__get_results(candidates)
        return results

    @staticmethod
    def __get_candidates(url):
        text = ImageProcessor.image_to_text(url)
        candidates = TextProcessor.find_candidates(text)
        return candidates

    @staticmethod
    def __get_results(candidates):
        tries = 0
        results = []
        while tries < MAX_RETRIES and len(results) == 0:
            results = list(map(TweetFinder.__search_tweet_for_candidate, candidates))
            results = list(filter(None, results))
            tries += 1
        unique_results = TweetFinder.__filter_duplicates(results)
        return unique_results

    @staticmethod
    def __filter_duplicates(results):
        unique_results = []
        for result in results:
            already_added = False
            for r in unique_results:
                if r.tweet.id == result.tweet.id:
                    already_added = True
                    break
            if not already_added:
                unique_results.append(result)
        return unique_results

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
        except Exception as e:
            print("Could not get tweets: " + str(e))
            tweets = []

        sorted_tweets = sorted(tweets, reverse=True, key=lambda tweet: TweetFinder.__score_result(tweet, candidate))

        if len(sorted_tweets) > 0:
            tweet = sorted_tweets[0]
            score = TweetFinder.__score_result(tweet, candidate)
            if score >= MIN_SCORE:
                return SearchResult(candidate, tweet, score)

        return None

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
