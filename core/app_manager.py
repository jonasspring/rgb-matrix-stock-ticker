import os
import platform
import json
import time

from apps.stock_app import StockApp
from apps.clock_app import ClockApp

def is_raspberry_pi():
    # 1. Prüfen, ob es sich überhaupt um ein Linux-System handelt
    if platform.system() != "Linux":
        return False
    
    # 2. Prüfen, ob die Raspberry-Pi-spezifische Model-Datei existiert
    model_path = "/proc/device-tree/model"
    if os.path.exists(model_path):
        with open(model_path, "r") as f:
            model_string = f.read().lower()
            if "raspberry pi" in model_string:
                return True
                
    return False

if is_raspberry_pi():
    from core.display import DisplayManager

def is_raspberry_pi():
    # 1. Prüfen, ob es sich überhaupt um ein Linux-System handelt
    if platform.system() != "Linux":
        return False
    
    # 2. Prüfen, ob die Raspberry-Pi-spezifische Model-Datei existiert
    model_path = "/proc/device-tree/model"
    if os.path.exists(model_path):
        with open(model_path, "r") as f:
            model_string = f.read().lower()
            if "raspberry pi" in model_string:
                return True
                
    return False

class AppManager(object):
    def __init__(self):

        with open("config.json") as f:
            config = json.load(f)

        self.config = config
        self.config_timestamp = os.path.getmtime('config.json')

        self.update_rate = 1 # Update rate for the main loop
        self.last_app_switch = time.monotonic()

        self.apps = {
            "stock_app": StockApp(config),
            "clock_app": ClockApp(config)
        }

        self.app_keys = list(self.apps.keys())

        if not config["clock_app"]["active"]:
            self.app_keys.remove("clock_app")

        self.current_app_index = 0

        if is_raspberry_pi():
            self.display = DisplayManager(self.config)
        else:
            self.display = None

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
        self.apps["clock_app"].update_config(self.config)

        if config["clock_app"]["active"] and not "clock_app" in self.app_keys:
            self.app_keys.append("clock_app")
        elif not config["clock_app"]["active"] and "clock_app" in self.app_keys:
            self.app_keys.remove("clock_app")

        if self.display:
            self.display.update_config(self.config)

    def main_loop(self):
        while True:
            start_time = time.monotonic()

            if self._check_config_update():
                print("Updating config")
                self._update_config()

            app_change_freq = self.config.get('app_change_freq', 30)

            app_switch = False
            if len(self.app_keys) > 1 and start_time - self.last_app_switch > app_change_freq:
                self.last_app_switch = start_time
                self.current_app_key = list(self.apps.keys())[0]
                self.current_app_index = (self.current_app_index + 1) % len(self.app_keys)
                app_switch = True

            # Update current app
            self.current_app_index = self.current_app_index % len(self.app_keys)
            app_key = self.app_keys[self.current_app_index]
            current_app = self.apps[app_key]
            update_image = current_app.update_data()
            
            if app_switch or update_image:
                img = current_app.render()

                if self.display:
                    self.display.update_image(img)
                else:
                    img.show()

            elapsed_time = time.monotonic() - start_time
            sleep_time = self.update_rate - elapsed_time

            if sleep_time > 0:
                time.sleep(sleep_time)


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)
    app = AppManager()
    app.main_loop()