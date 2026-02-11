from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import uuid
import io
import base64
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# 프론트엔드 포트(예: 5173)에서의 요청을 허용
CORS(app, supports_credentials=True) 

# 구조: { "session_token_1": { "uuid_a": "1", "uuid_b": "2"... }, ... }
SESSION_STORAGE = {}

def makeimage(text):
    #Pillow(PIL) 라이브러리를 사용해 60x60 크기의 흰색 이미지를 만들기.
    img = Image.new('RGB', (60, 60), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        # 폰트가 없으면 기본 폰트 사용 (윈도우: malgun.ttf, 맥/리눅스: 경로 확인 필요)
        font = ImageFont.truetype("malgun.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    
    if text != 'blank':
        # 텍스트가 중앙에 오도록 대략적인 위치 잡기
        d.text((20, 15), text, font=font, fill=(0, 0, 0))
    
    buffered = io.BytesIO()
    img.save(buffered, format="PNG") 
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

# 프론트의 useEffect에서 호출함
@app.route('/api/keypad', methods=['GET'])
def get_keypad():
    real_values = [str(i) for i in range(10)] + ['blank', 'blank']
    random.shuffle(real_values)
    
    response_list = []
    key_map = {} # 이번 세션의 정답지
    
    for value in real_values:
        unique_id = str(uuid.uuid4()) # 버튼마다 고유 ID 부여
        image_data = makeimage(value) # 숫자를 이미지로 변환
        #위의 text_to_base64_image 함수 호출해서 숫자에 해당하는 이미지파일 받아옴
        response_list.append({
            "id": unique_id,
            "image": image_data,
            "is_blank": (value == 'blank')
        })
        
        # 정답지에 기록 (UUID -> 실제 숫자)
        key_map[unique_id] = value
    
    
    # 클라이언트에게는 token을 주고, 서버는 token:key_map 쌍을 기억합니다.
    session_token = str(uuid.uuid4())
    SESSION_STORAGE[session_token] = key_map
    
    return jsonify({
        "layout": response_list,
        "token": session_token # 프론트엔드가 나중에 제출할 때 같이 보내야 함
    })

# [추가됨] 사용자가 누른 UUID들을 받아서 숫자로 변환하는 로직
@app.route('/api/submit', methods=['POST'])
def submit_input():
    data = request.json
    token = data.get('token')
    input_ids = data.get('input_ids', [])
    
    # 1. 토큰 유효성 검사
    if not token or token not in SESSION_STORAGE:
        return jsonify({"error": "유효하지 않거나 만료된 세션입니다."}), 400
        
    # 2. 저장된 정답지(key_map) 가져오기
    key_map = SESSION_STORAGE[token]
    
    decrypted_result = ""
    try:
        for uid in input_ids:
            # blank나 이상한 값이 들어올 경우 무시하거나 에러 처리
            if uid in key_map:
                val = key_map[uid]
                if val != 'blank':
                    decrypted_result += val
    except Exception as e:
        return jsonify({"error": "해독 중 오류 발생"}), 500

    print(f"사용자 입력 해독 결과: {decrypted_result}")
    
    return jsonify({
        "decrypted": decrypted_result,
        "message": "성공적으로 해독되었습니다."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
