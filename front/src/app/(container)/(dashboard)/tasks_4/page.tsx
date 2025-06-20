"use client";

import axios from 'axios';
import React, { useRef, useState , useEffect } from 'react';
import HTMLFlipBook from 'react-pageflip';
import '@/styles/book.css'; // CSS 스타일 파일
import { illustrationDTO } from '@/lib/type/illustration';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';
import Image from "next/image";

type FlipEvent = { data: number };

const illustrationResponse = async (): Promise<illustrationDTO[]> => {
  const story_id = '2257';
  const res = await axios.post('http://localhost:8721/api/v1/illustration/story/', { story_id });
  return res.data.illustration;
};

const storyParagraphResponse = async (): Promise<storyParagraphDTO[]> => {
  const story_id = '2257';
  const res = await axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id });
  return res.data.storyParagraph;
};

const DynamicFlipBook: React.FC = () => {
  const flipBook = useRef<HTMLDivElement>(null);
  const [illustration, setIllustration] = useState<illustrationDTO[]>([]);
  const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
      // API 호출하여 데이터 가져오기
    const fetchdata = async () => {
    try {

        const illustration = await illustrationResponse();
        const storyParagraph = await storyParagraphResponse();
        setIllustration(illustration);
        setStoryParagraph(storyParagraph);
      } catch (error) {
        console.error("데이터를 가져오는 중 오류 발생:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchdata();
  }, []);
  

  const [currentPage, setCurrentPage] = useState(0);

  // 페이지 변경 이벤트 핸들러
  const onFlip = (e: FlipEvent) => {
    setCurrentPage(e.data);
  };

  return (
    <>  
      {loading ? (
        <div className="loading">
          <div className="loading-spinner"></div>
          <div className="loading-text">Loading...</div>
        </div>
      ) : (
      <div className="flipbook-wrapper">
        <HTMLFlipBook
          ref={flipBook}
          width={400}
          height={600}
          size="stretch"
          minWidth={315}
          maxWidth={1000}
          minHeight={420}
          maxHeight={1350}
          maxShadowOpacity={0.5}
          showCover={true}
          autoSize={true}
          useMouseEvents={true}
          mobileScrollSupport={false}
          // swipeDistance={30}
          clickEventForward={true}
          usePortrait={true}
          startPage={0}
          drawShadow={true}
          flippingTime={800}
          showPageCorners={true}
          disableFlipByClick={false}
          style={{ margin: '0 auto' }}
          onFlip={onFlip}
          // onChangeOrientation={(orientation) => console.log(orientation)}
          // onChangeState={(state) => console.log(state)}
          className="flipbook"
        >
          {/* 표지 */}
          <div className="bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white p-8">
            <div className="text-center">
              <h2 className="text-4xl font-bold mb-4">숲속 토끼 이야기</h2>
              <p className="text-lg">재미있는 동화의 시작</p>
            </div>
          </div>

          {storyParagraph && storyParagraph.flatMap((storypage, index) => {
          const illust = illustration[index];
          return [
            <div key={`image-${index}`} className="pageflip-page right-page">
              <div className="page-content">
                {illust ? (
                  <Image
                    src={`/images/${illust.image_url ?? "soyee-secret.png"}`}
                    className="w-full h-auto object-cover"
                    alt=""
                    width={384} // 원하는 값
                    height={320} // 원하는 값
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-500">
                    이미지 없음
                  </div>
                )}
              </div>
            </div>,

            <div key={`text-${index}`} className="pageflip-page left-page">
              <div>
                <div className="page-content">
                  {storypage.content_text}
                </div>
                <div className="page-number right-number">
                  {index + 1}
                </div>
              </div>
            </div>
            ];
          })}

          {/* 뒷표지 */}
          <div className="bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center text-white p-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold mb-4">끝</h2>
              <p className="text-lg">재미있게 읽으셨나요?</p>
            </div>
          </div>
        </HTMLFlipBook>
        
        {/* 페이지 정보 및 컨트롤 */}
        {/* <div className="flipbook-controls">
          <div className="page-info">
            페이지 {currentPage + 1} / {pages.length}
          </div>
          
          <div className="control-buttons">
            <button 
              onClick={() => flipBook.current?.pageFlip().flipPrev()}
              disabled={currentPage === 0}
            >
              ← 이전
            </button>
            
            <button 
              onClick={() => flipBook.current?.pageFlip().flipNext()}
              disabled={currentPage === pages.length - 1}
            >
              다음 →
            </button>
          </div>
        </div> */}
      </div>
      )}
    </>
  );
};

export default DynamicFlipBook;