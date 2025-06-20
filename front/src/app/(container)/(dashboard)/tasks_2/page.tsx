"use client";

import axios from 'axios';
import React, { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import '@/styles/tasks_2.css';
import Loading from '@/(components)/Loading/loading';
// import { paragraphQADTO } from '@/lib/type/paragraphQA';
// import { storyParagraphDTO } from '@/lib/type/storyParagraph';


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


// const paragraphQAResponse = async (story_id : string): Promise<paragraphQADTO[]> => {
//   const res = await axios.post('http://localhost:8721/api/v1/paragraphQA/story/', { story_id });
//   return res.data.paragraphQA;
// };

// const storyParagraphResponse = async (story_id : string): Promise<storyParagraphDTO[]> => {
//   const res = await axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id });
//   return res.data.storyParagraph;
// };

export const useStoryData = () => {
  const [storyData, setStoryData] = useState(null);
  const [paragraphQA, setParagraphQA] = useState([]);
  const [storyParagraph, setStoryParagraph] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastParagraphIndex, setLastParagraphIndex] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (typeof window === 'undefined') return;
        
        const savedData = sessionStorage.getItem('storyData');
        const parsedData = JSON.parse(savedData || '{}');
        setStoryData(parsedData);

        console.log("parsedData:", parsedData);

        const story_id = parsedData.story_id;
        
        const [qaResponse, paragraphResponse] = await Promise.all([
          axios.post('http://localhost:8721/api/v1/paragraphQA/story/', { story_id }),
          axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id })
        ]);

        setParagraphQA(qaResponse.data.paragraphQA);
        setStoryParagraph(paragraphResponse.data.storyParagraph);
        
        // 마지막 paragraph_no 찾기
        const paragraphs = paragraphResponse.data.storyParagraph;
        if (paragraphs.length > 0) {
          const maxParagraphNo = Math.max(...paragraphs.map(p => p.paragraph_no));
          const lastIndex = paragraphs.findIndex(p => p.paragraph_no === maxParagraphNo);
          setLastParagraphIndex(lastIndex >= 0 ? lastIndex : paragraphs.length - 1);
        }

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return { storyData, paragraphQA, storyParagraph, loading, lastParagraphIndex };
};




const ImageCarousel: React.FC<ImageCarouselProps> = () => {
  const router = useRouter();
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  // const [paragraphQA, setParagraphQA] = useState<paragraphQADTO[]>([]);
  // const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);
  const { paragraphQA, storyParagraph, loading, lastParagraphIndex } = useStoryData();

  // 마지막 paragraph 인덱스로 초기 슬라이드 설정
  useEffect(() => {
    if (!loading && storyParagraph.length > 0) {
      setCurrentSlide(lastParagraphIndex);
    }
  }, [loading, lastParagraphIndex, storyParagraph.length]);

  console.log("paragraphQA:", paragraphQA);
  console.log("storyParagraph:", storyParagraph);

  // 각 슬라이드별 사용자 답변을 저장하는 state (tasks_1과 동일)
  const [userAnswers, setUserAnswers] = useState<{[key: number]: string}>({});
  // 현재 선택된 선택지를 저장하는 state (시각적 표시용)
  const [selectedChoices, setSelectedChoices] = useState<{[key: number]: number | null}>({});
  
  const totalSlides = storyParagraph.length;

  // 선택지 클릭 핸들러 (tasks_1과 동일)
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

  // input 값 직접 변경 핸들러 (tasks_1과 동일)
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

  
  // useEffect(() => {
  //   // API 호출하여 데이터 가져오기
  //   const fetchdata = async () => {

  //     const parsedData = JSON.parse(sessionStorage.getItem('storyData') || '{}');
  //     console.log("parsedData:", parsedData);

  //     const story_id = parsedData.story_id;
  //     console.log("story_id:", story_id);

  //     const paragraphQA = await paragraphQAResponse(story_id);
  //     const storyParagraph = await storyParagraphResponse(story_id);
  //     setParagraphQA(paragraphQA);
  //     setStoryParagraph(storyParagraph);
  //   };
  //   fetchdata();
  // }
  // , []);


  // 키보드 이벤트 처리
  // useEffect(() => {
  //   const handleKeyPress = (event: KeyboardEvent) => {
  //     if (event.key === 'ArrowLeft') {
  //       prevSlide();
  //     } else if (event.key === 'ArrowRight') {
  //       nextSlide();
  //     }
  //   };

  //   window.addEventListener('keydown', handleKeyPress);
  //   return () => window.removeEventListener('keydown', handleKeyPress);
  // }, [nextSlide, prevSlide]);



  // 점 표시기 렌더링 (tasks_1과 동일 - 답변 완료 상태 표시)
  const renderDots = () => {
    return storyParagraph.map((_, index) => (
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
    <>
      {loading ? (
        <Loading/>
        ) : (
        <div className="preview min-h-screen">
          <div className="content">
            <div className="intro-section">
              {/* 공백 */}
            </div>
            
            <div className="carousel">
              <div className="slides-box">
                {storyParagraph.map((data, index) => {
                  const data_QA = paragraphQA[index];
                  const selectedChoice = userAnswers[index]; // userAnswers 사용
                  
                  const choices = ['선택지1', '선택지2', '선택지3'];
                  
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
                                <div className='container_box_right_inner_box_ai'>
                                  {data_QA?.ai_question || 'AI 질문이 없습니다'}
                                </div>
                                
                                <div className='container_box_right_inner_box_user'>
                                  <div className='user-interaction-grid'>
                                    {/* 텍스트 작성 영역 */}
                                    <div className='text-input-area'>
                                      <div className='selected-text-display'>
                                        <input 
                                          type="text" 
                                          name={`userAnswer_${index}`}
                                          value={selectedChoice || ''}
                                          onChange={(e) => handleInputChange(index, e.target.value)}
                                          placeholder="이야기를 작성해 보아요!"
                                          className="answer-input"
                                          key={`input-${index}`}
                                          data-slide={index}
                                        />
                                      </div>
                                    </div>

                                    {/* 선택지 버튼들 */}
                                    <div className="choice-buttons-grid">
                                      {choices.map((choice, choiceIndex) => (
                                        <button
                                          key={choiceIndex}
                                          className={`choice-btn ${
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
                                        </button>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                                
                                
                                
                                {/* <div className='container_box_right_inner_box_temp'>
                                  <div className='container_box_right_inner_box_temp_btn'>임시저장</div>
                                </div> */}
                                <div className='next-button-area'>
                                  {index === 10 ? (
                                    <button 
                                      className="next-btn bg-green-500 hover:bg-green-600" 
                                      onClick={() => {
                                        // 메인 페이지로 이동
                                        location.href = '/';
                                      }}
                                    >
                                      완료
                                    </button>
                                  ) : (
                                    // 마지막 슬라이드일 때만 "다음" 버튼 표시
                                    index === lastParagraphIndex && (
                                      <button 
                                        className={`next-btn ${
                                          selectedChoice && selectedChoice.trim() !== '' && !isSubmitting
                                            ? 'bg-blue-500 hover:bg-blue-600 text-white' 
                                            : 'bg-gray-300 text-gray-500'
                                        }`}
                                        disabled={!selectedChoice || selectedChoice.trim() === '' || isSubmitting}
                                        onClick={async () => {
                                          if (selectedChoice && selectedChoice.trim() !== '' && !isSubmitting) {
                                            setIsSubmitting(true);
                                            console.log(`선택된 답변: ${selectedChoice}`);
                                            console.log(`선택된 선택지 인덱스:`, selectedChoices[index]);
                                            console.log(`현재 슬라이드: ${index + 1}`);
                                            console.log(`user_id: ${localStorage.getItem('user_id')}`);
                                            console.log(`story_id: ${JSON.parse(sessionStorage.getItem('storyData') || '{}').story_id}`);
                                            try {
                                              // 백엔드에 데이터 전송
                                              const response = await axios.post('http://localhost:8721/api/v1/chat/story/', {
                                                // paragraph_no: index + 1,
                                                user_input: selectedChoice,
                                                story_id: JSON.parse(sessionStorage.getItem('storyData') || '{}').story_id,
                                                user_id: localStorage.getItem('user_id') || '774'
                                              });
                                              
                                              console.log(`답변 저장 성공: ${selectedChoice}`);
                                              
                                              // 백엔드 응답에서 새로운 데이터를 받아서 세션스토리지 업데이트
                                              if (response.data) {
                                                // 새로운 스토리 데이터를 세션스토리지에 저장
                                                sessionStorage.setItem('storyData', JSON.stringify(response.data));
                                                
                                                // 현재 페이지 새로고침으로 새로운 데이터 로드
                                                window.location.reload();
                                              } else {
                                                // 다음 슬라이드로 이동 (기존 데이터 사용)
                                                nextSlide();
                                              }

                                            } catch (error) {
                                              console.error('답변 저장 오류:', error);
                                              alert('답변 저장에 실패했습니다. 다시 시도해주세요.');
                                            } finally {
                                              setIsSubmitting(false);
                                            }
                                          }
                                        }}
                                      >
                                        {isSubmitting ? '생성 중...' : '다음'}
                                      </button>
                                    )
                                  )}
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
                <span className="description-2-span">pel-world</span>
                <span className="description-2-span">®</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </>

  );
};

export default ImageCarousel;