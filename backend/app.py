from flask import Flask
from flask_cors import CORS

from routes.keypad import keypad_bp
from services.image_service import KeyImageService
from services.keypad_service import KeypadService
from stores.session_store import InMemorySessionStore

# Flask 앱 생성 및 CORS 허용
app = Flask(__name__)
CORS(app, supports_credentials=True)

# 서비스 객체를 조립(의존성 주입)한다.
image_service = KeyImageService()
session_store = InMemorySessionStore()
keypad_service = KeypadService(
    image_service=image_service,
    session_store=session_store,
)

# 라우터에서 꺼내 쓸 수 있게 앱 확장영역에 등록
app.extensions["keypad_service"] = keypad_service
app.register_blueprint(keypad_bp)


if __name__ == "__main__":
    # 레츠고
    app.run(debug=True, port=5000)
