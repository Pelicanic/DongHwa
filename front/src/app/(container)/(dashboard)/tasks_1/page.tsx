"use client";

import React, { useState, useEffect, useCallback } from 'react';
import '@/styles/tasks_1.css';

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

const ImageCarousel: React.FC<ImageCarouselProps> = ({
  slides = [
    {
      id: 1,
      title: "Slide 1",
    },
    {
      id: 2,
      title: "Slide 2",
    },
    {
      id: 3,
      title: "Slide 3",
    },
    {
      id: 4,
      title: "Slide 4",
    },
    {
      id: 5,
      title: "Slide 5",
    }
  ],
}) => {
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const totalSlides = slides.length;

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
    return slides.map((_, index) => (
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
            {slides.map((slide, index) => (
              <div
                key={slide.id}
                className={`slide ${index === currentSlide ? 'active' : ''}`}
                role="img"
              >
                <div 
                  className="slide-content" 
                >
                  <div className='slide-content-box'>
                    <div className='slide-content-box-question'>{slide.title}</div>
                    <div className='slide-content-box-ai-question'>질문2</div>
                    <div className='slide-content-box-user-question'>
                      
                      <div className='slide-content-box-user-question-text'>
                        <input type="text" placeholder="사용자 질문"/>
                      </div>
                      <div className='slide-content-box-user-question-btn'>
                        <div>선택지1</div>
                        <div>선택지2</div>
                        <div>선택지3</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
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