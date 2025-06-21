"use client";

import axios from 'axios';
import React, { useState, useEffect, useCallback } from 'react';
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
  const [illustrations, setIllustrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastParagraphIndex, setLastParagraphIndex] = useState(0);
  const [bgMusic, setBgMusic] = useState<HTMLAudioElement | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        if (typeof window === 'undefined') return;
        
        const savedData = sessionStorage.getItem('storyData');
        const parsedData = JSON.parse(savedData || '{}');
        setStoryData(parsedData);

        console.log("parsedData:", parsedData);

        const story_id = parsedData.story_id;
        
        const [qaResponse, paragraphResponse, illustrationResponse] = await Promise.all([
          axios.post('http://localhost:8721/api/v1/paragraphQA/story/', { story_id }),
          axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id }),
          axios.post('http://localhost:8721/api/v1/illustration/story/', { story_id })
        ]);
        
        console.log("qaResponse:", qaResponse.data.paragraphQA);
        console.log("paragraphResponse:", paragraphResponse.data.storyParagraph);
        console.log("illustrationResponse:", illustrationResponse.data);
        setParagraphQA(qaResponse.data.paragraphQA);
        setStoryParagraph(paragraphResponse.data.storyParagraph);
        setIllustrations(illustrationResponse.data.illustration);
        
        // 마지막 paragraph_no 찾기
        const paragraphs = paragraphResponse.data.storyParagraph;
        if (paragraphs.length > 0) {
          const maxParagraphNo = Math.max(...paragraphs.map(p => p.paragraph_no));
          const lastIndex = paragraphs.findIndex(p => p.paragraph_no === maxParagraphNo);
          setLastParagraphIndex(lastIndex >= 0 ? lastIndex : paragraphs.length - 1);
        }

        // 배경음악 설정 - tasks_1에서 선택한 기분에 따라
        const musicMapping = {
          "밝은": "fairy tale(Bright).mp3",
          "따뜻한": "fairy tale(Warm).mp3",
          "슬픈": "fairy tale(Sad).mp3",
          "신비로운": "fairy tale(Mythical).mp3",
          "무서운": "fairy tale(Scary).mp3"
        };

        // tasks_1에서 저장된 storyData에서 선택한 기분 가져오기
        const selectedMood = parsedData.answers && parsedData.answers[2]; // 3번째 질문의 답변 (기분)
        
        // 기본값으로 '밝은' 기분의 음악 사용 (fairy tale(Bright).mp3)
        const musicFile = (selectedMood && musicMapping[selectedMood]) 
          ? musicMapping[selectedMood] 
          : musicMapping["밝은"]; // 기본값: fairy tale(Bright).mp3
        
        console.log('Selected mood:', selectedMood);
        console.log('Music file to play:', musicFile);
        
        // 항상 음악 재생 (기본값이라도)
        const audio = new Audio(`/bgsound/${musicFile}`);
        audio.loop = true;
        audio.volume = 0.3; // 볼륨 30%로 설정
        
        // 자동 재생 시도
        audio.play().catch(error => {
          console.log('자동 재생이 차단되었습니다. 사용자 상호작용 후 재생됩니다:', error);
        });
        
        setBgMusic(audio);

      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return { storyData, paragraphQA, storyParagraph, illustrations, loading, lastParagraphIndex, bgMusic };
};




const ImageCarousel: React.FC<ImageCarouselProps> = () => {
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [volume, setVolume] = useState<number>(0.3); // 볼륨 상태 (0.0 ~ 1.0)
  const [isMuted, setIsMuted] = useState<boolean>(false); // 음소거 상태
  const [previousVolume, setPreviousVolume] = useState<number>(0.3); // 음소거 전 볼륨
  const [isControlsVisible, setIsControlsVisible] = useState<boolean>(true); // 사운드바 표시 상태
  const { paragraphQA, storyParagraph, illustrations, loading, lastParagraphIndex, bgMusic } = useStoryData();

  // 마지막 paragraph 인덱스로 초기 슬라이드 설정
  useEffect(() => {
    if (!loading && storyParagraph.length > 0) {
      setCurrentSlide(lastParagraphIndex);
    }
  }, [loading, lastParagraphIndex, storyParagraph.length]);

  // 배경음악 관리 - 컴포넌트 언마운트 시 정지
  useEffect(() => {
    return () => {
      if (bgMusic) {
        bgMusic.pause();
        bgMusic.currentTime = 0;
      }
    };
  }, [bgMusic]);

  // 볼륨 변경 함수
  const handleVolumeChange = useCallback((newVolume: number) => {
    setVolume(newVolume);
    if (bgMusic) {
      bgMusic.volume = newVolume;
    }
    // 볼륨이 0보다 크면 음소거 해제
    if (newVolume > 0 && isMuted) {
      setIsMuted(false);
    }
    // 볼륨이 0이면 음소거 상태로
    if (newVolume === 0) {
      setIsMuted(true);
    }
  }, [bgMusic, isMuted]);

  // 음소거 토글 함수
  const toggleMute = useCallback(() => {
    if (bgMusic) {
      if (isMuted) {
        // 음소거 해제: 이전 볼륨으로 복원
        const restoreVolume = previousVolume > 0 ? previousVolume : 0.3;
        setVolume(restoreVolume);
        bgMusic.volume = restoreVolume;
        setIsMuted(false);
      } else {
        // 음소거: 현재 볼륨 저장 후 0으로 설정
        setPreviousVolume(volume);
        setVolume(0);
        bgMusic.volume = 0;
        setIsMuted(true);
      }
    }
  }, [bgMusic, isMuted, volume, previousVolume]);

  // 사운드바 토글 함수
  const toggleControls = useCallback(() => {
    setIsControlsVisible(prev => !prev);
  }, []);

  // bgMusic이 변경될 때 볼륨 동기화
  useEffect(() => {
    if (bgMusic) {
      bgMusic.volume = volume;
    }
  }, [bgMusic, volume]);



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

  // 배경 이미지 URL 가져오기 함수
  const getBackgroundImage = (slideIndex: number) => {
    // 가장 간단한 방법: 인덱스 순서로 매칭
    const illustration = illustrations[slideIndex];
    console.log(`Getting background image for slide ${slideIndex}:`, illustration);
    // 이미지가 있으면 해당 URL 사용, 없으면 기본 이미지 사용
    const imageUrl = illustration?.image_url === 'test.png' ? '/images/signup-bg1.jpg' : `/images/${illustration?.image_url}`;

    return imageUrl;
  };

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
        <div 
          className="preview min-h-screen bg-no-repeat"
          style={{
            backgroundImage: `url('${getBackgroundImage(currentSlide)}')`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          <div style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '8px', // 12px → 8px
            backgroundColor: 'rgba(255, 255, 255, 0.3)',
            backdropFilter: 'blur(10px)',
            padding: '8px 12px', // 12px 16px → 8px 12px
            borderRadius: '10px', // 12px → 10px
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            transition: 'all 0.3s ease'
          }}>
            {/* 볼륨/음소거 아이콘 (클릭 가능) */}
            <button
              onClick={toggleMute}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '6px',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.1)';
                e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
              title={isMuted ? '음소거 해제' : '음소거'}
            >
              <img 
                src={isMuted ? '/images/volume_off.png' : '/images/volume_on.png'}
                alt={isMuted ? '음소거' : '소리 켜짐'}
                style={{
                  width: '20px', // 24px → 20px
                  height: '20px' // 24px → 20px
                }}
              />
            </button>
            
            {/* 볼륨 슬라이더 및 퍼센트 (토글 가능) */}
            {isControlsVisible && (
              <>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                  className="volume-slider"
                  style={{
                    background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${volume * 100}%, #e5e7eb ${volume * 100}%, #e5e7eb 100%)`,
                    width: '60px', // 80px → 60px 로 줄임
                    height: '3px' // 높이도 줄임
                  }}
                  title={`볼륨: ${Math.round(volume * 100)}%`}
                />
                
                <span style={{
                  fontSize: '11px', // 12px → 11px
                  color: '#1f2937', // 진한 회색으로 변경
                  minWidth: '28px', // 32px → 28px
                  textAlign: 'center',
                  fontWeight: '600' // 폰트 두께 추가
                }}>
                  {Math.round(volume * 100)}%
                </span>
              </>
            )}
            
            {/* 사운드바 토글 버튼 */}
            <button
              onClick={toggleControls}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '4px',
                borderRadius: '6px',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.1)';
                e.currentTarget.style.backgroundColor = 'rgba(59, 130, 246, 0.2)';
                // 이미지 색상을 흰색으로 변경
                const img = e.currentTarget.querySelector('img');
                if (img) {
                  img.style.filter = 'brightness(0) saturate(100%) invert(100%)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.backgroundColor = 'transparent';
                // 이미지 색상을 기본 진한 회색으로 복원
                const img = e.currentTarget.querySelector('img');
                if (img) {
                  img.style.filter = 'brightness(0) saturate(100%) invert(15%) sepia(6%) saturate(1042%) hue-rotate(194deg) brightness(94%) contrast(91%)';
                }
              }}
              title={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
            >
              <img 
                src={isControlsVisible ? '/images/left.png' : '/images/right.png'}
                alt={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
                style={{
                  width: '14px',
                  height: '14px',
                  filter: 'brightness(0) saturate(100%) invert(15%) sepia(6%) saturate(1042%) hue-rotate(194deg) brightness(94%) contrast(91%)', // 진한 회색 필터
                  transition: 'filter 0.2s ease'
                }}
              />
            </button>
          </div>
          <div className="content">
            <div className="intro-section">
              {/* 공백 */}
            </div>
            
            <div className="carousel">
              <div className="slides-box">
                {storyParagraph.map((data, index) => {
                  const data_QA = paragraphQA[index];
                  const selectedChoice = userAnswers[index]; // userAnswers 사용
                  
                  // 선택지에서 [, ], , 문자 제거 후 처리
                  let choices = ['선택지1', '선택지2', '선택지3']; // 기본값
                  
                  if (data_QA?.answer_choice) {
                    // [, ], , 문자 제거
                    const cleanedText = data_QA.answer_choice.replace(/[\[\],']/g, '');
                    console.log(`Original text:`, data_QA.answer_choice);
                    console.log(`Cleaned text:`, cleanedText);
                    
                    // 숫자. 패턴으로 분리
                    const splitChoices = cleanedText.split(/[123]\./);
                    console.log(`Split choices:`, splitChoices);
                    
                    // 빈 문자열 제거 및 트림
                    const filteredChoices = splitChoices.filter(choice => choice.trim() !== '').map(choice => choice.trim());
                    
                    if (filteredChoices.length > 0) {
                      choices = filteredChoices;
                    }
                  }
                  
                  console.log(`Final choices for slide ${index}:`, choices);
                  
                  return (
                    <div
                      key={index}
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
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px', width: '100%' }}>
                                    <span style={{ fontSize: '14px', fontWeight: '600', minWidth: 'fit-content' }}>
                                      진행상황
                                    </span>
                                    <div style={{ 
                                      flex: 1, 
                                      height: '8px', 
                                      backgroundColor: '#e5e7eb', 
                                      borderRadius: '4px',
                                      overflow: 'hidden'
                                    }}>
                                      <div style={{
                                        height: '100%',
                                        backgroundColor: '#3b82f6',
                                        width: `${((index + 1) / 10) * 100}%`,
                                        borderRadius: '4px',
                                        transition: 'width 0.3s ease'
                                      }}></div>
                                    </div>
                                    <span style={{ 
                                      fontSize: '14px', 
                                      fontWeight: '600', 
                                      color: '#3b82f6',
                                      minWidth: 'fit-content'
                                    }}>
                                      {index + 1}/10
                                    </span>
                                  </div>
                                </div>
                                <div className='container_box_right_inner_box_ai'>
                                  {data_QA?.ai_question || 'AI 질문이 없습니다'}
                                </div>
                                
                                <div className='container_box_right_inner_box_user'>
                                  {index !== 9 && ( // 9번째 인덱스가 아니면 표시
                                    <div className={`user-interaction-grid ${
                                      currentSlide !== lastParagraphIndex ? 'input-only' : ''
                                    }`}>
                                      {/* 텍스트 작성 영역 */}
                                      <div className={`text-input-area ${
                                        currentSlide !== lastParagraphIndex ? 'expanded' : ''
                                      }`}>
                                        <div className='selected-text-display'>
                                          {currentSlide !== lastParagraphIndex ? (
                                            <textarea 
                                              name={`userAnswer_${index}`}
                                              value={selectedChoice || ''}
                                              onChange={(e) => {
                                                if (currentSlide === lastParagraphIndex) {
                                                  handleInputChange(index, e.target.value);
                                                }
                                              }}
                                              placeholder={data_QA?.answer_text || ""}
                                              className={`answer-input expanded`}
                                              key={`textarea-${index}`}
                                              data-slide={index}
                                              disabled={true}
                                              rows={3}
                                              style={{
                                                backgroundColor: '#f3f4f6',
                                                cursor: 'not-allowed',
                                                resize: 'none'
                                              }}
                                            />
                                          ) : (
                                            <input 
                                              type="text" 
                                              name={`userAnswer_${index}`}
                                              value={selectedChoice || ''}
                                              onChange={(e) => {
                                                handleInputChange(index, e.target.value);
                                              }}
                                              placeholder="이야기를 작성해 보아요!"
                                              className="answer-input"
                                              key={`input-${index}`}
                                              data-slide={index}
                                              style={{
                                                backgroundColor: '#ffffff',
                                                cursor: 'text'
                                              }}
                                            />
                                          )}
                                        </div>
                                      </div>

                                      {/* 선택지 버튼들 */}
                                      <div className={`choice-buttons-grid ${
                                        currentSlide !== lastParagraphIndex ? 'hidden' : ''
                                      }`} style={{
                                        display: currentSlide === lastParagraphIndex ? 'flex' : 'none'
                                      }}>
                                        {choices.map((choice, choiceIndex) => (
                                          <button
                                            key={choiceIndex}
                                            className={`choice-btn ${
                                              selectedChoices[index] === choiceIndex ? 'choice-selected' : ''
                                            }`}
                                            onClick={(e) => {
                                              e.preventDefault();
                                              e.stopPropagation();
                                              // 마지막 슬라이드에서만 클릭 가능
                                              if (index === lastParagraphIndex) {
                                                console.log(`Button clicked: Slide ${index}, Choice ${choiceIndex}`);
                                                handleChoiceClick(index, choiceIndex, choice);
                                              }
                                            }}
                                            role="button"
                                            tabIndex={index === lastParagraphIndex ? 0 : -1}
                                            aria-label={`선택지 ${choiceIndex + 1}: ${choice}`}
                                            onKeyDown={(e) => {
                                              if (e.key === 'Enter' || e.key === ' ') {
                                                e.preventDefault();
                                                if (index === lastParagraphIndex) {
                                                  handleChoiceClick(index, choiceIndex, choice);
                                                }
                                              }
                                            }}
                                            disabled={index !== lastParagraphIndex} // 마지막 슬라이드가 아니면 비활성화
                                            style={{
                                              pointerEvents: index === lastParagraphIndex ? 'auto' : 'none',
                                              zIndex: 10,
                                              position: 'relative',
                                              opacity: index !== lastParagraphIndex ? 0.5 : 1,
                                              cursor: index !== lastParagraphIndex ? 'not-allowed' : 'pointer'
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
                                  )}
                                  
                                  {/* 9번째 인덱스일 때 완료 메시지 표시 */}
                                  {index === 9 && (
                                    <div style={{
                                      display: 'flex',
                                      alignItems: 'center',
                                      justifyContent: 'center',
                                      height: '100%',
                                      fontSize: '24px',
                                      fontWeight: '700',
                                      color: '#1a1a1a',
                                      textAlign: 'center'
                                    }}>
                                      이야기가 완성되었습니다!
                                    </div>
                                  )}
                                </div>
                                
                                
                                
                                {/* <div className='container_box_right_inner_box_temp'>
                                  <div className='container_box_right_inner_box_temp_btn'>임시저장</div>
                                </div> */}
                                <div className='next-button-area'>
                                  {index === 9 ? (
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