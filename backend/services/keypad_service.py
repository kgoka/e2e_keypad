import random
import uuid


class KeypadService:
    DEFAULT_KEYPAD_VALUES = [str(i) for i in range(10)] + ["blank", "blank"]

    def __init__(self, image_service, session_store):
        self._image_service = image_service
        self._session_store = session_store
        self._keypad_values = list(self.DEFAULT_KEYPAD_VALUES)

    def build_layout(self):
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
            key_map[unique_id] = value

        token = self._session_store.create(key_map)
        return {"layout": layout, "token": token}

    def has_session(self, token):
        return bool(token) and self._session_store.get(token) is not None

    def decode_input_ids(self, token, input_ids):
        key_map = self._session_store.get(token) or {}
        decrypted_chars = []

        for key_id in input_ids:
            value = key_map.get(key_id)
            if value and value != "blank":
                decrypted_chars.append(value)

        return "".join(decrypted_chars)
