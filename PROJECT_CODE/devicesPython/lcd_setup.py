
import ST7735
from PIL import Image, ImageDraw, ImageFont
import time

class lcd_setup():
    def __init__(self):
        print("LCD setup Initiated !")
        self.display = ST7735.ST7735(
            port=0,
            cs=ST7735.BG_SPI_CS_FRONT,
            dc="GPIO9",
            backlight="GPIO12",
            rotation=270,
            spi_speed_hz=20_000_000
        )
        try:
            self.display.begin()
        except RuntimeError as error:
            print(error)
            return
        self.width, self.height = self.display.width, self.display.height
        self.image = Image.new("RGB", (self.width, self.height), (0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        self.font_url = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"



        #clear the screen
        self.clear()
    def print(self, text, font_size=24, x=0, y=0, color=(255, 255, 255), speed=1):
        font = ImageFont.truetype(self.font_url, font_size)
        #get text size :
        text_size = self.draw.textsize(text, font)
        text_width = text_size[0]
        text_height = text_size[1]
        y = y - text_height/2 # correction factor !

        #Scroll text
        if text_width > 0:
            #display text :
            self.draw.rectangle((0, 0, self.width, self.height), (0, 0, 0))
            self.draw.text((x, y), text, font=font, fill=color)
            time.sleep(0.01) # avoid flickering + let time to see the text
            for i in range(0, text_width + self.width, speed): # correction factor !
                self.draw.rectangle((0, 0, self.width, self.height), (0, 0, 0))
                self.draw.text((x - i, y), text, font=font, fill=color)
                self.display.display(self.image)
                time.sleep(0.01) # avoid flickering

        else:

            self.draw.text((x, y), text, font=font, fill=color)
            self.display.display(self.image)

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), (0, 0, 0))
        self.display.display(self.image)

    