import GetOldTweets3 as got3
from fuzzywuzzy import fuzz
from realtweetornotbot.analyse.imageprocessor import ImageProcessor
from realtweetornotbot.analyse.textprocessor import TextProcessor
from searchresult import SearchResult

TWEET_MAX_AMOUNT = 50000
MAX_RETRIES = 5
MIN_SCORE = 65


class TweetFinder:

    @staticmethod
    def find_tweets(image_url):
        text = ImageProcessor.image_to_text(image_url)
        search_criteria_candidates = TextProcessor.text_to_search_criteria_candidates(text)
        results = TweetFinder.__get_results(search_criteria_candidates)
        return results

    @staticmethod
    def __get_results(search_criteria_candidates):
        tries = 0
        results = []
        while tries < MAX_RETRIES and len(results) == 0:
            results = list(map(TweetFinder.__get_tweet_for_search_criteria, search_criteria_candidates))
            results = list(filter(None, results))
            results = list(filter(lambda result: result.tweet is not None, results))
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
    def __get_tweet_for_search_criteria(search_criteria):
        got3_criteria = got3.manager.TweetCriteria() \
            .setMaxTweets(TWEET_MAX_AMOUNT)
        if search_criteria.date:
            got3_criteria.setSince(search_criteria.format_from_date()) \
                .setUntil(search_criteria.format_to_date())
        if search_criteria.user:
            got3_criteria.setUsername(search_criteria.user)
        if search_criteria.content:
            got3_criteria.setQuerySearch(search_criteria.format_content_to_or_query())

        try:
            tweets = got3.manager.TweetManager.getTweets(got3_criteria)
        except Exception as e:
            print("Could not get tweets: " + str(e))
            tweets = []

        sorted_tweets = sorted(tweets, reverse=True, key=lambda tweet: TweetFinder.__score_result(tweet, search_criteria))

        if len(sorted_tweets) > 0:
            tweet = sorted_tweets[0]
            score = TweetFinder.__score_result(tweet, search_criteria)
            if score >= MIN_SCORE:
                return SearchResult(search_criteria, tweet, score)

        return None

    @staticmethod
    def __score_result(tweet, search_criteria):
        score = fuzz.token_sort_ratio(tweet.text, search_criteria.content)
        return score
