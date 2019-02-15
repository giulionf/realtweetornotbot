# Types of images that can be processed
IMAGE_TYPES = ["jpg", "png", "jpeg", "webp"]


class UrlUtils:

    @staticmethod
    def is_imgur_submission(url):
        return "imgur.com" in url

    @staticmethod
    def is_image_submission(url):
        return any(data_type in url for data_type in IMAGE_TYPES)

