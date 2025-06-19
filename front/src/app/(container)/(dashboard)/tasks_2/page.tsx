"use client";

import axios from 'axios';
import React, { useState, useEffect, useCallback } from 'react';
import '@/styles/tasks_2.css';
import { paragraphQADTO } from '@/lib/type/paragraphQA';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';


interface SlideData {
  id: number;
  title: string;
  background: string;
}

interface ImageCarouselProps {
  slides?: SlideData[];
  title?: string;
  description?: string;
}

const paragraphQAResponse = async (): Promise<paragraphQADTO[]> => {
  const story_id = '2245';
  const res = await axios.post('http://localhost:8721/api/v1/paragraphQA/story/', { story_id });
  return res.data.paragraphQA;
};

const storyParagraphResponse = async (): Promise<storyParagraphDTO[]> => {
  const story_id = '2245';
  const res = await axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id });
  return res.data.storyParagraph;
};






const ImageCarousel: React.FC<ImageCarouselProps> = () => {
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [paragraphQA, setParagraphQA] = useState<paragraphQADTO[]>([]);
  const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);
  const totalSlides = storyParagraph.length;

  // 다음 슬라이드로 이동
  const nextSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev + 1) % totalSlides);
  }, [totalSlides]);

  // 이전 슬라이드로 이동
  const prevSlide = useCallback(() => {
    setCurrentSlide((prev) => (prev - 1 + totalSlides) % totalSlides);
  }, [totalSlides]);

  // 특정 슬라이드로 이동
  const goToSlide = useCallback((index: number) => {
    setCurrentSlide(index);
  }, []);

  useEffect(() => {
    // API 호출하여 데이터 가져오기
    const fetchdata = async () => {
      const paragraphQA = await paragraphQAResponse();
      const storyParagraph = await storyParagraphResponse();
      setParagraphQA(paragraphQA);
      setStoryParagraph(storyParagraph);
    };
    fetchdata();
  }, []);


  // 키보드 이벤트 처리
  useEffect(() => {
    const handleKeyPress = (event: KeyboardEvent) => {
      if (event.key === 'ArrowLeft') {
        prevSlide();
      } else if (event.key === 'ArrowRight') {
        nextSlide();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [nextSlide, prevSlide]);



  // 점 표시기 렌더링
  const renderDots = () => {
    return storyParagraph.map((_, index) => (
      <div
        key={index}
        className={`dot-indicator ${index === currentSlide ? 'dot-active' : 'dot-inactive'} ${
          index === 0 ? 'dot-indicator-1' : `dot-indicator-${index + 1}`
        }`}
        data-slide={index}
        onClick={() => goToSlide(index)}
        role="button"
        tabIndex={0}
        aria-label={`Go to slide ${index + 1}`}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            goToSlide(index);
          }
        }}
      >
        <div className={index === currentSlide ? 'dot-indicator-active' : 'dot-indicator-inactive'}></div>
      </div>
    ));
  };

  return (
    <div className="preview min-h-screen">
      <div className="content">
        <div className="intro-section">
          공백
        </div>
        
        <div className="carousel">
          <div className="slides-box">
            {storyParagraph.map((data, index) => {
              const data_QA = paragraphQA[index];
              return (
              <div
                key={data.paragraph_no}
                className={`slide ${index === currentSlide ? 'active' : ''}`}
                role="img"
              >
                <div className="slide-content">
                    <div className='container_box'> 
                        <div className='container_box_left'>
                            <div className='container_box_left_inner'>
                                <div className='container_box_left_inner_text'>
                                    {data.content_text || '내용이 없습니다'}
                                </div>
                            </div>
                        </div>
                        <div className='container_box_right'>
                            <div className='container_box_right_inner'>
                                <div className='container_box_right_inner_box'>
                                  <div className='container_box_right_inner_box_progress'>
                                    진행상황
                                  </div>
                                  <div className='container_box_right_inner_box_ai'>{data_QA?.ai_question || 'AI 질문이 없습니다'}</div>
                                  <div className='container_box_right_inner_box_user'>유저 선택</div>
                                  <div className='container_box_right_inner_box_temp'>
                                    <div className='container_box_right_inner_box_temp_btn'>임시저장</div>
                                  </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
              </div>
            );
            })}
          </div>
          
          <div className="slides-navigation">
            <button
              className="click-area"
              onClick={prevSlide}
              aria-label="Previous slide"
              type="button"
            >
              <div className="arrow-left">
                <svg className="arrow-svg" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
                </svg>
              </div>
            </button>
            
            <div className="slide-indicator" role="tablist" aria-label="Slide indicators">
              {renderDots()}
            </div>
            
            <button
              className="click-area"
              onClick={nextSlide}
              aria-label="Next slide"
              type="button"
            >
              <div className="arrow-right">
                <svg className="arrow-svg" viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M8.59 16.59L10 18l6-6-6-6-1.41 1.41L13.17 12z"/>
                </svg>
              </div>
            </button>
          </div>
        </div>
        
        <div className="description2">
          <span>
            <span className="description-2-span">clean.design</span>
            <span className="description-2-span">®</span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default ImageCarousel;