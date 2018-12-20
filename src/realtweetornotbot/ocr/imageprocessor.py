import io
import requests
import pytesseract
from PIL import Image

MIN_WIDTH = 3000
MIN_HEIGHT = 3000
PIXEL_BINARY_THRESHOLD = 200


class ImageProcessor:

    @staticmethod
    def image_to_text(image_url):
        image = ImageProcessor.__get_image(image_url)
        image = ImageProcessor.__optimize(image)
        text = pytesseract.image_to_string(image, lang="eng")
        return text

    @staticmethod
    def __get_image(url):
        response = requests.get(url)
        image = Image.open(io.BytesIO(response.content))
        return image

    @staticmethod
    def __optimize(image):
        image = image.convert('L')
        image = ImageProcessor.__scale_to_working_size(image)
        image = image.point(lambda p: p > PIXEL_BINARY_THRESHOLD and 255)
        # image = image.filter(ImageFilter.EDGE_ENHANCE)
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
