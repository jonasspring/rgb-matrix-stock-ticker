import json
import time
import os
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont
from core.base_app import BaseApp

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class ClockApp(BaseApp):

    def __init__(self, config):
        self.config = config.get("clock_app", {})
        self.pixel_shape = config.get("pixel_shape", (64, 32))

        # Status für den Wechsel zwischen Zeit und Datum
        self.display_mode = "time"  # Startet mit der Uhrzeit
        self.last_change_time = time.time()
        self.last_drawn_text = ""

        # Schriftgröße 16 ist perfekt für 64x32 (exakt die doppelte Skalierung des 8px Fonts)
        try:
            self.font = ImageFont.truetype("04B_03__.TTF", size=16)
        except OSError:
            # Fallback, falls der Font-Pfad nicht stimmt
            self.font = ImageFont.load_default()

    def update_config(self, config):
        self.config = config.get("clock_app", {})
        self.pixel_shape = config.get("pixel_shape", (64, 32))
        self.last_drawn_text = ""

    def update_data(self):
        """
        Prüft ob gewechselt werden muss oder ob die Minute umgesprungen ist.
        """
        update_image = False
        current_time = time.time()
        
        # 1. Prüfen, ob wir zwischen Uhrzeit und Datum wechseln müssen
        change_interval = self.config.get("change_interval_sec", 10)
        
        if (current_time - self.last_change_time) > change_interval:
            # switch mode
            self.display_mode = "date" if self.display_mode == "time" else "time"
            self.last_change_time = current_time
            update_image = True

        # 2. Prüfen, ob sich der Text an sich geändert hat (z.B. Minute springt um)
        now = datetime.now()
        if self.display_mode == "time":
            current_text = now.strftime("%H:%M")
        else:
            current_text = now.strftime("%d.%m.")

        if current_text != self.last_drawn_text:
            self.last_drawn_text = current_text
            update_image = True
            
        return update_image


    def render(self) -> Image:
        """
        Generiert das 64x32 Bild mit exakt zentriertem Text.
        """
        img = Image.new("RGB", self.pixel_shape, (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Farben aus der Config (Fallback: Weiß für Zeit, Cyan für Datum)
        if self.display_mode == "time":
            text_color = tuple(self.config.get("time_color", (255, 255, 255)))
        else:
            text_color = tuple(self.config.get("date_color", (0, 255, 255)))

        # Exakte Mitte der Matrix ermitteln (bei 64x32 ist das X=32, Y=16)
        center_x = self.pixel_shape[0] // 2
        center_y = self.pixel_shape[1] // 2

        # anchor="mm" (Middle-Middle) zentriert den Text horizontal und vertikal perfekt an der Koordinate
        draw.text((center_x, center_y), self.last_drawn_text, fill=text_color, font=self.font, anchor="mm")

        return img


if __name__ == "__main__":
    # Mock Config zum Testen
    test_config = {
        "pixel_shape": (64, 32),
        "clock_app": {
            "change_interval_sec": 3,
            "time_color": [255, 255, 255],
            "date_color": [255, 255, 255]
        }
    }
    
    app = ClockApp(test_config)
    
    # Simuliere einen Loop zum Testen des Wechsels
    for i in range(10):
        if app.update_data():
            img = app.render()
            img.show()
        time.sleep(1)