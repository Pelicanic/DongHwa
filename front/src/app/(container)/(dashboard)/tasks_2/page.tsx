"use client";

import { apiClient, API_ROUTES } from '@/lib/api';
import { debugLog } from '@/lib/logger';
import React, { useState, useEffect, useCallback } from 'react';
import '@/styles/tasks_2.css';
import '@/styles/soundbar.css';
import Loading from '@/(components)/Loading/loading';
import { requireLogin } from '@/lib/utils/auth';
import { extractMoodFromQuestionText, setupBackgroundMusic } from '@/lib/utils/music';
import Swal from 'sweetalert2';
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
        
        const user_id = localStorage.getItem('user_id');
        if (!user_id) {
          await Swal.fire({
            title: '로그인 필요',
            text: '로그인이 필요합니다.',
            icon: 'warning',
            confirmButtonText: '확인'
          });
          window.location.href = '/user/login';
          return;
        }

        // 먼저 진행 중인 스토리가 있는지 확인
        try {
          const inProgressResponse = await apiClient.post(API_ROUTES.USER_IN_PROGRESS_STORY, {
            user_id: user_id
          });
          
          if (inProgressResponse.data.success && inProgressResponse.data.story) {
            // 진행 중인 스토리가 있으면 그 데이터를 사용
            const progressStory = inProgressResponse.data.story;
            setStoryData(progressStory);
            
            debugLog.story('진행 중인 스토리 로드', {
              'Story Data': progressStory
            });
            
            // 진행 중인 스토리를 sessionStorage에 저장
            sessionStorage.setItem('storyData', JSON.stringify(progressStory));
            
            const story_id = progressStory.story_id;
            
            const [qaResponse, paragraphResponse, illustrationResponse] = await Promise.all([
              apiClient.post(API_ROUTES.PARAGRAPH_QA, { story_id }),
              apiClient.post(API_ROUTES.STORY_PARAGRAPH, { story_id }),
              apiClient.post(API_ROUTES.ILLUSTRATION, { story_id })
            ]);
            
            debugLog.api('API 응답 데이터', {
              'QA Response': qaResponse.data.paragraphQA,
              'Paragraph Response': paragraphResponse.data.storyParagraph,
              'Illustration Response': illustrationResponse.data
            });
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

            // DB에서 기분 추출 및 배경음악 설정
            let extractedMood = '밝은';
            const qaData = qaResponse.data.paragraphQA;
            
            if (qaData && qaData.length > 0 && paragraphs && paragraphs.length > 0) {
              const firstParagraph = paragraphs.find(p => p.paragraph_no === 1);
              if (firstParagraph) {
                const firstParagraphQA = qaData.find(qa => qa.paragraph_id === firstParagraph.paragraph_id);
                if (firstParagraphQA && firstParagraphQA.question_text) {
                  extractedMood = extractMoodFromQuestionText(firstParagraphQA.question_text);
                  debugLog.story('DB에서 추출한 기분', {
                    'Extracted Mood': extractedMood
                  });
                }
              }
            }

            // 배경음악 설정
            const audio = setupBackgroundMusic(
              extractedMood,
              0.3,
              () => debugLog.audio('배경음악이 자동으로 재생되었습니다.'),
              (error) => debugLog.audio('자동 재생이 차단되었습니다. 사용자 상호작용 후 재생됩니다.', { 'Error': error })
            );
            
            if (audio) {
              setBgMusic(audio);
            }
          } else {
            // 가장 최신 동화가 in_progress가 아닌 경우
            const reason = inProgressResponse.data.reason;
            const latestStatus = inProgressResponse.data.latest_status;
            
            if (reason === 'no_stories') {
              // 아예 동화가 없는 경우
              await Swal.fire({
                title: '동화 없음',
                text: '새로운 동화를 시작해주세요.',
                icon: 'info',
                confirmButtonText: '확인'
              });
              window.location.href = '/';
            } else if (reason === 'latest_not_in_progress') {
              // 가장 최신 동화가 completed이거나 다른 상태인 경우
              if (latestStatus === 'completed') {
                await Swal.fire({
                  title: '동화 완성',
                  text: '최근 동화가 이미 완성되었습니다.',
                  icon: 'success',
                  confirmButtonText: '확인'
                });
              } else {
                await Swal.fire({
                  title: '진행 중인 동화 없음',
                  text: `최근 동화 상태: ${latestStatus}`,
                  icon: 'info',
                  confirmButtonText: '확인'
                });
              }
            }
            
            window.location.href = '/';
            return;
          }
        } catch (apiError) {
          console.error('진행 중인 스토리 조회 실패:', apiError);
          await Swal.fire({
            title: '오류 발생',
            text: '데이터를 불러오는 중 오류가 발생했습니다.',
            icon: 'error',
            confirmButtonText: '확인'
          });
          window.location.href = '/';
          return;
        }

      } catch (err) {
        debugLog.error("useStoryData error", err);
        await Swal.fire({
          title: '오류 발생',
          text: '데이터를 불러오는 중 오류가 발생했습니다.',
          icon: 'error',
          confirmButtonText: '확인'
        });
        window.location.href = '/';
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return { storyData, paragraphQA, storyParagraph, illustrations, loading, lastParagraphIndex, bgMusic };
};




const ImageCarousel: React.FC<ImageCarouselProps> = () => {
  // 로그인 확인
  useEffect(() => {
    requireLogin();
  }, []);

  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [volume, setVolume] = useState<number>(0.3); // 볼륨 상태 (0.0 ~ 1.0)
  const [isMuted, setIsMuted] = useState<boolean>(false); // 음소거 상태
  const [previousVolume, setPreviousVolume] = useState<number>(0.3); // 음소거 전 볼륨
  const [isControlsVisible, setIsControlsVisible] = useState<boolean>(true); // 사운드바 표시 상태
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false); // 모달 상태
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
      // 볼륨을 변경할 때 음악이 재생되지 않았다면 재생 시도
      if (bgMusic.paused && newVolume > 0) {
        bgMusic.play().catch(error => {
          debugLog.audio('볼륨 조절 시 음악 재생 실패', { 'Error': error });
        });
      }
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
        // 음소거 해제 시 음악이 재생되지 않았다면 재생 시도
        if (bgMusic.paused) {
          bgMusic.play().catch(error => {
            debugLog.audio('음소거 해제 시 음악 재생 실패', { 'Error': error });
          });
        }
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

  // 모달 열기 함수
  const openModal = useCallback(() => {
    setIsModalOpen(true);
  }, []);

  // 모달 닫기 함수
  const closeModal = useCallback(() => {
    setIsModalOpen(false);
  }, []);

  // 배경 클릭 핸들러 (사운드바와 carousel 영역 제외)
  const handleBackgroundClick = useCallback((e: React.MouseEvent) => {
    const target = e.target as HTMLElement;
    
    // carousel 클래스나 사운드바 영역을 클릭한 경우 모달 열지 않음
    if (
      target.closest('.carousel') || 
      target.closest('[data-volume-control]')
    ) {
      return;
    }
    
    // 그 외의 배경 영역을 클릭했을 때만 모달 열기
    openModal();
  }, [openModal]);

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
    // 선택지 클릭 로그 제거
    
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
    
    // 선택 완료 로그 제거
  }, []);

  // input 값 직접 변경 핸들러 (tasks_1과 동일)
  const handleInputChange = useCallback((slideIndex: number, value: string) => {
    // 입력 변경 로그 제거
    
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      
      if (value.trim() === '') {
        // 빈 값일 때는 해당 키를 아예 삭제
        delete newAnswers[slideIndex];
      } else {
        // 값이 있을 때만 저장
        newAnswers[slideIndex] = value;
      }
      
      // 상태 업데이트 로그 제거
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
    debugLog.story('배경 이미지 가져오기', {
      'Slide Index': slideIndex,
      'Illustration': illustration
    });
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
            backgroundPosition: 'center'
          }}
          onClick={handleBackgroundClick}
        >
          <div data-volume-control className="music-control-container">
            {/* 볼륨/음소거 아이콘 (클릭 가능) */}
            <button
              onClick={toggleMute}
              className="mute-button"
              title={isMuted ? '음소거 해제' : '음소거'}
            >
              <img 
                src={isMuted ? '/images/volume_off.png' : '/images/volume_on.png'}
                alt={isMuted ? '음소거' : '소리 켜짐'}
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
                    background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${volume * 100}%, #e5e7eb ${volume * 100}%, #e5e7eb 100%)`
                  }}
                  title={`볼륨: ${Math.round(volume * 100)}%`}
                />
                
                <span className="volume-percentage">
                  {Math.round(volume * 100)}%
                </span>
              </>
            )}
            
            {/* 사운드바 토글 버튼 */}
            <button
              onClick={toggleControls}
              className="toggle-button"
              title={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
            >
              <img 
                src={isControlsVisible ? '/images/left.png' : '/images/right.png'}
                alt={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
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
                  const data_QA_next = paragraphQA[index + 1];
                  const selectedChoice = userAnswers[index]; // userAnswers 사용
                  
                  // 선택지에서 [, ], , 문자 제거 후 처리
                  let choices = ['선택지1', '선택지2', '선택지3']; // 기본값
                  
                  if (data_QA?.answer_choice) {
                    // [, ], , 문자 제거
                    const cleanedText = data_QA.answer_choice.replace(/[\[\],']/g, '');
                  debugLog.story('선택지 처리 과정', {
                    'Original Text': data_QA.answer_choice,
                    'Cleaned Text': cleanedText
                  });
                    
                    // 숫자. 패턴으로 분리
                    const splitChoices = cleanedText.split(/[123]\./);
                    debugLog.story('선택지 분리 결과', {
                      'Split Choices': splitChoices
                    });
                    
                    // 빈 문자열 제거 및 트림
                    const filteredChoices = splitChoices.filter(choice => choice.trim() !== '').map(choice => choice.trim());
                    
                    if (filteredChoices.length > 0) {
                      choices = filteredChoices;
                    }
                  }
                  
                  debugLog.story('최종 선택지 결과', {
                    'Slide Index': index,
                    'Final Choices': choices
                  });
                  
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
                                              placeholder={data_QA_next?.question_text || ""}
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
                                              name={`userAnswer_${currentSlide}`}
                                              value={selectedChoice || ''}
                                              onChange={(e) => {
                                                handleInputChange(currentSlide, e.target.value);
                                              }}
                                              placeholder="이야기를 작성해 보아요!"
                                              className="answer-input"
                                              key={`input-${currentSlide}`}
                                              data-slide={currentSlide}
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
                                                debugLog.story('선택지 버튼 클릭', {
                                                  'Slide Index': index,
                                                  'Choice Index': choiceIndex,
                                                  'Choice Text': choice
                                                });
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
                                        // 현재 story_id를 sessionStorage에 저장
                                        const currentStoryData = sessionStorage.getItem('storyData');
                                        if (currentStoryData) {
                                          const parsedData = JSON.parse(currentStoryData);
                                          if (parsedData.story_id) {
                                            sessionStorage.setItem('selectedStoryId', parsedData.story_id);
                                            debugLog.story('tasks_3으로 story_id 전달', {
                                              'Story ID': parsedData.story_id
                                            });
                                          }
                                        }
                                        // tasks_3 페이지로 이동
                                        window.location.href = '/tasks_3';
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
                                            debugLog.story('다음 버튼 클릭 - 데이터 전송', {
                                              'Selected Choice': selectedChoice,
                                              'Selected Choice Index': selectedChoices[index],
                                              'Current Slide': index + 1,
                                              'User ID': localStorage.getItem('user_id'),
                                              'Story ID': JSON.parse(sessionStorage.getItem('storyData') || '{}').story_id
                                            });
                                            try {
                                              // 필수 데이터 검증
                                              const user_id = localStorage.getItem('user_id');
                                              const storyDataStr = sessionStorage.getItem('storyData');
                                              
                                              if (!user_id) {
                                                await Swal.fire({
                                                  title: '로그인 필요',
                                                  text: '로그인이 필요합니다.',
                                                  icon: 'warning',
                                                  confirmButtonText: '확인'
                                                });
                                                window.location.href = '/user/login';
                                                return;
                                              }
                                              
                                              if (!storyDataStr) {
                                                await Swal.fire({
                                                  title: '스토리 데이터 없음',
                                                  text: '스토리 데이터를 찾을 수 없습니다.',
                                                  icon: 'error',
                                                  confirmButtonText: '확인'
                                                });
                                                window.location.href = '/';
                                                return;
                                              }
                                              
                                              let storyData;
                                              try {
                                                storyData = JSON.parse(storyDataStr);
                                              } catch (parseError) {
                                                debugLog.error('스토리 데이터 파싱 오류', parseError);
                                                await Swal.fire({
                                                  title: '데이터 오류',
                                                  text: '스토리 데이터가 손상되었습니다.',
                                                  icon: 'error',
                                                  confirmButtonText: '확인'
                                                });
                                                window.location.href = '/';
                                                return;
                                              }
                                              
                                              if (!storyData.story_id) {
                                                await Swal.fire({
                                                  title: '스토리 ID 없음',
                                                  text: '스토리 ID를 찾을 수 없습니다.',
                                                  icon: 'error',
                                                  confirmButtonText: '확인'
                                                });
                                                window.location.href = '/';
                                                return;
                                              }
                                              
                                              // 백엔드에 데이터 전송
                                              const requestData = {
                                                user_input: selectedChoice,
                                                story_id: storyData.story_id,
                                                user_id: user_id
                                              };
                                              
                                              debugLog.api('API 요청 데이터', requestData);
                                              console.log('=== STORY_CREATE API 요청 ===');
                                              console.log('Request Data:', requestData);
                                              console.log('API URL:', API_ROUTES.STORY_CREATE);
                                              console.log('Base URL:', apiClient.defaults.baseURL);
                                              console.log('Full URL:', `${apiClient.defaults.baseURL}${API_ROUTES.STORY_CREATE}`);
                                              console.log('User Agent:', navigator.userAgent);
                                              console.log('Current Time:', new Date().toISOString());
                                              
                                              const response = await apiClient.post(API_ROUTES.STORY_CREATE, requestData);
                                              
                                              debugLog.api('답변 저장 성공', {
                                                'Selected Choice': selectedChoice,
                                                'Response Data': response.data
                                              });
                                              
                                              // 백엔드 응답 검증
                                              if (response.data && response.data.success !== false) {
                                                // 새로운 스토리 데이터를 세션스토리지에 저장
                                                sessionStorage.setItem('storyData', JSON.stringify(response.data));
                                                
                                                // 현재 페이지 새로고침으로 새로운 데이터 로드
                                                window.location.reload();
                                              } else {
                                                // 응답에 오류가 있는 경우
                                                const errorMessage = response.data?.message || '알 수 없는 오류가 발생했습니다.';
                                                await Swal.fire({
                                                  title: '저장 실패',
                                                  text: errorMessage,
                                                  icon: 'error',
                                                  confirmButtonText: '확인'
                                                });
                                              }
                                            } catch (error: any) {
                                              debugLog.error('답변 저장 오류', error, {
                                                'Selected Choice': selectedChoice,
                                                'Slide Index': index,
                                                'Error Status': error.response?.status,
                                                'Error Data': error.response?.data
                                              });
                                              
                                              let errorMessage = '답변 저장에 실패했습니다.';
                                              
                                              if (error.response) {
                                                // 서버에서 응답한 오류
                                                if (error.response.status === 401) {
                                                  errorMessage = '로그인이 만료되었습니다. 다시 로그인해주세요.';
                                                } else if (error.response.status === 403) {
                                                  errorMessage = '권한이 없습니다.';
                                                } else if (error.response.status === 404) {
                                                  errorMessage = 'API 경로를 찾을 수 없습니다.';
                                                } else if (error.response.status === 500) {
                                                  errorMessage = '서버 내부 오류가 발생했습니다.';
                                                } else if (error.response.data?.message) {
                                                  errorMessage = error.response.data.message;
                                                }
                                              } else if (error.request) {
                                                // 네트워크 오류
                                                errorMessage = '네트워크 연결을 확인해주세요.';
                                              } else {
                                                // 기타 오류
                                                errorMessage = error.message || '알 수 없는 오류가 발생했습니다.';
                                              }
                                              
                                              await Swal.fire({
                                                title: '저장 실패',
                                                text: errorMessage,
                                                icon: 'error',
                                                confirmButtonText: '확인'
                                              });
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
      
      {/* 모달 */}
      {isModalOpen && (
        <div 
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999,
            backdropFilter: 'blur(5px)',
            animation: 'fadeIn 0.3s ease-out'
          }}
          onClick={closeModal}
        >
          <div 
            style={{
              position: 'relative',
              maxWidth: '90vw',
              maxHeight: '90vh',
              width: '800px',
              height: '600px',
              borderRadius: '12px',
              overflow: 'hidden',
              boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
              animation: 'modalSlideIn 0.4s ease-out'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            
            {/* 배경 이미지 */}
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundImage: `url('${getBackgroundImage(currentSlide)}')`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat'
              }}
            />
          </div>
        </div>
      )}
    </>

  );
};

export default ImageCarousel;