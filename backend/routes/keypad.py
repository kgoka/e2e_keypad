from flask import Blueprint, current_app, jsonify, request

from services.crypto_service import decrypt_ciphertext_b64, get_public_key_pem

keypad_bp = Blueprint("keypad", __name__, url_prefix="/api")


@keypad_bp.get("/keypad")
def get_keypad():
    keypad_service = current_app.extensions["keypad_service"]
    payload = keypad_service.build_layout()
    payload["public_key"] = get_public_key_pem()
    return jsonify(payload)


@keypad_bp.post("/submit")
def submit_input():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    encrypted_input_ids = data.get("encrypted_input_ids")

    if not isinstance(encrypted_input_ids, str) or not encrypted_input_ids:
        return jsonify({"error": "encrypted_input_ids is required"}), 400

    keypad_service = current_app.extensions["keypad_service"]
    if not keypad_service.has_session(token):
        return jsonify({"error": "Invalid or expired session token"}), 400

    decrypted_input_ids = decrypt_ciphertext_b64(encrypted_input_ids)
    input_ids = [item for item in decrypted_input_ids.split(",") if item]
    decrypted = keypad_service.decode_input_ids(token, input_ids)
    return jsonify({"decrypted": decrypted, "message": "Submitted successfully."})
