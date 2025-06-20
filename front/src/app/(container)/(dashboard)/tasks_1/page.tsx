"use client";

import React from 'react';
import axios from 'axios';

import { useState, useCallback } from 'react';
import '@/styles/tasks_1.css';
import Swal from 'sweetalert2'

interface SlideData {
  id: number;
  title: string;
  choices: string[]; // 선택지 배열 추가
}

interface ImageCarouselProps {
  slides?: SlideData[];
  title?: string;
  description?: string;
}

const InteractiveCarousel: React.FC<ImageCarouselProps> = ({
  slides = [
    {
      id: 1,
      title: "어떤 이야기를 참고해서 만들까 ?",
      choices: ["여우와 두루미", "개미와 베짱이", "토끼와 거북이"]
    },
    {
      id: 2,
      title: "테마는 어떻게 할까?",
      choices: ["고전", "판타지", "현대", "로맨스", "미스터리"]
    },
    {
      id: 3,
      title: "이야기 속의 분위기는 어때?",
      choices: ["밝은", "따뜻한", "슬픈", "신비로운", "무서운"]
    },
    {
      id: 4,
      title: "주인공의 이름을 정해봐!",
      choices: ["마리", "제이슨", "루시", "철수", "영희"]
    },
    {
      id: 5,
      title: "짠! 마법의 주인공 뽑기 시간이야! 어떤 주인공이 더 재밌는 이야기를 만들어줄 것 같아?",
      choices: ["남자", "여자", "무관"]
    }
  ],
}) => {
  // useRouter 훅 추가
  // 현재 슬라이드 인덱스를 저장하는 state
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  // 각 슬라이드별 사용자 답변을 저장하는 state
  const [userAnswers, setUserAnswers] = useState<{[key: number]: string}>({});
  // 현재 선택된 선택지를 저장하는 state (시각적 표시용)
  const [selectedChoices, setSelectedChoices] = useState<{[key: number]: number | null}>({});
  // 전체 슬라이드 수
  const totalSlides = slides.length;
  // 선택지 클릭 핸들러
  const handleChoiceClick = useCallback((slideIndex: number, choiceIndex: number, choiceText: string) => {
    console.log(`Choice clicked - Slide: ${slideIndex}, Choice: ${choiceIndex}, Text: ${choiceText}`);
    
    // 해당 슬라이드의 input에 선택한 값 설정
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      
      if (choiceText.trim() === '') {
        // 빈 값일 때는 해당 키를 아예 삭제
        delete newAnswers[slideIndex];
      } else {
        // 값이 있을 때만 저장
        newAnswers[slideIndex] = choiceText;
      }
      
      return newAnswers;
    });
    
    // 선택된 선택지 인덱스 저장 (하이라이트 표시용)
    setSelectedChoices(prev => ({
      ...prev,
      [slideIndex]: choiceIndex
    }));
    
    console.log(`슬라이드 ${slideIndex + 1}에서 "${choiceText}" 선택됨`);
  }, []);

  // input 값 직접 변경 핸들러
  const handleInputChange = useCallback((slideIndex: number, value: string) => {
    console.log(`Input change - Slide: ${slideIndex}, Value: ${value}`);
    
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      
      if (value.trim() === '') {
        // 빈 값일 때는 해당 키를 아예 삭제
        delete newAnswers[slideIndex];
      } else {
        // 값이 있을 때만 저장
        newAnswers[slideIndex] = value;
      }
      
      console.log('New answers state:', newAnswers);
      return newAnswers;
    });
    
    // 직접 입력 시 선택지 하이라이트 해제
    setSelectedChoices(prev => ({
      ...prev,
      [slideIndex]: null
    }));
  }, []);

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

  // 모든 답변 제출 함수
  const handleSubmitAllAnswers = useCallback(async () => {
    const answeredCount = Object.keys(userAnswers).length;
    
    if (answeredCount !== totalSlides) {
      alert(`모든 질문에 답변해주세요. (현재 ${answeredCount}/${totalSlides} 완료)`);
      return;
    }
    
    const result = await Swal.fire({
      title: "이렇게 이야기를 만들어볼까?",
      text: `선택지 : \n${Object.entries(userAnswers).map(([slideIndex, answer]) => 
      `슬라이드 ${parseInt(slideIndex) + 1}: ${answer}`).join('\n')}`,
      icon: "question",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      cancelButtonText: "잠깐만!",
      confirmButtonText: "좋아!"
    });

    if (result.isConfirmed) {
      try {
        // 로딩 표시
        Swal.fire({
          title: '이야기를 생성하고 있습니다...',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        // 백엔드에 답변 데이터 전송
        // axios로 백엔드에 답변 데이터 전송
        const response = await axios.post('http://localhost:8721/api/v1/chat/story/', {
          answers: userAnswers,
          paragraph_no : '1',
          user_id: '774', // 실제 사용자 ID로 변경 필요
          mode: 'create',
        });

        const storyData = response.data;

        // 성공 메시지 표시
        await Swal.fire({
          title: "자 이제 이야기 속으로 떠나볼까?!",
          confirmButtonText: "가자 !",
          icon: "success"
        });

        // 생성된 스토리 ID와 함께 페이지 이동
        sessionStorage.setItem('storyData', JSON.stringify(storyData));
        // router.push('/tasks_2');
        location.href = '/tasks_2';

      } catch (error) {
        console.error('스토리 생성 오류:', error);
        
        Swal.fire({
          title: "오류가 발생했습니다",
          text: "스토리 생성에 실패했습니다. 다시 시도해주세요.",
          icon: "error"
        });
      }
    }
  }, [userAnswers, totalSlides]);

        // Swal.fire({
        //   title: "자 이제 이야기 속으로 떠나볼까?!",
        //   confirmButtonText: "가자!",
        //   icon: "success"
        // }).then(() => {
        //   const params = new URLSearchParams();
        //   params.set('answers', JSON.stringify(userAnswers));
        //   router.push(`/tasks_2?${params.toString()}`);
          // alert("이제 이야기를 만들어볼 시간입니다!");
          // Router.push({
          //   pathname: '/tasks_2',
          //   query: {
          //     answers: JSON.stringify(userAnswers) // 사용자 답변을 쿼리 파라미터로 전달
          //   }
          // }); // 실제 스토리 페이지로 이동
        // });
  //     }
  //   });
  // }, [userAnswers, totalSlides, router]);

  // 키보드 이벤트 처리
  // useEffect(() => {
  //   const handleKeyPress = (event: KeyboardEvent) => {
  //     if (event.key === 'ArrowLeft') {
  //       prevSlide();
  //     } else if (event.key === 'ArrowRight') {
  //       nextSlide();
  //     } else if (event.key >= '1' && event.key <= '3') {
  //       // 숫자 1,2,3 키로 선택지 선택
  //       const choiceIndex = parseInt(event.key) - 1;
  //       const currentSlideData = slides[currentSlide];
  //       if (currentSlideData.choices[choiceIndex]) {
  //         handleChoiceClick(currentSlide, choiceIndex, currentSlideData.choices[choiceIndex]);
  //       }
  //     }
  //   };

  //   window.addEventListener('keydown', handleKeyPress);
  //   return () => window.removeEventListener('keydown', handleKeyPress);
  // }, [nextSlide, prevSlide, currentSlide, slides, handleChoiceClick]);

  // 점 표시기 렌더링
  const renderDots = () => {
    return slides.map((_, index) => (
      <div
        key={index}
        className={`dot-indicator ${index === currentSlide ? 'dot-active' : 'dot-inactive'} ${
          index === 0 ? 'dot-indicator-1' : `dot-indicator-${index + 1}`
        } ${userAnswers[index] ? 'dot-completed' : ''}`} // 답변 완료된 슬라이드 표시
        data-slide={index}
        onClick={() => goToSlide(index)}
        role="button"
        tabIndex={0}
        aria-label={`Go to slide ${index + 1}${userAnswers[index] ? ' (답변 완료)' : ''}`}
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
    <div
      className="preview min-h-screen bg-no-repeat"
      style={{
        backgroundImage: "url('/images/task1-bg.jpg')",
        backgroundSize: 'auto 105%',
        backgroundPosition: 'auto 100%',
      }}
    >
      <div className="content">
        <div className="intro-section">
          <div className="intro-text">
            <h2>질문에 답해주세요</h2>
            <p>선택지를 클릭하거나 직접 입력하세요</p>
          </div>
        </div>
        
        {/* 메인 컨텐츠 영역을 flex로 구성 */}
        <div className="main-content-wrapper">
          <div className="carousel">
            <div className="slides-box">
              {slides.map((slide, index) => (
                <div
                  key={slide.id}
                  className={`slide ${index === currentSlide ? 'active' : ''}`}
                  role="img"
                >
                  <div className="slide-content">
                    <div className='slide-content-box'>
                      <div className='slide-content-box-question'>
                        <h3>{slide.title}</h3>
                        <span className="slide-number">({index + 1}/{totalSlides})</span>
                      </div>
                      
                      <div className='slide-content-box-ai-question'>
                      <input 
                      type="text" 
                      name={`userAnswer_${index}`}
                      value={userAnswers[index] || ''}
                      onChange={(e) => handleInputChange(index, e.target.value)}
                      placeholder="답변을 입력하거나 아래 선택지를 클릭하세요"
                      className="answer-input"
                        key={`input-${index}`}
                          data-slide={index}
                      />
                    </div>
                      
                      <div className='slide-content-box-user-question'>
                        <div className='slide-content-box-user-question-btn'>
                          {slide.choices.map((choice, choiceIndex) => (
                            <div
                              key={choiceIndex}
                              className={`choice-button ${
                                selectedChoices[index] === choiceIndex ? 'choice-selected' : ''
                              }`}
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                console.log(`Button clicked: Slide ${index}, Choice ${choiceIndex}`);
                                handleChoiceClick(index, choiceIndex, choice);
                              }}
                              role="button"
                              tabIndex={0}
                              aria-label={`선택지 ${choiceIndex + 1}: ${choice}`}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter' || e.key === ' ') {
                                  e.preventDefault();
                                  handleChoiceClick(index, choiceIndex, choice);
                                }
                              }}
                              style={{
                                pointerEvents: 'auto',
                                zIndex: 10,
                                position: 'relative'
                              }}
                            >
                              <span className="choice-text">{choice}</span>
                              {selectedChoices[index] === choiceIndex && (
                                <span className="choice-check">✓</span>
                              )}
                            </div>
                          ))}
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

          {/* 답변 요약을 carousel 밖으로 이동 */}
          <div className="answer-summary">
            <div className="summary-header">
              <h3>답변 현황</h3>
              <span className="completion-rate">
                {Object.keys(userAnswers).length}/{totalSlides} 완료
              </span>
            </div>
            
            <div className="summary-grid">
              {slides.map((slide, index) => (
                <div 
                  key={index} 
                  className={`summary-item ${userAnswers[index] ? 'completed' : 'pending'}`}
                  onClick={() => goToSlide(index)}
                >
                  <div className="summary-question">Q{index + 1}. {slide.title}</div>
                  <div className="summary-answer">
                    {userAnswers[index] || '답변 없음'}
                  </div>
                </div>
              ))}
            </div>

            <button 
              className="submit-button"
              onClick={handleSubmitAllAnswers}
              disabled={Object.keys(userAnswers).length !== totalSlides}
            >
              {Object.keys(userAnswers).length === totalSlides 
                ? `모든 답변 제출 (${Object.keys(userAnswers).length}/${totalSlides})` 
                : `답변 완료 후 제출 가능 (${Object.keys(userAnswers).length}/${totalSlides})`
              }
            </button>
          </div>
        </div>
        <div className="description2">
          <span>
            <span className="description-2-span">pel-world</span>
            <span className="description-2-span">®</span>
          </span>
        </div>
      </div>
    </div>
  );
};

export default InteractiveCarousel;