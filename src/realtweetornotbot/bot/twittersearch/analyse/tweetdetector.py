import io
import requests
import numpy
from keras.models import load_model
from keras.preprocessing import image
from PIL import Image

model_path = "../res/tweet_detector.hdf5"
img_width = 255
img_height = 255


class TweetDetector:
    """ Neural Network that detects if an image is a tweet or not """

    def __init__(self):
        self.neural_network = load_model(model_path)

    def is_url_tweet(self, image_url):
        image = Image.open(io.BytesIO(requests.get(image_url).content))
        return self.is_tweet(image)

    def is_tweet(self, pillow_image):
        """ Returns true if the image is a tweet. If an error occured, true is passed """
        img = image.img_to_array(pillow_image.resize((img_width, img_height), Image.ANTIALIAS))
        img = numpy.expand_dims(img, axis=0)
        images = numpy.vstack([img])
        classes = self.neural_network.predict_classes(images, batch_size=10)
        return False if classes[0][0] == 0 else True

