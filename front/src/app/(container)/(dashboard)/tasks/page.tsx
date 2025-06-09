'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';

// 작성자 : 최재우
// 기능 : 타이핑효과를 위한 라이브러리
// 마지막 수정일 : 2025-06-08
import { Typewriter } from 'react-simple-typewriter'

let currentStoryId: number | null = null;

// 작성자 : 최준혁
// 기능 : LangGraph 기반 동화 생성 API 호출 함수 (user_id=760 테스트용)
// 마지막 수정일 : 2025-06-03
// 실제 동화 생성시에는 동화 생성 버튼, 혹은 채팅으로 '동화 생성' 등 트리거와 분기가 필요
const getAIResponse = async (msg: string): Promise<string> => {
  try {
    const user_id = 760;

    const res = await axios.post('http://localhost:8721/api/v1/chat/story/', {
      input: msg,
      user_id,
      story_id: currentStoryId,  // 초기엔 null → 백엔드가 생성
      mode: 'create',
    });

    // story_id가 없다면 백에서 새로 내려온 걸 저장
    if (!currentStoryId && res.data?.story_id) {
      currentStoryId = res.data.story_id;
    }

    return res.data?.paragraph || '동화를 생성할 수 없습니다.';
  } catch (error) {
    console.error('LangGraph 요청 실패:', error);
    return '서버에 연결할 수 없습니다.';
  }
};


export default function GeminiStoryChatbot() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: "안녕하세요! 🧒 저와 함께 동화를 만들어봐요. 주제나 상황을 입력해보세요!" }
  ]);
  const [input, setInput] = useState('');
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 메시지 추가될 때마다 자동 스크롤
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  // 메시지 전송 핸들러
  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages(prev => [...prev, { sender: 'user', text: trimmed }]);
    setInput('');

    const aiResponse = await getAIResponse(trimmed);
    setMessages(prev => [...prev, { sender: 'ai', text: aiResponse }]);
  };

  const handleClear = () => {
    setMessages([
      { sender: 'ai', text: "안녕하세요! 🧒 저와 함께 동화를 만들어봐요. 주제나 상황을 입력해보세요!" }
    ]);
  };

  const lastIdx = messages.length - 1;

  return (
    <main className="bg-gray-50 min-h-screen px-4 py-6 ">
      <div className="container mx-auto max-w-4xl">

        {/* 헤더 */}
        <div className="mb-6">
          <h1 className="text-2xl md:text-3xl font-bold text-gray-800">🧒 함께 만들어가는 나만의 동화책</h1>
          <p className="text-gray-600 text-sm mt-1">예: “작은 여우가 눈 오는 날 길을 잃었어”</p>
        </div>

        {/* 채팅 창 */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-4">
          <div className="flex items-center px-4 py-3 border-b border-gray-200 bg-gray-50 rounded-t-lg">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full" />
              <span className="text-sm font-medium text-gray-700">대화중 ...</span>
            </div>
          </div>

          <div
            ref={chatContainerRef}
            className="overflow-y-auto h-[calc(100vh-300px)] min-h-[400px] p-4 space-y-4"
          >
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex space-x-3 animate-fadeIn ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                {msg.sender === 'ai' && (
                  <div className="flex-shrink-0 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">AI</span>
                  </div>
                )}
                <div className="flex-1 max-w-md">
                  <div className={`${msg.sender === 'user' ? 'bg-gray-800 text-white' : 'bg-blue-50 text-gray-800'} rounded-lg px-4 py-3`}>
                    {/* 타이핑효과 구현 Start
                    작성자 : 최재우
                    기능 : 타이핑효과를 위한 라이브러리
                    마지막 수정일 : 2025-06-08 */}
                    {msg.sender === 'ai' ? (
                      <Typewriter
                        words={[msg.text]}
                        typeSpeed={43}
                        cursor={idx === lastIdx}
                      />
                    ) : (
                      msg.text
                    )}
                    {/* 타이핑효과 구현 end */}
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
            <label className="block text-sm font-medium text-gray-700 mb-2">어떤 이야기를 들려줄까요?</label>
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
                placeholder="예: 용감한 토끼가 친구를 찾고 있어요"
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
              대화 초기화
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
