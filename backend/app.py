from flask import Flask, jsonify, request
from flask_cors import CORS
import random
import uuid
import io
import base64
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

CORS(app)

SESSION_STORAGE = {}

def text_to_base64_image(text):
    #Pillow(PIL) 라이브러리를 사용해 60x60 크기의 흰색 이미지를 만들기.

    img = Image.new('RGB', (60, 60), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("malgun.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
    if text != 'blank':
        #공백이 아닐경우 숫자를 그려라
        d.text((20, 15), text, font=font, fill=(0, 0, 0))
    buffered = io.BytesIO()
    img.save(buffered, format="PNG") 
    return f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode('utf-8')}"

# 프론트의 useEffect에서 호출함
@app.route('/api/keypad', methods=['GET'])
def get_keypad():
    #real_values에 0부터 9까지 저장하고 공백(blank) 두개까지 더함
    real_values = [str(i) for i in range(10)] + ['blank', 'blank']
    random.shuffle(real_values)
    
    session_token = str(uuid.uuid4())
    #response_list = 프론트 전달용 , key_map은 백엔드 저장용
    response_list = []
    key_map = {}
    
    for value in real_values:
        #uuid.uuid4로 키값 생성
        unique_id = str(uuid.uuid4())
        image_data = text_to_base64_image(value)
        #위의 text_to_base64_image 함수 호출해서 숫자에 해당하는 이미지파일 받아옴
        response_list.append({
            "id": unique_id,
            "image": image_data,
            "is_blank": (value == 'blank')
        })
        #프론트에 보낼 response_list 만듦 여기 키값, 이미지값 포함되어있고 이거 프론트로 전송

        key_map[unique_id] = value
        #key_map에 키값에 해당하는 실제값 저장

    SESSION_STORAGE[session_token] = key_map
    
    print(f"✅ 토큰 발급됨: {session_token}")
    
   
    return jsonify({
        "token": session_token,
        "layout": response_list
    })

@app.route('/api/submit', methods=['POST'])
def submit_input():
    try:
        req_data = request.json
        token = req_data.get('token')
        input_ids = req_data.get('input_ids', [])
        
        print(f"\n--- [DEBUG] 데이터 도착 ---")
        print(f"1. 받은 토큰: {token}")
        print(f"2. 받은 ID 개수: {len(input_ids)}개")
        
        # 저장소 확인
        print(f"3. 현재 서버가 기억하는 토큰 목록: {list(SESSION_STORAGE.keys())}")

        key_map = SESSION_STORAGE.get(token)
        
        if not key_map:
            print("🚨 오류: 매칭되는 토큰이 없음! (서버 재시작됨? 브라우저 새로고침 필요)")
            return jsonify({"decrypted": "Token Error (새로고침 하세요)"})

        result_string = ""
        for uid in input_ids:
            real_value = key_map.get(uid)
            if real_value:
                result_string += real_value
            else:
                print(f"   - 경고: ID {uid}에 해당하는 값이 없음")
    
        print(f"🔓 최종 해독 결과: '{result_string}'")
        return jsonify({"decrypted": result_string})

    except Exception as e:
        print(f"🔥 서버 에러 발생: {e}")
        return jsonify({"decrypted": "Server Error"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)