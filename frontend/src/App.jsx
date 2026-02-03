import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

axios.defaults.withCredentials = true;

function App() {
  const [layout, setLayout] = useState([])
  const [loading, setLoading] = useState(true)
  const [inputIds, setInputIds] = useState([]) // 사용자가 누른 UUID들
  const [sessionToken, setSessionToken] = useState('') // 서버가 준 입장권

  useEffect(() => {
    // useEffect <- React에서 화면 처음 띄울때 실행하는 함수
    //여기서 백엔드의 /api/keypad 호출함
    axios.get('/api/keypad') 
      .then(res => {
        setLayout(res.data.layout)
        setSessionToken(res.data.token) // 토큰 저장
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }, [])

  const handleKeyClick = (item) => {
    if (item.is_blank) return;
    setInputIds(prev => [...prev, item.id]); 
  }

  const handleClearAll = () => setInputIds([]);
  const handleDelete = () => setInputIds(prev => prev.slice(0, -1));

  const handleSubmit = async () => {
    try {
      // [수정완료] input_ids 로 변수명을 맞춰서 전송
      const res = await axios.post('/api/submit', { 
        token: sessionToken, 
        input_ids: inputIds 
      });
      
      alert(`서버 해독 결과: ${res.data.decrypted}`);
      
    } catch (err) {
      console.error(err);
      alert("전송 에러!");
    }
  }

  return (
    //여기서 띄움
    <div className="container">
      <h1>이미지 보안 키패드</h1>
      
      <div className="input-display">
        {inputIds.length === 0 ? "비밀번호 입력" : inputIds.map((_, i) => <span key={i}>*</span>)}
      </div>
      
      {loading ? <p>로딩 중...</p> : (
        <div className="keypad-wrapper">
          {/* 4행 3열 그리드 */}
          <div className="keypad-grid">
            {layout.map((item) => (
              <button 
                key={item.id} 
                className={`key-btn ${item.is_blank ? 'hidden-key' : ''}`}
                disabled={item.is_blank}
                onClick={() => handleKeyClick(item)}
              >
                {item.image && <img src={item.image} alt="key" className="key-img" />}
              </button>
            ))}
          </div>

          <div className="action-row">
            <button className="action-btn clear-all" onClick={handleClearAll}>전체삭제</button>
            <button className="action-btn submit" onClick={handleSubmit}>입력</button>
            <button className="action-btn delete" onClick={handleDelete}>←</button>
          </div>
        </div>
      )}
    </div>
  )
}

export default App