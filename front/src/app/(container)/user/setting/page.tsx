'use client';

import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import HTMLFlipBook from 'react-pageflip';
import { Typewriter } from 'react-simple-typewriter';

let currentStoryId: number | null = null;

const getAIResponse = async (msg: string): Promise<string> => {
  try {
    const user_id = 760;
    const res = await axios.post('http://localhost:8721/api/v1/chat/story/', {
      input: msg,
      user_id,
      story_id: currentStoryId,
      mode: 'create',
    });
    if (!currentStoryId && res.data?.story_id) {
      currentStoryId = res.data.story_id;
    }
    return res.data?.paragraph || '동화를 생성할 수 없습니다.';
  } catch (error) {
    console.error('LangGraph 요청 실패:', error);
    return '서버에 연결할 수 없습니다.';
  }
};

const paginateParagraphs = (paragraphs: string[], maxChars = 300): string[] => {
  const pages: string[] = [];
  let current = '';

  for (const para of paragraphs) {
    if (current.length + para.length + 2 <= maxChars) {
      current += current ? `\n\n${para}` : para;
    } else {
      pages.push(current);
      current = para;
    }
  }

  if (current) pages.push(current);
  return pages;
};

export default function GeminiStoryChatbot() {
  const [messages, setMessages] = useState([
    { sender: 'ai', text: '안녕하세요! 🧒 저와 함께 동화를 만들어봐요. 주제나 상황을 입력해보세요!' },
  ]);
  const [input, setInput] = useState('');
  const [paragraphs, setParagraphs] = useState<string[]>([]);
  const [printedText, setPrintedText] = useState('');
  const [typingComplete, setTypingComplete] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const pages = paginateParagraphs([...paragraphs, printedText]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;

    setMessages(prev => [...prev, { sender: 'user', text: trimmed }]);
    setInput('');
    const aiResponse = await getAIResponse(trimmed);
    setMessages(prev => [...prev, { sender: 'ai', text: aiResponse }]);
    setTypingComplete(false);

    // AI 타이핑 후 책 타이핑 실행
    setTimeout(() => {
      let i = 0;
      setPrintedText('');
      const interval = setInterval(() => {
        setPrintedText(prev => {
          const next = aiResponse.slice(0, i + 1);
          if (next === aiResponse) {
            clearInterval(interval);
            setParagraphs(p => [...p, aiResponse]);
            setPrintedText('');
            setTypingComplete(true);
          }
          return next;
        });
        i++;
      }, 25);
    }, aiResponse.length * 30 + 300); // AI 타이핑이 끝난 후에 시작되도록 딜레이
  };

  const handleClear = () => {
    setMessages([{ sender: 'ai', text: '안녕하세요! 🧒 저와 함께 동화를 만들어봐요. 주제나 상황을 입력해보세요!' }]);
    setParagraphs([]);
    setPrintedText('');
    setTypingComplete(false);
  };

  const lastIdx = messages.length - 1;
  const isDark = true;

  return (
    <main className={`min-h-screen ${isDark ? 'bg-gray-900 text-gray-100' : 'bg-white text-gray-900'} px-4 sm:px-6 py-10`}>
      <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 max-w-screen-xl mx-auto">
        {/* Left - Chat */}
        <div className="w-full lg:w-1/2">
          <h1 className="text-xl font-bold mb-3">🧒 나만의 동화책 만들기</h1>

          <div className={`rounded-lg border shadow mb-4 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white'}`}>
            <div className={`px-4 py-2 border-b flex items-center space-x-2 ${isDark ? 'border-gray-700 bg-gray-700' : 'border-gray-200 bg-gray-50'}`}>
              <div className="w-2.5 h-2.5 bg-green-500 rounded-full" />
              <span className="text-sm font-medium">대화중 ...</span>
            </div>
            <div ref={chatContainerRef} className="p-3 space-y-3 overflow-y-auto h-[calc(100vh-300px)] min-h-[400px]">
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.sender === 'user' ? 'justify-end' : ''}`}>
                  <div className={`max-w-[85%] text-sm px-3 py-2 rounded-lg ${msg.sender === 'user' ? 'bg-blue-600 text-white' : isDark ? 'bg-gray-600 text-white' : 'bg-blue-50 text-gray-800'}`}>
                    {msg.sender === 'ai' ? (
                      <Typewriter
                        words={[msg.text]}
                        typeSpeed={30}
                        cursor={false}
                      />
                    ) : (
                      msg.text
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className={`rounded-lg border p-3 ${isDark ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
            <label className="block text-sm font-medium mb-1">어떤 이야기를 들려줄까요?</label>
            <div className="flex space-x-2">
              <textarea
                rows={2}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                className="flex-1 resize-none border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
                placeholder="예: 용감한 토끼가 친구를 찾고 있어요"
              />
              <button onClick={handleSend} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">전송</button>
            </div>
            <button onClick={handleClear} className="mt-3 w-full py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300">초기화</button>
          </div>
        </div>

        {/* Right - FlipBook */}
        <div className="w-full lg:w-2/3 flex justify-center items-center">
         <HTMLFlipBook
            width={380}
            height={450}
            maxShadowOpacity={0.3}
            showCover={false}
            flippingTime={800}
            usePortrait={false}
            className="shadow-xl rounded-lg max-w-full"
            style={{
            //   backgroundColor: isDark ? '#3c2f21' : '#f4e9c6',
            backgroundColor: '#f4e9c6',
            color: '#1a1a1a',
            }}
          >
            {pages.map((content, idx) => (
              <div
                key={idx}
                className="bg-white w-full h-full px-8 py-10 font-serif text-base leading-relaxed whitespace-pre-wrap"
              >

                {typingComplete || idx < pages.length - 1 ? content : printedText}
              </div>
            ))}
          </HTMLFlipBook>
        </div>
      </div>
    </main>
  );
}