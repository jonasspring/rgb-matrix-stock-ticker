from abc import ABC, abstractmethod
from PIL import Image


class BaseApp(ABC):
    """
    Base class for each app that displays something on the rbg matrix.
    """

    def __init__(self, config):
        self.config = config
    
    @abstractmethod
    def update_data(self):
        """
        Method to fetch new data, e.g. new stock prices, time, date, ...
        """
        pass

    @abstractmethod
    def render(self)-> Image:
        """
        Method to generate a new image for the led matrix
        """
        pass