import io
import requests
import easyocr
from PIL import Image, ImageEnhance
from threading import Lock

MAX_RESOLUTION = 9000000    # the max. amount of pixels allowed when up-scaling an image for OCR

ocr_lock = Lock()   # Only one thread should upscale the image at any given point to not overstep RAM limits


class ImageProcessor:
    """ Helper class for extracting text out of an image url """

    @staticmethod
    def image_to_text(image_url):
        """ Downloads the image and reads its text. If no text could be read, it will return an empty string """
        ocr_lock.acquire()
        reader = easyocr.Reader(lang_list=['en', 'de'], gpu=False)
        result = reader.readtext(image_url)
        text = " ".join([i[1] for i in result])
        ocr_lock.release()
        return text
