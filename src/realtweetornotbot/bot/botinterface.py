import abc


class BotInterface(abc.ABC):

    @abc.abstractmethod
    def fetch_new_posts(self):
        pass

    @abc.abstractmethod
    def get_image_url_from_post(self, post):
        pass

    @abc.abstractmethod
    def find_tweet(self, post):
        pass

    @abc.abstractmethod
    def handle_tweet_result(self, post, tweets):
        pass
