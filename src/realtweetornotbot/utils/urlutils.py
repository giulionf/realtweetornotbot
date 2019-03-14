import requests

IMAGE_FORMATS = ("image/png", "image/jpeg", "image/jpg", "image/webp")


class UrlUtils:
    """ Helper class for URLs """

    @staticmethod
    def is_imgur_url(url):
        """ Returns true, if an image url is an IMGUR image or album """
        return "imgur.com" in url

    @staticmethod
    def is_image_url(url):
        """ Returns true if the url is to an image file """
        r = requests.head(url)
        if r.headers.get("content-type") in IMAGE_FORMATS:
            return True
        return False
