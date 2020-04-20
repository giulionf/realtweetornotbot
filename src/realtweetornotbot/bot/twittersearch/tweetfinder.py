from rapidfuzz import fuzz
from GetOldTweets3.manager import TweetCriteria, TweetManager
from realtweetornotbot.bot.twittersearch import CriteriaBuilder, Result

TWEET_MAX_AMOUNT = 50000    # Limit for Tweet crawling
MAX_RETRIES = 5             # Limit for retries of Tweet Crawling when 0 was returned as result length
MIN_SCORE = 65              # Minimum score to be displayed as result


class TweetFinder:
    """ Helper class to find tweets given a URL of an image """

    @staticmethod
    def build_criteria_for_image(image_url):
        """ Builds a list of possible criteria for a given tweet image url """
        return CriteriaBuilder.image_to_search_criteria_candidates(image_url)

    @staticmethod
    def find_tweets(criteria_candidates):
        """ Returns a list of twittersearch.result with the given search results for each candidate

        Parameters
        ----------
        criteria_candidates : list of twittersearch.criteria
            Criteria Candidates for a given tweet image.
        """
        results = TweetFinder.__get_results(criteria_candidates)
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
        got3_criteria = TweetCriteria().setMaxTweets(TWEET_MAX_AMOUNT)
        if search_criteria.date:
            got3_criteria\
                .setSince(search_criteria.format_from_date())\
                .setUntil(search_criteria.format_to_date())
        if search_criteria.user:
            got3_criteria.setUsername(search_criteria.user)
        if search_criteria.content:
            got3_criteria.setQuerySearch(search_criteria.format_content_to_or_query())

        try:
            tweets = TweetManager.getTweets(got3_criteria)
        except Exception as e:
            print("Could not get tweets: " + str(e))
            tweets = []

        sorted_tweets = sorted(tweets,
                               reverse=True,
                               key=lambda x: TweetFinder.__score_result(x, search_criteria))

        if len(sorted_tweets) > 0:
            tweet = sorted_tweets[0]
            score = TweetFinder.__score_result(tweet, search_criteria)
            if score >= MIN_SCORE:
                return Result(search_criteria, tweet, score)

        return None

    @staticmethod
    def __score_result(tweet, search_criteria):
        score = fuzz.token_sort_ratio(tweet.text, search_criteria.content)
        return score
