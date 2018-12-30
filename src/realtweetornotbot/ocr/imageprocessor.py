import io
import requests
import pytesseract
from PIL import Image, ImageEnhance

MIN_WIDTH = 5000
MIN_HEIGHT = 5000


class ImageProcessor:

    @staticmethod
    def image_to_text(image_url):
        image = ImageProcessor.__get_image(image_url)
        if image:
            image = ImageProcessor.__optimize(image)
            text = pytesseract.image_to_string(image, lang="eng")
            return text
        else:
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
        width = image.size[0]
        height = image.size[1]
        scale_x = MIN_WIDTH / width
        scale_y = MIN_HEIGHT / height
        scale = max(scale_x, scale_y)
        image = image.resize((int(width * scale), int(height * scale)), Image.ANTIALIAS)
        return image
