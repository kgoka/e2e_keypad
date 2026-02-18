import base64
import io

from PIL import Image, ImageDraw, ImageFont


class KeyImageService:
    IMAGE_SIZE = (60, 60)
    BACKGROUND_COLOR = (255, 255, 255)
    TEXT_COLOR = (0, 0, 0)
    FONT_NAME = "malgun.ttf"
    FONT_SIZE = 24

    def __init__(self):
        self.width, self.height = self.IMAGE_SIZE
        self.background_color = self.BACKGROUND_COLOR
        self.text_color = self.TEXT_COLOR
        self.font_name = self.FONT_NAME
        self.font_size = self.FONT_SIZE

    def _load_font(self):
        return ImageFont.truetype(self.font_name, self.font_size)

    def make_image(self, text):
        image = Image.new("RGB", (self.width, self.height), color=self.background_color)
        draw = ImageDraw.Draw(image)

        if text != "blank":
            font = self._load_font()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) / 2
            y = (self.height - text_height) / 2
            draw.text((x, y), text, font=font, fill=self.text_color)

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
