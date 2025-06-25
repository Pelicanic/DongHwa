"use client";

import React from 'react';
import { apiClient, API_ROUTES } from '@/lib/api';
import { createPageDebugger } from '@/lib/logger';
import { useState, useCallback, useEffect } from 'react';
import '@/styles/tasks_1.css';
import Swal from 'sweetalert2'
import { requireLogin } from '@/lib/utils/auth';

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
      title: "무슨 동화를 좋아해 ?",
      choices: ["여우와 두루미", "개미와 베짱이", "토끼와 거북이"]
    },
    {
      id: 2,
      title: "이야기 속 세상은 어떤 게 재밌을까?",
      choices: ["고전", "판타지", "현대", "로맨스", "미스터리"]
    },
    {
      id: 3,
      title: "이야기 속 기분은 어땠으면 좋겠어?",
      choices: ["밝은", "따뜻한", "슬픈", "신비로운", "무서운"]
    },
    {
      id: 4,
      title: "주인공에게 우리만의 특별한 이름을 지어주자!",
      choices: ["마리", "제이슨", "루시", "철수", "영희"]
    },
    {
      id: 5,
      title: "어떤 주인공이 더 재밌는 이야기를 만들어줄 것 같아?",
      choices: ["남자", "여자", "무관"]
    }
  ],
}) => {
  // 슬라이드 데이터를 상태로 관리 (랜덤 기능을 위해)
  const [slidesData, setSlidesData] = useState<SlideData[]>(slides);
  
  // Tasks_1 페이지 전용 디버거
  const debug = createPageDebugger('TASKS_1');
  
  // 랜덤 제목 가져오기 함수
  const fetchRandomTitles = useCallback(async () => {
    try {
      debug.api('랜덤 제목 요청', {});
      const response = await apiClient.get(API_ROUTES.RANDOM_PUBLISHED_TITLES);
      
      if (response.data.success && response.data.titles) {
        const randomTitles = response.data.titles;
        debug.story('랜덤 제목 수신', {
          'Random Titles': randomTitles
        });
        
        // 첫 번째 슬라이드의 선택지를 업데이트
        setSlidesData(prev => {
          const updated = prev.map((slide, index) => 
            index === 0 ? { ...slide, choices: [...randomTitles] } : slide
          );
          console.log('업데이트된 슬라이드 데이터:', updated); // 디버깅
          return updated;
        });
        
        // 첫 번째 슬라이드의 선택된 답변과 선택지 초기화
        setUserAnswers(prev => {
          const newAnswers = { ...prev };
          delete newAnswers[0];
          return newAnswers;
        });
        setSelectedChoices(prev => ({
          ...prev,
          0: null
        }));
        
        console.log('랜덤 제목으로 업데이트 완료:', randomTitles); // 디버깅
        
      } else {
        debug.error('랜덤 제목 요청 실패', response.data);
        console.log('API 응답이 예상과 다름:', response.data); // 디버깅
      }
    } catch (error) {
      debug.error('랜덤 제목 API 오류', error);
      console.error('API 호출 오류:', error); // 디버깅
    }
  }, []);
  
  // 로그인 확인
  useEffect(() => {
    requireLogin();
  }, []);
  
  // useRouter 훅 추가
  // 현재 슬라이드 인덱스를 저장하는 state
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  // 각 슬라이드별 사용자 답변을 저장하는 state
  const [userAnswers, setUserAnswers] = useState<{[key: number]: string}>({});
  // 현재 선택된 선택지를 저장하는 state (시각적 표시용)
  const [selectedChoices, setSelectedChoices] = useState<{[key: number]: number | null}>({});
  // 전체 슬라이드 수
  const totalSlides = slidesData.length;
  // 선택지 클릭 핸들러
  const handleChoiceClick = useCallback((slideIndex: number, choiceIndex: number, choiceText: string) => {
    debug.user('선택지 클릭', {
      'Slide Index': slideIndex,
      'Choice Index': choiceIndex,
      'Choice Text': choiceText
    });
    
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
    
    debug.story('사용자 선택 완료', {
      'Slide Number': slideIndex + 1,
      'Selected Text': choiceText
    });
  }, []);

  // input 값 직접 변경 핸들러
  const handleInputChange = useCallback((slideIndex: number, value: string) => {
    debug.user('입력 값 변경', {
      'Slide Index': slideIndex,
      'Input Value': value
    });
    
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      
      if (value.trim() === '') {
        // 빈 값일 때는 해당 키를 아예 삭제
        delete newAnswers[slideIndex];
      } else {
        // 값이 있을 때만 저장
        newAnswers[slideIndex] = value;
      }
      
      debug.log('답변 상태 업데이트', {
        'New Answers': newAnswers
      });
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
        debug.story('스토리 생성 시작', {
          'User Answers': userAnswers,
          'Total Questions': totalSlides,
          'Completion Rate': `${answeredCount}/${totalSlides}`
        });

        // 로딩 표시
        Swal.fire({
          title: '이야기를 생성하고 있습니다...',
          allowOutsideClick: false,
          didOpen: () => {
            Swal.showLoading();
          }
        });

        debug.story('스토리 생성 API 호출', {
          'Request Data': {
            answers: userAnswers,
            paragraph_no: '1',
            user_id: '774',
            mode: 'create'
          }
        });
        const response = await apiClient.post(API_ROUTES.STORY_CREATE, {
          answers: userAnswers,
          paragraph_no : '1',
          user_id: '774', // 실제 사용자 ID로 변경 필요
          mode: 'create',
        });

        const storyData = response.data;

        debug.story('스토리 생성 성공', {
          'Generated Story Data': storyData,
          'User Answers': userAnswers
        });

        // 성공 메시지 표시
        await Swal.fire({
          title: "자 이제 이야기 속으로 떠나볼까?!",
          confirmButtonText: "가자 !",
          icon: "success"
        });

        // 생성된 스토리 ID와 함께 페이지 이동
        sessionStorage.setItem('storyData', JSON.stringify({
          ...storyData,
          answers: userAnswers // tasks_1에서 선택한 답변들 추가
        }));
        // router.push('/tasks_2');
        window.location.href = '/tasks_2';

      } catch (error) {
        debug.error('스토리 생성 오류', error, {
          'User Answers': userAnswers,
          'Request Parameters': {
            paragraph_no: '1',
            user_id: '774',
            mode: 'create'
          }
        });
        
        Swal.fire({
          title: "오류가 발생했습니다",
          text: "스토리 생성에 실패했습니다. 다시 시도해주세요.",
          icon: "error"
        });
      }
    }
  }, [userAnswers, totalSlides]);

  // 점 표시기 렌더링
  const renderDots = () => {
    return slidesData.map((_, index) => (
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
            {/* <h2>질문에 답해주세요</h2>
            <p>선택지를 클릭하거나 직접 입력하세요</p> */}
          </div>
        </div>
        
        {/* 메인 컨텐츠 영역을 flex로 구성 */}
        <div className="main-content-wrapper">
          <div className="carousel">
            <div className="slides-box">
              {slidesData.map((slide, index) => (
                <div
                  key={slide.id}
                  className={`slide ${index === currentSlide ? 'active' : ''}`}
                  role="img"
                >
                  <div className="slide-content">
                    <div className='slide-content-box' style={{
                      backgroundColor: '#faf6ed'
                    }}>
                      <div className='slide-content-box-question' style={{
                        backgroundColor: '#faf6ed',
                      }}>
                        <h3>{slide.title}</h3>
                        
                        {index === 0 && (
                          <div style={{ marginTop: '10px' }}>
                            <button
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                fetchRandomTitles();
                              }}
                              className="random-button"
                              type="button"
                              style={{
                                padding: '10px 20px',
                                backgroundColor: '#ff6b6b',
                                color: 'white',
                                border: '2px solid #ff6b6b',
                                borderRadius: '25px',
                                fontSize: '14px',
                                fontWeight: 'bold',
                                cursor: 'pointer',
                                transition: 'all 0.3s ease',
                                boxShadow: '0 4px 8px rgba(255, 107, 107, 0.3)',
                                zIndex: 99999,
                                position: 'relative',
                                pointerEvents: 'auto',
                                display: 'block',
                                width: 'auto'
                              }}
                              onMouseOver={(e) => {
                                console.log('버튼 호버!');
                                e.currentTarget.style.backgroundColor = '#ff5252';
                                e.currentTarget.style.transform = 'scale(1.05)';
                                e.currentTarget.style.boxShadow = '0 6px 12px rgba(255, 82, 82, 0.4)';
                              }}
                              onMouseOut={(e) => {
                                e.currentTarget.style.backgroundColor = '#ff6b6b';
                                e.currentTarget.style.transform = 'scale(1)';
                                e.currentTarget.style.boxShadow = '0 4px 8px rgba(255, 107, 107, 0.3)';
                              }}
                            >
                              🎲 랜덤 동화 제목
                            </button>
                          </div>
                        )}
                      </div>
                      
                      <div className='slide-content-box-ai-question' style={{
                        backgroundColor: '#faf6ed'
                      }}>
                      <input 
                      type="text" 
                      name={`userAnswer_${index}`}
                      value={userAnswers[index] || ''}
                      onChange={(e) => handleInputChange(index, e.target.value)}
                      placeholder="답변을 입력하거나 아래 선택지를 클릭하세요"
                      className="answer-input"
                      style={{
                        backgroundColor: '#faf6ed'
                      }}
                        key={`input-${index}`}
                          data-slide={index}
                      />
                    </div>
                      
                      <div className='slide-content-box-user-question' style={{
                        backgroundColor: '#faf6ed'
                      }}>
                        <div className='slide-content-box-user-question-btn' style={{
                          backgroundColor: '#faf6ed'
                        }}>
                          {slide.choices.map((choice, choiceIndex) => (
                            <div
                              key={choiceIndex}
                              className={`choice-button ${
                                selectedChoices[index] === choiceIndex ? 'choice-selected' : ''
                              }`}
                              onClick={(e) => {
                                e.preventDefault();
                                e.stopPropagation();
                                debug.user('선택지 버튼 클릭', {
                                  'Slide Index': index,
                                  'Choice Index': choiceIndex,
                                  'Choice Text': choice
                                });
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
              {slidesData.map((slide, index) => (
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