import json
import time
import os

import numpy as np

import PIL
from PIL import Image, ImageDraw, ImageFont
from core.base_app import BaseApp
import yfinance as yf

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STOCK_INTERVALS = {
    "1d": "5m",
    "1mo": "1h",
    "1y": "1d",
    "max": "1d"
}
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "GBp": "£",
    "JPY": "¥",
    "CAD": "CA$",
    "AUD": "A$",
    "CHF": "CHF",
    "CNY": "¥",
}

class StockApp(BaseApp):

    def __init__(self, config):
        self.config = config["stock_app"]
        self.pixel_shape = config["pixel_shape"]

        self.stock_list = []
        self.stock_data = {}
        self.stock_currencies = {}

        self.last_fetch_time = 0
        self.last_stock_change_time = 0
        self.stock_index = 0

        self.font_ticker = ImageFont.truetype("04B_03__.TTF", size=8)

    def update_config(self, config):
        self.config = config["stock_app"]
        self.stock_list = []
        self.stock_data = {}
        self.stock_currencies = {}
        self._update_stock_data()

    def _update_stock_data(self):

        for stock, stock_settings in self.config["stocks"].items():
            stock_ticker = yf.Ticker(stock)
            if self.config["period"] in STOCK_INTERVALS.keys():
                self.stock_data[stock] = stock_ticker.history(period=self.config["period"], interval=STOCK_INTERVALS[self.config["period"]])
            else:
                self.stock_data[stock] = stock_ticker.history(period=self.config["period"])

            self.stock_currencies[stock] = stock_ticker.info.get("currency")

            if stock not in self.stock_list and stock_settings["active"]:
                self.stock_list.append(stock)

        self.last_fetch_time = time.time()
    
    def update_data(self):
        """
        Method to fetch current stock prices and to switch to new stocks
        Returns:
        - update_image: Boolean whether image should be updated or not
        """
        update_image = False

        current_time = time.time()
        if (current_time - self.last_fetch_time) > self.config["fetch_interval"]:
            self._update_stock_data()
            update_image = True

        amount_stocks = len(self.stock_list)
        if amount_stocks > 1 and (current_time - self.last_stock_change_time) > self.config["change_interval_sec"]:
            self.stock_index = (self.stock_index + 1) % amount_stocks
            self.last_stock_change_time = current_time
            update_image = True
        return update_image


    def render(self)-> Image:
        """
        Method to generate a new image for the led matrix
        """

        # Get current stock data
        if len(self.stock_list) < 1:
            return None
        if self.stock_index >= len(self.stock_list):
            self.stock_index = 0
        
        stock = self.stock_list[self.stock_index]
        data = self.stock_data[stock]
        currency = self.stock_currencies[stock]

        prices = data['Close'].tolist()
        if not prices:
            return None

        start_price, current_price = prices[0], prices[-1]
        change_pct = ((current_price - start_price) / start_price) * 100
        change_ispos = change_pct >= 0

        # Downsampling/Upsampling of prices, based on available pixels
        prices_graph = []
        indices = np.linspace(0, len(prices), self.pixel_shape[0] + 1, dtype=int)
        for idx_start, idx_end in zip(indices[:-1],indices[1:]):
            prices_graph.append(np.median(prices[idx_start:max(idx_end, idx_start+1)])) 

        # Prepare Base Image
        img = Image.new("RGB", self.pixel_shape, (0, 0, 0))
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        #font_ticker = ImageFont.truetype(os.path.join(BASE_DIR, "..", "/Pixel_fonts/04b_03/04B_03__.TTF"), size=8)
        font_ticker = self.font_ticker 
        #font_ticker = ImageFont.truetype("dogicapixel.ttf", size=8)
        trend_color = (0, 255, 0)

        # -------------- Draw Stock image ----------------------

        # Stock Name
        if len(stock) > 7:
            stock_name = stock[:7]
        else:
            stock_name = stock
        draw.text((1, 0), stock_name, fill=(255, 255, 255), font=font_ticker)

        # Stock Price
        if currency in CURRENCY_SYMBOLS.keys():
            draw.text((1, 8), f"{CURRENCY_SYMBOLS[currency]} {current_price:.2f}", fill=(255, 255, 255), font=font_ticker)
        else:
            draw.text((1, 8), f"{currency} {current_price:.2f}", fill=(255, 255, 255), font=font_ticker)

        # Relative Change
        rel_change_sign = '+' if change_ispos else '-'
        #rel_change_txt = f"{rel_change_sign}{abs(change_pct):.2f}%"
        rel_change_txt = f"{rel_change_sign}{abs(change_pct):.1e}" if abs(change_pct) >= 10000 else f"{rel_change_sign}{abs(change_pct):.2f}%"
        rel_change_color = (0, 255, 0) if change_ispos else (255, 0, 0)
        draw.text((63, 1), rel_change_txt, fill=rel_change_color, font=font_ticker, anchor="rt")

        # Display period
        draw.text((63, 8), self.config["period"], fill=(255, 255, 255), font=font_ticker, anchor="rt")

        # Stock Graph
        x_graph_min, x_graph_max = 0, self.pixel_shape[0] - 1
        y_graph_min, y_graph_max = self.pixel_shape[1] - 1 - self.config["graph_height"], self.pixel_shape[1] - 1
        max_price = max(prices_graph)
        min_price = min(prices_graph)

        if max_price == min_price:
            prices_pixels = self.config["graph_height"] // 2 * np.ones((len(prices_graph),))
        else:
            prices_pixels = (np.round((prices_graph - min_price)/(max_price - min_price) * self.config["graph_height"])).astype(int)

        for idx in range(len(prices_pixels)):
            x = int(idx)
            y1 = int(y_graph_max)
            y2 = int(y_graph_max + 1 - prices_pixels[idx])
            draw.line([(x, y1), (x, y2)], fill=(0,75,0))

        for idx in range(len(prices_pixels) - 1):
            x1 = int(idx)
            y1 = int(y_graph_max - prices_pixels[idx])
            x2 = int(idx + 1)
            y2 = int(y_graph_max - prices_pixels[idx + 1])
            draw.line([(x1, y1), (x2, y2)], fill=trend_color)

        return img



if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    app = StockApp(config)
    app.update_data()

    img = app.render()
    img.show()