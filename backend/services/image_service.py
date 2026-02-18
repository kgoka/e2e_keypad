import base64
import io

from PIL import Image, ImageDraw, ImageFont


class KeyImageService:
    # 키패드 버튼 이미지 기본 스타일
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
        # 시스템 폰트가 없으면 Pillow 기본 폰트로 대체
        try:
            return ImageFont.truetype(self.font_name, self.font_size)
        except IOError:
            return ImageFont.load_default()

    def make_image(self, text):
        # 60x60 흰 배경 이미지 생성
        image = Image.new("RGB", (self.width, self.height), color=self.background_color)
        draw = ImageDraw.Draw(image)

        if text != "blank":
            font = self._load_font()
            # 텍스트를 중앙에 오도록 좌표 계산
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (self.width - text_width) / 2
            y = (self.height - text_height) / 2
            draw.text((x, y), text, font=font, fill=self.text_color)

        # 프론트에서 바로 쓸 수 있게 data URL(base64) 형태로 반환
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded}"
