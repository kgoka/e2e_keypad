import random
import uuid


class InvalidSessionError(Exception):
    pass


class KeypadService:
    # 숫자 10개 + 빈칸 2개를 섞어서 12개 버튼 구성
    DEFAULT_KEYPAD_VALUES = [str(i) for i in range(10)] + ["blank", "blank"]

    def __init__(self, image_service, session_store):
        self._image_service = image_service
        self._session_store = session_store
        self._keypad_values = list(self.DEFAULT_KEYPAD_VALUES)

    def build_layout(self):
        # 매 요청마다 버튼 순서를 랜덤하게 섞음
        values = list(self._keypad_values)
        random.shuffle(values)

        layout = []
        key_map = {}

        for value in values:
            unique_id = str(uuid.uuid4())
            layout.append(
                {
                    "id": unique_id,
                    "image": self._image_service.make_image(value),
                    "is_blank": value == "blank",
                }
            )
            # 서버 내부에서만 UUID -> 실제 값 매핑을 저장
            key_map[unique_id] = value

        token = self._session_store.create(key_map)
        return {"layout": layout, "token": token}

    def decode_input_ids(self, token, input_ids):
        if not token:
            raise InvalidSessionError("Missing session token")

        key_map = self._session_store.get(token)
        if key_map is None:
            raise InvalidSessionError("Invalid or expired session token")

        # 프론트가 보낸 UUID 배열을 숫자 문자열로 복원
        decrypted_chars = []
        for key_id in input_ids:
            value = key_map.get(key_id)
            if value and value != "blank":
                decrypted_chars.append(value)

        return "".join(decrypted_chars)
