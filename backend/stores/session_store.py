import uuid


class InMemorySessionStore:
    def __init__(self):
        # token -> {uuid: value} 형태로 세션 맵을 보관
        self._sessions = {}

    def create(self, key_map):
        # 키패드 1회분 매핑을 새 토큰으로 저장
        token = str(uuid.uuid4())
        self._sessions[token] = key_map
        return token

    def get(self, token):
        # 토큰에 해당하는 매핑이 없으면 None 반환
        return self._sessions.get(token)
