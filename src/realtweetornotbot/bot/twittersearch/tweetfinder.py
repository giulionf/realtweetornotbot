from rapidfuzz import fuzz
from realtweetornotbot.bot.twittersearch import CriteriaBuilder, Result
import snscrape.modules.twitter as sntwitter
from snscrape.base import  ScraperException

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
    def __get_tweet_for_search_criteria(criteria):
        try:
            tweets = sntwitter.TwitterSearchScraper(criteria.to_query()).get_items()
            sorted_tweets_by_similarity = sorted(tweets,
                                   reverse=True,
                                   key=lambda x: TweetFinder.__score_result(x, criteria))

            if len(sorted_tweets_by_similarity) > 0:
                best_matching_tweet = sorted_tweets_by_similarity[0]
                score = TweetFinder.__score_result(best_matching_tweet, criteria)
                if score >= MIN_SCORE:
                    return Result(criteria, best_matching_tweet, score)
        except ScraperException:
            return None

        return None

    @staticmethod
    def __score_result(tweet, search_criteria):
        score = fuzz.token_sort_ratio(tweet.content, search_criteria.content)
        return score
