'use client';

import React, { useRef, useEffect, useState } from 'react';
import HTMLFlipBook from 'react-pageflip';
import { illustrationDTO } from '@/lib/type/illustration';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';
import Image from "next/image";

// interface PageData {
//   id: number;
//   content: string;
//   title?: string;
//   isLeft?: boolean; // 왼쪽 페이지인지 구분
// }


interface PageFlipProps {
  illustration?: illustrationDTO[];
  storyParagraph?: storyParagraphDTO[];
  width?: number;
  height?: number;
  size?: 'fixed' | 'stretch';
  minWidth?: number;
  maxWidth?: number;
  minHeight?: number;
  maxHeight?: number;
  drawShadow?: boolean;
  flippingTime?: number;
  usePortrait?: boolean;
  startZIndex?: number;
  autoSize?: boolean;
  maxShadowOpacity?: number;
  showCover?: boolean;
  mobileScrollSupport?: boolean;
  swipeDistance?: number;
  clickEventForward?: boolean;
  useMouseEvents?: boolean;
  disableFlipByClick?: boolean;
}

type FlipEvent = { data: number };

const PageFlip: React.FC<PageFlipProps> = ({
  illustration = [],
  storyParagraph = [],
  width = 400,
  height = 600,
  size = 'fixed',
  minWidth = 315,
  maxWidth = 1000,
  minHeight = 420,
  maxHeight = 1350,
  drawShadow = true,
  flippingTime = 1000,
  usePortrait = false, // 양쪽 보기에서는 landscape 모드
  startZIndex = 0,
  autoSize = true,
  maxShadowOpacity = 0.5,
  showCover = true, // 표지 보이기
  mobileScrollSupport = true,
  swipeDistance = 30,
  clickEventForward = true,
  useMouseEvents = true,
  disableFlipByClick = false
}) => {
  const bookRef = useRef<HTMLDivElement>(null); // 또는 라이브러리에서 제공하는 ref 타입
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(storyParagraph.length);

  useEffect(() => {
    setTotalPages(storyParagraph.length*2);
  }, [storyParagraph]);

  // 페이지 변경 이벤트 핸들러
  const onFlip = (e: FlipEvent) => {
    setCurrentPage(e.data);
  };

  // 현재 보이는 페이지 범위 계산
  const getCurrentSpread = () => {
    if (currentPage === 0) {
      return { left: 0, right: 1 }; // 표지와 첫 페이지
    }
    const leftPage = currentPage;
    const rightPage = currentPage + 1;
    return { 
      left: leftPage <= totalPages - 1 ? leftPage : null, 
      right: rightPage <= totalPages - 1 ? rightPage : null 
    };
  };

  const spread = getCurrentSpread();

  return (
    <div className="pageflip-container dual-page">
      {/* 플립북 */}
      <HTMLFlipBook
        ref={bookRef}
        width={width}
        height={height}
        size={size}
        minWidth={minWidth}
        maxWidth={maxWidth}
        minHeight={minHeight}
        maxHeight={maxHeight}
        drawShadow={drawShadow}
        flippingTime={flippingTime}
        usePortrait={usePortrait}
        startZIndex={startZIndex}
        autoSize={autoSize}
        maxShadowOpacity={maxShadowOpacity}
        showCover={showCover}
        mobileScrollSupport={mobileScrollSupport}
        swipeDistance={swipeDistance}
        clickEventForward={clickEventForward}
        useMouseEvents={useMouseEvents}
        disableFlipByClick={disableFlipByClick}
        onFlip={onFlip}
        className="pageflip-book dual-page-book"
      >

        {/* 표지 */}
        <div className="bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white p-8">
          <div className="text-center">
            <h2 className="text-4xl font-bold mb-4">숲속 토끼 이야기</h2>
            <p className="text-lg">재미있는 동화의 시작</p>
          </div>
        </div>

        {/* 스토리 페이지들 - 각 단락마다 이미지(왼쪽) + 텍스트(오른쪽) 쌍으로 생성 */} 
        {/* {storyParagraph && storyParagraph.flatMap((storypage, index) => {
        const illust = illustration[index];
        return [
          <div key={`image-${storypage.paragraph_no}`} className="pageflip-page right-page">
            <div className="page-content">
              {illust ? (
                <Image
                  src={illust.image_url ?? "/placeholder.png"}
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
            <div className="page-number left-number">
              {index + 1}
            </div> */}
            {/* 페이지 구분선 (가운데) */}
            {/* {index % 2 === 0 && (
              <div className="page-divider"></div>
            )}
          </div>,

          <div key={`text-${storypage.paragraph_no}`} className="pageflip-page left-page">
            <div>
              <div className="page-content">
                {storypage.content_text}
              </div>
              <div className="page-number right-number">
                {index + 1}
              </div> */}
              {/* 페이지 구분선 (가운데) */}
              {/* {index % 2 === 1 && (
                <div className="page-divider"></div>
              )}
            </div>
          </div>
          ];
        })} */}

        {/* 뒷표지 */}
        <div className="bg-gradient-to-br from-green-500 to-blue-500 flex items-center justify-center text-white p-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">끝</h2>
            <p className="text-lg">재미있게 읽으셨나요?</p>
          </div>
        </div>
      </HTMLFlipBook>
    </div>
  );
};

export default PageFlip;