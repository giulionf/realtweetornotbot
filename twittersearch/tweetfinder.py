import os
import requests
from rapidfuzz import fuzz
import datetime as dt

from twittersearch.criteriabuilder import CriteriaBuilder
from twittersearch.searchresult import TweetCandidate
from twittersearch.tweet import Tweet

TWEET_MAX_AMOUNT = 250000  # Limit for Tweet crawling
MAX_RETRIES = (
    5  # Limit for retries of Tweet Crawling when 0 was returned as result length
)
MIN_SCORE = 65  # Minimum score to be displayed as result


class TweetFinder:
    """Finds tweets given the url of an image. It performs OCR and image analysis with the given ana"""

    @staticmethod
    def build_criteria_for_image(image_url):
        """Builds a list of possible criteria for a given tweet image url"""
        return CriteriaBuilder.image_to_search_criteria_candidates(image_url)

    @staticmethod
    def find_tweets(criteria_candidates):
        """Returns a list of SearchResult with the given search results for each candidate

        Parameters
        ----------
        criteria_candidates : list of twittersearch.criteria
            Criteria Candidates for a given tweet image.
        """

        # Try a few times to make sure an empty result is not due to server side problems.
        for _ in range(0, MAX_RETRIES):
            # Get the tweets matching the criteria using a twitter scraper
            results = list(
                map(TweetFinder.__get_tweet_for_search_criteria, criteria_candidates)
            )

            # Filter None results
            results = list(filter(None, results))
            results = list(filter(lambda result: result.tweet is not None, results))

            # Filter duplicates if we get some results before returning
            if len(results) > 0:
                unique_results = TweetFinder.__filter_duplicates(results)
                return unique_results

        return []

    @staticmethod
    def __filter_duplicates(results):
        """Delete duplicates from the result list by filtering for unique tweet ids"""
        unique_results = []
        unique_ids = []
        for result in results:
            if result.tweet.id not in unique_ids:
                unique_results.append(result)
                unique_ids.append(result.tweet.id)
        return unique_results

    @staticmethod
    def __get_tweet_for_search_criteria(criteria):
        """Gets the best tweet for a given search criteria"""

        # Limit search to last n days + only search when a username is found
        if (
            criteria.user == ""
            or (dt.date.today() - criteria.from_date()).days
            >= os.getenv("TWITTER_API_MAX_AGE_DAYS", 7)
        ):
            return None

        # Search tweets with the Twitter API
        search_args = load_credentials(filename="", yaml_key="", env_overwrite=True)
        query = gen_request_parameters(query=criteria.to_query(), results_per_call=100)
        try:
            api_result = collect_results(
                query, max_tweets=100, result_stream_args=search_args
            )
        except requests.exceptions.HTTPError:
            print("HTTP Error!")

        # We can omit the summary item
        api_result = [i for i in api_result if "newest_id" not in i]

        # Buffer into SearchResult objects that are then scored by the Similarity distance
        tweets = [Tweet(criteria=criteria, api_tweet=tweet) for tweet in api_result]
        sorted_tweets_by_similarity = sorted(
            tweets, reverse=True, key=lambda x: TweetFinder.__score_result(x, criteria)
        )

        if len(sorted_tweets_by_similarity) > 0:

            # The score to display will be the one of the best matching tweet (aka the first in the sorted list)
            best_matching_tweet = sorted_tweets_by_similarity[0]
            score = TweetFinder.__score_result(best_matching_tweet, criteria)

            # We will only return the result, if it is bigger than a certain minimum score. This needs to be
            # fine tuned to compensate for slight errors in OCR that still find the correct tweet.
            if score >= MIN_SCORE:
                return TweetCandidate(criteria, best_matching_tweet, score)

        return None

    @staticmethod
    def __score_result(tweet, search_criteria):
        """Score the tweet by measuring how similar the OCR text is to the tweets content"""
        score = fuzz.token_sort_ratio(tweet.content, search_criteria.content)
        return score
