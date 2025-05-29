'use client';

// 패키지 import 
import { useState,  useRef, useEffect} from 'react'; // useState : 상태 변경, useEffect : 렌더링 이후 이벤트 발생시킬때
import axios from 'axios' // 서버와의 통신을 위해 사용


// AI 응답 메시지를 서버에서 받아오는 함수
const getAIResponse = async (msg: string): Promise<string> => {
  try {
    const res = await axios.post('http://localhost:8000/api/v1/chat/', { 
    // const res = await axios.post('http://116.125.140.113:8720/api/v1/chat/', { 
      msg: msg
    });
    return res.data?.aimsg || 'AI 응답이 없습니다.';
  } catch (error) {
    console.error('AI 요청 실패:', error);
    return 'AI 서버에 연결할 수 없습니다.';
  }
};

export default function GeminiChatbot() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "안녕하세요! 소나기소설에 대해 무엇이든 물어보세요." },
    { sender: 'user', text: "소나기 작품에 대해 알려주세요" },
    { sender: 'ai', text: "황순원의 '소나기'는 1953년에 발표된 단편소설로, 순수한 사랑을 그린 대표작입니다." }
  ]);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 메시지 추가될 때마다 스크롤 맨 아래로
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // 메시지 전송 함수
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    // 사용자 메시지 추가
    setMessages(prev => [...prev, { sender: 'user', text: trimmed }]);
    setInput('');

    // 서버 응답 받아오기
    const aiResponse = await getAIResponse(trimmed);

    // AI 응답 메시지 추가
    setMessages(prev => [...prev, { sender: 'ai', text: aiResponse }]);
  };

  // 채팅 전체 삭제
  const handleClear = () => {
    setMessages([]);
  };

  return (
    <main className="bg-gray-50 min-h-screen px-4 py-6">
      <div className="container mx-auto max-w-4xl">
        {/* 헤더 */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800">GEMINI 소나기소설 챗봇</h1>
        </div>

        {/* 채팅 컨테이너 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4">
          <div className="flex items-center px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full" />
              <span className="text-sm font-medium text-gray-700">Chatbot</span>
            </div>
          </div>

          <div
            ref={chatContainerRef}
            className="overflow-y-auto h-[calc(100vh-300px)] min-h-[400px] p-4 space-y-4"
          >
            {messages.length === 0 && (
              <div className="flex justify-center">
                <div className="bg-gray-100 px-4 py-2 rounded-full text-sm text-gray-600">
                  대화를 시작해보세요
                </div>
              </div>
            )}

            {messages.map((msg, idx) => (
              <div key={idx} className={`flex space-x-3 animate-fadeIn ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                {msg.sender === 'ai' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">AI</span>
                  </div>
                )}
                <div className="flex-1 max-w-md">
                  <div className={`${msg.sender === 'user' ? 'bg-gray-800 text-white' : 'bg-blue-50 text-gray-800'} rounded-lg px-4 py-3`}>
                    <p>{msg.text}</p>
                  </div>
                  <span className="text-xs text-gray-500 mt-1 block text-right">
                    {new Date().toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                {msg.sender === 'user' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">U</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* 입력 영역 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">AI와 대화할 내용을 입력하세요</label>
            <div className="flex space-x-2">
              <textarea
                rows={3}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="메시지를 입력하세요..."
              />
              <button
                onClick={handleSend}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                전송
              </button>
            </div>
          </div>
          <div className="px-4 pb-4">
            <button
              onClick={handleClear}
              className="w-full py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition"
            >
              채팅내용 지우기
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
