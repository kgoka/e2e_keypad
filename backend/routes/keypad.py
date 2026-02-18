from flask import Blueprint, current_app, jsonify, request

from services.keypad_service import InvalidSessionError

# /api/* 경로를 담당하는 키패드 라우터
keypad_bp = Blueprint("keypad", __name__, url_prefix="/api")


@keypad_bp.get("/keypad")
def get_keypad():
    # 앱에 등록된 서비스로 랜덤 키패드 레이아웃 생성
    keypad_service = current_app.extensions["keypad_service"]
    payload = keypad_service.build_layout()
    return jsonify(payload)


@keypad_bp.post("/submit")
def submit_input():
    # 요청 바디에서 토큰/입력 ID 목록 추출
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    input_ids = data.get("input_ids", [])

    # 타입이 맞지 않으면 바로 400 응답
    if not isinstance(input_ids, list):
        return jsonify({"error": "input_ids must be a list"}), 400

    keypad_service = current_app.extensions["keypad_service"]

    try:
        # UUID 목록을 실제 숫자 문자열로 복원
        decrypted = keypad_service.decode_input_ids(token, input_ids)
    except InvalidSessionError as exc:
        # 세션 토큰 오류(누락/만료/불일치)
        return jsonify({"error": str(exc)}), 400

    return jsonify({"decrypted": decrypted, "message": "Submitted successfully."})
