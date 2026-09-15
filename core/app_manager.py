import os
import json
import time

from apps.stock_app import StockApp

class AppManager(object):
    def __init__(self):

        with open("config.json") as f:
            config = json.load(f)

        self.config = config
        self.config_timestamp = os.path.getmtime('config.json')

        self.apps = {
            "stock_app": StockApp(config)
        }

    def _check_config_update(self):
        if self.config_timestamp != os.path.getmtime('config.json'):
            return True
        else:
            return False

    def _update_config(self):

        with open("config.json") as f:
            config = json.load(f)

        self.config = config
        self.config_timestamp = os.path.getmtime('config.json')
        self.apps["stock_app"].update_config(self.config)

    def main_loop(self):
        # TODO "Game loop" alle x.x sekunden, bei dem alles durchgegangen wird (non-blocking)
        while True:
            if self._check_config_update():
                print("Updating config")
                self._update_config()

            self.apps["stock_app"].update_data()
            img = self.apps["stock_app"].render()
            img.show()

            time.sleep(self.apps["stock_app"].config['change_interval_sec'])


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    app = AppManager()
    app.main_loop()