import time
import yfinance as yf
from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions

class DisplayManager(object):
    def __init__(self, config):

        self.options = self._get_options(config)

        self.matrix = RGBMatrix(options=self.options)

    def _get_options(self, config):
        pixel_shape = config["pixel_shape"]
        
        options = RGBMatrixOptions()
        options.rows = pixel_shape[1]
        options.cols = pixel_shape[0]
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat-pwm'
        options.led_rgb_sequence = "RBG"
        options.gpio_slowdown = 2
        options.pwm_bits = 9                            # Hohe Bildwiederholrate
        options.brightness = config["brightness"]       # Helligkeit in %
        options.drop_privileges = False

        return options

    def update_config(self, config):
        config_changed = config["brightness"] != self.options.brightness

        if config_changed:
            #self.matrix.Clear()
            self.options = self._get_options(config)
            self.matrix = RGBMatrix(options=self.options)

    def update_image(self, img):
        self.matrix.SetImage(img.convert("RGB"))