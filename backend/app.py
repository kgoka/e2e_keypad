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

def makeimage(text):
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
    
    #response_list = 프론트 전달용 , key_map은 백엔드 저장용
    response_list = []
    key_map = {}
    
    for value in real_values:
        #uuid.uuid4로 키값 생성
        unique_id = str(uuid.uuid4())
        image_data = makeimage(value)
        #위의 text_to_base64_image 함수 호출해서 숫자에 해당하는 이미지파일 받아옴
        response_list.append({
            "id": unique_id,
            "image": image_data,
            "is_blank": (value == 'blank')
        })
        #프론트에 보낼 response_list 만듦 여기 키값, 이미지값 포함되어있고 이거 프론트로 전송

        key_map[unique_id] = value
        #key_map에 키값에 해당하는 실제값 저장


    
   
    return jsonify({
        "layout": response_list
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)