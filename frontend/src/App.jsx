import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

// 쿠키/세션 기반 통신을 위해 credential 포함 전송
axios.defaults.withCredentials = true;

// PIN 최대 입력 길이(키패드 4자리)
const MAX_PIN_LENGTH = 4;

// PEM 공개키 문자열을 Web Crypto가 읽을 수 있는 ArrayBuffer로 변환
const pemToArrayBuffer = (pem) => {
  // PEM 헤더/푸터/공백 제거 후 base64 본문만 남긴다.
  let base64 = pem.replace(/-----BEGIN PUBLIC KEY-----|-----END PUBLIC KEY-----|\s/g, "");
  // 복사 과정에서 섞일 수 있는 base64 외 문자는 제거
  base64 = base64.replace(/[^A-Za-z0-9+/=]/g, "");
  // 길이를 4의 배수로 맞추기 위해 padding 보정
  const padLength = (4 - (base64.length % 4)) % 4;
  base64 += "=".repeat(padLength);

  // base64 -> binary string -> Uint8Array -> ArrayBuffer
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes.buffer;
};

// ArrayBuffer(암호문)를 서버 전송용 base64 문자열로 변환
const arrayBufferToBase64 = (buffer) => {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.length; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
};

// 공개키로 평문을 RSA-OAEP(SHA-256) 방식으로 암호화
const encryptWithPublicKey = async (publicKeyPem, plainText) => {
  // 브라우저 Web Crypto 키 객체 생성
  const key = await window.crypto.subtle.importKey(
    "spki",
    pemToArrayBuffer(publicKeyPem),
    { name: "RSA-OAEP", hash: "SHA-256" },
    false,
    ["encrypt"]
  );

  // 평문 UTF-8 인코딩 후 공개키 암호화
  const encrypted = await window.crypto.subtle.encrypt(
    { name: "RSA-OAEP" },
    key,
    new TextEncoder().encode(plainText)
  );

  return arrayBufferToBase64(encrypted);
};

function App() {
  // 랜덤 키패드 버튼 데이터
  const [layout, setLayout] = useState([]);
  // 초기 API 로딩 상태
  const [loading, setLoading] = useState(true);
  // 사용자가 누른 버튼 UUID 목록(실제 숫자는 서버만 앎)
  const [inputIds, setInputIds] = useState([]);
  // 서버에서 내려준 세션 토큰
  const [sessionToken, setSessionToken] = useState("");
  // 서버에서 내려준 공개키(프론트 암호화용)
  const [publicKey, setPublicKey] = useState("");

  useEffect(() => {
    // 페이지 진입 시 키패드 레이아웃 + 토큰 + 공개키를 한번에 요청
    axios
      .get("/api/keypad")
      .then((res) => {
        setLayout(res.data.layout || []);
        setSessionToken(res.data.token || "");
        setPublicKey(res.data.public_key || "");
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleKeyClick = (item) => {
    // 빈칸 버튼은 무시
    if (item.is_blank) return;

    // 최대 길이를 넘지 않도록 UUID 추가
    setInputIds((prev) => {
      if (prev.length >= MAX_PIN_LENGTH) return prev;
      return [...prev, item.id];
    });
  };

  // 전체 입력 삭제
  const handleClearAll = () => setInputIds([]);
  // 마지막 1자리 삭제
  const handleDelete = () => setInputIds((prev) => prev.slice(0, -1));

  const handleSubmit = async () => {
    // 제출 전 필수값 체크
    if (!publicKey) {
      alert("공개키가 없습니다.");
      return;
    }
    if (!sessionToken) {
      alert("세션 토큰이 없습니다.");
      return;
    }
    if (inputIds.length === 0) {
      alert("먼저 비밀번호를 입력해 주세요.");
      return;
    }

    // UUID 목록을 콤마로 합쳐 평문 생성
    const mergedInputIds = inputIds.join(",");
    // 공개키로 암호화한 뒤 base64 암호문 생성
    const encryptedInputIds = await encryptWithPublicKey(publicKey, mergedInputIds);

    // 서버로는 평문 UUID 대신 암호문만 전송
    const res = await axios.post(
      "/api/submit",
      {
        token: sessionToken,
        encrypted_input_ids: encryptedInputIds,
      },
      // 4xx도 throw하지 않고 응답으로 받아 사용자 메시지 처리
      { validateStatus: () => true }
    );

    // 서버 에러 응답 처리
    if (res.status >= 400) {
      alert(`전송 실패: ${res.data?.error || "알 수 없는 오류"}`);
      return;
    }

    // 성공 시 서버 해독 결과 표시
    alert(`서버 해독 결과: ${res.data.decrypted}`);
  };

  return (
    <div className="container">
      <h1>E2E 키패드</h1>

      {/* 입력 자리수 마스킹 표시 */}
      <div className="input-display">
        {inputIds.length === 0 ? "비밀번호 입력" : inputIds.map((_, i) => <span key={i}>*</span>)}
      </div>

      {/* 초기 로딩 전/후 UI 분기 */}
      {loading ? (
        <p>로딩 중...</p>
      ) : (
        <div className="keypad-wrapper">
          {/* 서버에서 받은 랜덤 키패드 배치 렌더링 */}
          <div className="keypad-grid">
            {layout.map((item) => (
              <button
                key={item.id}
                className={`key-btn ${item.is_blank ? "hidden-key" : ""}`}
                disabled={item.is_blank}
                onClick={() => handleKeyClick(item)}
              >
                {item.image && <img src={item.image} alt="key" className="key-img" />}
              </button>
            ))}
          </div>

          {/* 하단 동작 버튼 영역 */}
          <div className="action-row">
            <button className="action-btn clear-all" onClick={handleClearAll}>
              전체 삭제
            </button>
            <button className="action-btn submit" onClick={handleSubmit}>
              입력
            </button>
            <button className="action-btn delete" onClick={handleDelete}>
              지우기
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
