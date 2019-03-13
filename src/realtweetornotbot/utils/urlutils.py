IMAGE_TYPES = ["jpg", "png", "jpeg", "webp"]    # Types of images that can be processed


class UrlUtils:
    """ Helper class for URLs """

    @staticmethod
    def is_imgur_url(url):
        """ Returns true, if an image url is an IMGUR image or album """
        return "imgur.com" in url

    @staticmethod
    def is_image_url(url):
        """ Returns true, if the URL is to an image file """
        return any(data_type in url for data_type in IMAGE_TYPES)

