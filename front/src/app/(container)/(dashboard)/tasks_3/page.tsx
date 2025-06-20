"use client";

import axios from 'axios';
import React, { useRef, useState , useEffect } from 'react';
import HTMLFlipBook from 'react-pageflip';
import '@/styles/book.css'; // CSS 스타일 파일
import { illustrationDTO } from '@/lib/type/illustration';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';
import { storyDTO } from '@/lib/type/story';
import Image from "next/image";
import Loading from '@/(components)/Loading/loading';

type FlipEvent = { data: number };

const DynamicFlipBook: React.FC = () => {
  const flipBook = useRef<HTMLDivElement>(null);
  const [illustration, setIllustration] = useState<illustrationDTO[]>([]);
  const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);
  const [story, setStory] = useState<storyDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // API 호출하여 데이터 가져오기
    const fetchdata = async () => {
      try {
        // sessionStorage에서 story_id 가져오기 (클라이언트에서만 가능)
        const story_id = sessionStorage.getItem('selectedStoryId') || '2257';
        console.log('tasks_3에서 받은 story_id:', story_id);
        
        // API 호출시 story_id 사용
        const [illustrationRes, storyParagraphRes, storyRes] = await Promise.all([
          axios.post('http://localhost:8721/api/v1/illustration/story/', { story_id }),
          axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id }),
          axios.post('http://localhost:8721/api/v1/story/story/', { story_id }),
        ]);

        console.log('Story 데이터:', storyRes.data.story);
        console.log('Illustration 데이터:', illustrationRes.data.illustration);
        console.log('Story Paragraph 데이터:', storyParagraphRes.data.storyParagraph);
        
        setIllustration(illustrationRes.data.illustration);
        setStoryParagraph(storyParagraphRes.data.storyParagraph);
        setStory(storyRes.data.story);
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
        <Loading />
      ) : (
        <div
          className="flipbook-wrapper"
          style={{
            backgroundImage: "url('/images/task3-bg1.jpg')",
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div
            style={{
              padding: '60px',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              width: '100%',
              height: '100%',
            }}
          >
        <HTMLFlipBook
          ref={flipBook}
          width={384}
          height={480}
          size="stretch"
          minWidth={300}
          maxWidth={500}
          minHeight={400}
          maxHeight={600}
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
            <div className="text-center"style={{
                  height: '100%',
                  padding: '100px 30px',
                  fontFamily: 'Ownglyph_ryurue-Rg',
                }}>
              <h2 className="text-4xl font-bold mb-4">{story.title}</h2>
              <p className="text-lg">이야기 속으로 들어가보아요!</p>
            </div>
          </div>

          {storyParagraph && storyParagraph.flatMap((storypage, index) => {
          const illust = illustration[index];
          console.log('storypage', storypage);
          console.log('illust', illust);
          return [
            <div key={`image-${index}`} className="pageflip-page right-page" style={{
              backgroundColor: 'rgba(255, 255, 255, 0.3)' /* 흰색 배경, 30% 투명도 */
            }}>
              <div className="page-content">
                {illust ? (
                  <Image
                    src={illust.image_url ? `/images/${illust.image_url}` : '/images/soyee-secret.png'}

                    className="w-full h-full object-cover"
                    alt=""
                    width={384} // 원하는 값
                    height={320} // 원하는 값
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-500" style={{
                    fontFamily: 'Ownglyph_ryurue-Rg',
                  }}>
                    이미지 없음
                  </div>
                )}
              </div>
            </div>,

            <div key={`text-${index}`} className="pageflip-page left-page">
              <div style={{
                backgroundColor: '#faf6ed', /* 배경색 더욱 연하게 수정 */
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between'
              }}>
                <div className="page-content" style={{
                  color: '#1a1a1a',
                  fontSize: '1.65rem',
                  fontWeight: '700',
                  lineHeight: '1.75',
                  letterSpacing: '0.3rem', /* 글자 간격 추가 */
                  padding: '26px',
                  fontFamily: 'Ownglyph_ryurue-Rg',
                }}>
                  {storypage.content_text}
                </div>
                <div className="page-number right-number" style={{
                  color: '#4b5563',
                  fontSize: '16px',
                  fontWeight: '600',
                  fontFamily: 'Ownglyph_ryurue-Rg',
                }}>
                  {index + 1}
                </div>
              </div>
            </div>
            ];
          })}

          {/* 뒷표지 */}
          <div className="end_page flex items-center justify-center text-white p-8">
            <div className="end_page_text text-center" style={{
                  height: '100%',
                  padding: '100px',
                  fontFamily: 'Ownglyph_ryurue-Rg',
                }}>
              <h2 className="text-3xl font-bold mb-4">끝</h2>
              <p className="text-lg">재미있게 읽으셨나요?</p>
            </div>
          </div>
          </HTMLFlipBook>
          </div>
      </div>
      )}
    </>
  );
};

export default DynamicFlipBook;