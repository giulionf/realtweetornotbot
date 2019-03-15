import io
import requests
import pytesseract
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
        image = ImageProcessor.__get_image(image_url)
        if image:
            image = ImageProcessor.__optimize(image)
            text = pytesseract.image_to_string(image, lang="eng")
            del image
            ocr_lock.release()
            return text
        else:
            ocr_lock.release()
            return ""

    @staticmethod
    def __get_image(url):
        try:
            return Image.open(io.BytesIO(requests.get(url).content))
        except:
            return None

    @staticmethod
    def __optimize(image):
        image = image.convert('L')
        image = ImageProcessor.__scale_to_working_size(image)
        image = ImageEnhance.Contrast(image).enhance(2)
        return image

    @staticmethod
    def __scale_to_working_size(image):
        width = float(image.size[0])
        height = float(image.size[1])
        ratio = width/height
        new_height = int((MAX_RESOLUTION/ratio)**0.5)
        new_width = int(new_height * ratio)
        return image.resize((new_width, new_height), Image.ANTIALIAS)
