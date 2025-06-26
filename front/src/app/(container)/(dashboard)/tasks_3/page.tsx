"use client";

import { apiClient, API_ROUTES } from '@/lib/api';
import { debugLog } from '@/lib/logger';
import React, { useRef, useState , useEffect, useCallback } from 'react';
import HTMLFlipBook from 'react-pageflip';
import '@/styles/book.css'; // CSS 스타일 파일
import '@/styles/soundbar.css'; // 사운드바 CSS 파일
import { illustrationDTO } from '@/lib/type/illustration';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';
import { storyDTO } from '@/lib/type/story';
import Image from "next/image";
import Loading from '@/(components)/Loading/loading';

interface FlipEvent {
  data: number;
}

const DynamicFlipBook: React.FC = () => {
  const flipBook = useRef<HTMLDivElement>(null);
  // autoPlayTimeout을 useRef로 추가
  const autoPlayTimeout = useRef<NodeJS.Timeout | null>(null);
  
  const [illustration, setIllustration] = useState<illustrationDTO[]>([]);
  const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);
  const [story, setStory] = useState<storyDTO | null>(null);
  const [loading, setLoading] = useState(true);
  
  // 사운드바 관련 state 추가
  const [bgVolume, setBgVolume] = useState<number>(0.3); // 배경음악 볼륨 상태 (0.0 ~ 1.0)
  const [ttsVolume, setTtsVolume] = useState<number>(0.5); // TTS 볼륨 상태 (0.0 ~ 1.0)
  const [isBgMuted, setIsBgMuted] = useState<boolean>(false); // 배경음악 음소거 상태
  const [isTtsMuted, setIsTtsMuted] = useState<boolean>(false); // TTS 음소거 상태
  const [previousBgVolume, setPreviousBgVolume] = useState<number>(0.3); // 배경음악 음소거 전 볼륨
  const [previousTtsVolume, setPreviousTtsVolume] = useState<number>(0.5); // TTS 음소거 전 볼륨
  const [isControlsVisible, setIsControlsVisible] = useState<boolean>(true); // 사운드바 표시 상태
  const [bgMusic, setBgMusic] = useState<HTMLAudioElement | null>(null);
  
  // TTS 관련 state 추가
  const [ttsAudio, setTtsAudio] = useState<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [storyId, setStoryId] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(0);

  // TTS 파일 존재 여부 확인 함수
  const hasTTSForCurrentPage = useCallback(() => {
    if (!storyParagraph.length || currentPage === 0 || currentPage >= (storyParagraph.length * 2) + 1) {
      return false;
    }
    
    const paragraphIndex = Math.floor((currentPage - 1) / 2);
    if (paragraphIndex < 0 || paragraphIndex >= storyParagraph.length) {
      return false;
    }
    
    const currentParagraph = storyParagraph[paragraphIndex];
    const ttsFileName = currentParagraph.tts;
    
    return ttsFileName && ttsFileName.trim() !== '' && ttsFileName !== 'null' && ttsFileName !== 'undefined';
  }, [storyParagraph, currentPage]);



  useEffect(() => {
    // API 호출하여 데이터 가져오기
    const fetchdata = async () => {
      try {
        // sessionStorage에서 story_id 가져오기 (클라이언트에서만 가능)
        const story_id = sessionStorage.getItem('selectedStoryId') || '2241';
        
        setStoryId(story_id); // TTS용 story_id 저장
        debugLog.story('Tasks_3에서 Story ID 받음', {
          'Story ID': story_id
        });
        
        // API 호출시 story_id 사용
        const [illustrationRes, storyParagraphRes, storyRes] = await Promise.all([
          apiClient.post(API_ROUTES.ILLUSTRATION, { story_id }),
          apiClient.post(API_ROUTES.STORY_PARAGRAPH, { story_id }),
          apiClient.post(API_ROUTES.STORY_BY_ID, { story_id }),
        ]);

        debugLog.api('Tasks_3 API 응답 데이터', {
          'Story Data': storyRes.data.story,
          'Illustration Data': illustrationRes.data.illustration,
          'Story Paragraph Data': storyParagraphRes.data.storyParagraph
        });
        
        setIllustration(illustrationRes.data.illustration);
        setStoryParagraph(storyParagraphRes.data.storyParagraph);
        setStory(storyRes.data.story); // 배열의 첫 번째 요소를 가져와서 단일 객체로 설정
        
        // DB에서 Mood 값 추출 - paragraph_no가 1인 ParagraphQA의 question_text에서 추출
        let extractedMood = '밝은'; // 기본값
        
        // ParagraphQA 데이터 가져오기
        const qaResponse = await apiClient.post(API_ROUTES.PARAGRAPH_QA, { story_id });
        const qaData = qaResponse.data.paragraphQA;
        const paragraphs = storyParagraphRes.data.storyParagraph;
        
        if (qaData && qaData.length > 0 && paragraphs && paragraphs.length > 0) {
          // paragraph_no가 1인 StoryParagraph 찾기
          const firstParagraph = paragraphs.find((p: storyParagraphDTO) => p.paragraph_no === 1);
          if (firstParagraph) {
            // 해당 paragraph_id를 가진 ParagraphQA 찾기
            const firstParagraphQA = qaData.find((qa: { paragraph_id?: number; question_text?: string }) => qa.paragraph_id === firstParagraph.paragraph_id);
            if (firstParagraphQA && firstParagraphQA.question_text) {
              const questionText = firstParagraphQA.question_text;
              // 기분 대체 로그 제거
              
              // 'Mood: ' 또는 '[Mood] : ' 뒤의 값을 추출
              // 기존 형식: "Mood: 슬픈" 또는 새 형식: "[Mood] : 따뜻한"
              const moodMatch = questionText.match(/(?:Mood:|\[Mood\]\s*:)\s*([^,]+)/i);
              if (moodMatch && moodMatch[1]) {
                extractedMood = moodMatch[1].trim();
                // 기분 추출 로그 제거
              }
            }
          }
        }
        
        // 배경음악 설정 - DB에서 추출한 기분에 따라
        const musicMapping: Record<string, string> = {
          "밝은": "fairy tale(Bright).mp3",
          "따뜻한": "fairy tale(Warm).mp3",
          "슬픈": "fairy tale(Sad).mp3",
          "신비로운": "fairy tale(Mythical).mp3",
          "무서운": "fairy tale(Scary).mp3"
        };

        // sessionStorage에서 storyData 가져오기 -> DB에서 추출한 기분 사용
        // const savedData = sessionStorage.getItem('storyData');
        // const parsedData = savedData ? JSON.parse(savedData) : {};
        // const selectedMood = parsedData.answers && parsedData.answers[2]; // 3번째 질문의 답변 (기분)
        const selectedMood: string = extractedMood; // DB에서 추출한 기분 사용
        
        // 기본값으로 '밝은' 기분의 음악 사용 (fairy tale(Bright).mp3)
        const musicFile: string = (selectedMood && musicMapping[selectedMood]) 
          ? musicMapping[selectedMood] 
          : musicMapping["밝은"]; // 기본값: fairy tale(Bright).mp3
        
        // 배경음악 설정 로그 제거
        
        // 항상 음악 재생 (기본값이라도)
        const audio = new Audio(`/bgsound/${musicFile}`);
        audio.loop = true;
        audio.volume = 0.3; // 배경음악 볼륨 30%로 설정
        
        // 오디오 객체를 먼저 설정
        setBgMusic(audio);
        
        // 자동 재생 시도
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              // 자동 재생 로그 제거
            })
            .catch(() => {
              // 자동 재생 차단 로그 제거
              // 자동재생이 차단된 경우를 위한 이벤트 리스너 추가
              const handleFirstUserInteraction = () => {
                audio.play().then(() => {
                  console.log('사용자 상호작용 후 배경음악이 재생되었습니다.');
                }).catch(err => {
                  console.log('사용자 상호작용 후에도 재생 실패:', err);
                });
                // 이벤트 리스너 제거 (한 번만 실행)
                document.removeEventListener('click', handleFirstUserInteraction);
                document.removeEventListener('keydown', handleFirstUserInteraction);
                document.removeEventListener('touchstart', handleFirstUserInteraction);
              };
              
              // 다양한 사용자 상호작용 이벤트 리스너 추가
              document.addEventListener('click', handleFirstUserInteraction, { once: true });
              document.addEventListener('keydown', handleFirstUserInteraction, { once: true });
              document.addEventListener('touchstart', handleFirstUserInteraction, { once: true });
            });
        }
        
      } catch (error) {
        debugLog.error('데이터를 가져오는 중 오류 발생', error, {
          'Function': 'fetchdata',
          'Story ID': storyId || 'N/A'
        });
      } finally {
        setLoading(false);
      }
    };
    fetchdata();
  }, [storyId]);


  // 배경음악 및 TTS 관리 - 컴포넌트 언마운트 시 정지
  useEffect(() => {
    return () => {
      if (bgMusic) {
        bgMusic.pause();
        bgMusic.currentTime = 0;
      }
      if (ttsAudio) {
        ttsAudio.pause();
        ttsAudio.currentTime = 0;
      }
      // autoPlayTimeout 정리
      if (autoPlayTimeout.current) {
        clearTimeout(autoPlayTimeout.current);
      }
    };
  }, [bgMusic, ttsAudio]);

  // 배경음악 볼륨 변경 함수
  const handleBgVolumeChange = useCallback((newVolume: number) => {
    setBgVolume(newVolume);
    if (bgMusic) {
      bgMusic.volume = newVolume;
      // 볼륨을 변경할 때 음악이 재생되지 않았다면 재생 시도
      if (bgMusic.paused && newVolume > 0) {
        bgMusic.play().catch(error => {
          console.log('볼륨 조절 시 음악 재생 실패:', error);
        });
      }
    }
    // 볼륨이 0보다 크면 음소거 해제
    if (newVolume > 0 && isBgMuted) {
      setIsBgMuted(false);
    }
    // 볼륨이 0이면 음소거 상태로
    if (newVolume === 0) {
      setIsBgMuted(true);
    }
  }, [bgMusic, isBgMuted]);

  // TTS 볼륨 변경 함수
  const handleTtsVolumeChange = useCallback((newVolume: number) => {
    setTtsVolume(newVolume);
    if (ttsAudio) {
      ttsAudio.volume = newVolume;
    }
    // 볼륨이 0보다 크면 음소거 해제
    if (newVolume > 0 && isTtsMuted) {
      setIsTtsMuted(false);
    }
    // 볼륨이 0이면 음소거 상태로
    if (newVolume === 0) {
      setIsTtsMuted(true);
    }
  }, [ttsAudio, isTtsMuted]);

  // 배경음악 음소거 토글 함수
  const toggleBgMute = useCallback(() => {
    if (bgMusic) {
      if (isBgMuted) {
        // 음소거 해제: 이전 볼륨으로 복원
        const restoreVolume = previousBgVolume > 0 ? previousBgVolume : 0.3;
        setBgVolume(restoreVolume);
        bgMusic.volume = restoreVolume;
        setIsBgMuted(false);
        // 음소거 해제 시 음악이 재생되지 않았다면 재생 시도
        if (bgMusic.paused) {
          bgMusic.play().catch(error => {
            console.log('음소거 해제 시 음악 재생 실패:', error);
          });
        }
      } else {
        // 음소거: 현재 볼륨 저장 후 0으로 설정
        setPreviousBgVolume(bgVolume);
        setBgVolume(0);
        bgMusic.volume = 0;
        setIsBgMuted(true);
      }
    }
  }, [bgMusic, isBgMuted, bgVolume, previousBgVolume]);

  // TTS 음소거 토글 함수
  const toggleTtsMute = useCallback(() => {
    if (ttsAudio) {
      if (isTtsMuted) {
        // 음소거 해제: 이전 볼륨으로 복원
        const restoreVolume = previousTtsVolume > 0 ? previousTtsVolume : 0.5;
        setTtsVolume(restoreVolume);
        ttsAudio.volume = restoreVolume;
        setIsTtsMuted(false);
      } else {
        // 음소거: 현재 볼륨 저장 후 0으로 설정
        setPreviousTtsVolume(ttsVolume);
        setTtsVolume(0);
        ttsAudio.volume = 0;
        setIsTtsMuted(true);
      }
    }
  }, [ttsAudio, isTtsMuted, ttsVolume, previousTtsVolume]);

  // 사운드바 토글 함수
  const toggleControls = useCallback(() => {
    setIsControlsVisible(prev => !prev);
  }, []);

  // TTS 재생 함수
  const playTTS = useCallback(() => {
    if (!storyId || !storyParagraph.length) {
      console.log('story_id 또는 단락 데이터가 없습니다.');
      return;
    }

    // 표지(0)나 마지막 페이지에서는 TTS 재생 안함
    if (currentPage === 0 || currentPage >= (storyParagraph.length * 2) + 1) {
      console.log('표지 또는 뒤표지에서는 TTS를 재생할 수 없습니다.');
      return;
    }

    // 현재 페이지에 해당하는 단락 찾기
    // currentPage가 1,2는 첫번째 단락, 3,4는 두번째 단락...
    const paragraphIndex = Math.floor((currentPage - 1) / 2);
    
    if (paragraphIndex < 0 || paragraphIndex >= storyParagraph.length) {
      console.log('유효하지 않은 단락 인덱스:', paragraphIndex);
      return;
    }

    const currentParagraph = storyParagraph[paragraphIndex];
    const ttsFileName = currentParagraph.tts;
    
    console.log('Current paragraph:', currentParagraph);
    console.log('TTS filename:', ttsFileName);
    
    // TTS 파일이 없으면 재생하지 않음
    if (!ttsFileName || ttsFileName.trim() === '' || ttsFileName === 'null' || ttsFileName === 'undefined') {
      console.log('해당 단락에 TTS 파일이 없습니다.');
      return;
    }
    
    console.log('Full TTS path:', `/tts/${storyId}/${ttsFileName}`);

    // 기존 TTS 오디오 정지
    if (ttsAudio) {
      ttsAudio.pause();
      ttsAudio.currentTime = 0;
    }

    // 새 TTS 오디오 생성 및 재생
    const audio = new Audio(`/tts/${storyId}/${ttsFileName}`);
    audio.volume = ttsVolume; // TTS 볼륨으로 설정
    
    audio.onplay = () => setIsPlaying(true);
    audio.onended = () => setIsPlaying(false);
    audio.onerror = () => {
      console.error('TTS 파일 재생 오류:', `/tts/${storyId}/${ttsFileName}`);
      setIsPlaying(false);
    };

    setTtsAudio(audio);
    audio.play().catch(error => {
      console.error('TTS 재생 실패:', error);
      setIsPlaying(false);
    });
  }, [storyId, storyParagraph, ttsAudio, ttsVolume, currentPage]);

  // TTS 일시정지/재개 함수
  const pauseTTS = useCallback(() => {
    if (ttsAudio) {
      if (isPlaying) {
        ttsAudio.pause();
        setIsPlaying(false);
      } else {
        ttsAudio.play().catch(error => {
          console.error('TTS 재개 실패:', error);
          setIsPlaying(false);
        });
      }
    }
  }, [ttsAudio, isPlaying]);

  // TTS 완전 정지 함수 (페이지 변경 시에만 사용)
  const stopTTS = useCallback(() => {
    if (ttsAudio) {
      ttsAudio.pause();
      ttsAudio.currentTime = 0;
      setIsPlaying(false);
    }
  }, [ttsAudio]);

  // 특정 페이지에 대한 TTS 재생 함수
  const playTTSForPage = useCallback((pageNumber: number) => {
    if (!storyId || !storyParagraph.length) {
      return;
    }

    // 표지나 마지막 페이지에서는 TTS 재생 안함
    if (pageNumber === 0 || pageNumber >= (storyParagraph.length * 2) + 1) {
      return;
    }

    const paragraphIndex = Math.floor((pageNumber - 1) / 2);
    
    if (paragraphIndex < 0 || paragraphIndex >= storyParagraph.length) {
      return;
    }

    const currentParagraph = storyParagraph[paragraphIndex];
    const ttsFileName = currentParagraph.tts;
    
    // TTS 파일이 없으면 재생하지 않음
    if (!ttsFileName || ttsFileName.trim() === '' || ttsFileName === 'null' || ttsFileName === 'undefined') {
      return;
    }

    // 기존 TTS 오디오 정지
    if (ttsAudio) {
      ttsAudio.pause();
      ttsAudio.currentTime = 0;
    }

    // 새 TTS 오디오 생성 및 재생
    const audio = new Audio(`/tts/${storyId}/${ttsFileName}`);
    audio.volume = ttsVolume;
    
    audio.onplay = () => setIsPlaying(true);
    audio.onended = () => setIsPlaying(false);
    audio.onerror = () => {
      console.error('TTS 파일 재생 오류:', `/tts/${storyId}/${ttsFileName}`);
      setIsPlaying(false);
    };

    setTtsAudio(audio);
    audio.play().catch(error => {
      console.error('TTS 재생 실패:', error);
      setIsPlaying(false);
    });
  }, [storyId, storyParagraph, ttsAudio, ttsVolume]);

  // 볼륨 동기화
  useEffect(() => {
    if (bgMusic) {
      bgMusic.volume = bgVolume;
    }
  }, [bgMusic, bgVolume]);

  useEffect(() => {
    if (ttsAudio) {
      ttsAudio.volume = ttsVolume;
    }
  }, [ttsAudio, ttsVolume]);

  // 페이지 변경 이벤트 핸들러
  const onFlip = (e: FlipEvent) => {
    setCurrentPage(e.data);
    
    if (ttsAudio && isPlaying) {
      stopTTS();
    }
    if (autoPlayTimeout.current) {
      clearTimeout(autoPlayTimeout.current);
      autoPlayTimeout.current = null;
    }
    
    const newPage = e.data;
    // TTS 볼륨이 0이면 자동 재생하지 않음
    if (ttsVolume === 0) {
      return;
    }
    
    if (newPage > 0 && newPage < (storyParagraph.length * 2) + 1) {
      const paragraphIndex = Math.floor((newPage - 1) / 2);
      if (paragraphIndex >= 0 && paragraphIndex < storyParagraph.length) {
        const currentParagraph = storyParagraph[paragraphIndex];
        const ttsFileName = currentParagraph?.tts;
        
        if (ttsFileName && ttsFileName.trim() !== '' && ttsFileName !== 'null' && ttsFileName !== 'undefined') {
          autoPlayTimeout.current = setTimeout(() => {
            playTTSForPage(newPage);
          }, 1500);
        }
      }
    }
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
          {/* 사운드바 */}
          <div data-volume-control className="music-control-container">
            {/* TTS 재생/일시정지 버튼 */}
            <button
              onClick={hasTTSForCurrentPage() ? (ttsAudio && (isPlaying || ttsAudio.currentTime > 0) ? pauseTTS : playTTS) : undefined}
              className="tts-button"
              title={
                !hasTTSForCurrentPage()
                  ? 'TTS 파일 없음' 
                  : ttsAudio && ttsAudio.currentTime > 0 
                    ? (isPlaying ? 'TTS 일시정지' : 'TTS 재개')
                    : 'TTS 재생'
              }
              disabled={!hasTTSForCurrentPage()}
              style={{
                marginRight: '10px',
                padding: '8px 12px',
                backgroundColor: 
                  !hasTTSForCurrentPage()
                    ? '#6b7280' 
                    : isPlaying 
                      ? '#f59e0b' 
                      : '#3b82f6',
                border: 'none',
                borderRadius: '5px',
                cursor: !hasTTSForCurrentPage() ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: '14px',
                fontWeight: 'bold',
                minWidth: '80px',
                opacity: !hasTTSForCurrentPage() ? 0.5 : 1
              }}
            >
              {!hasTTSForCurrentPage()
                ? '🚫 TTS없음'
                : ttsAudio && ttsAudio.currentTime > 0 
                  ? (isPlaying ? '⏸️ 일시정지' : '▶️ 재개')
                  : '▶️ 재생'
              }
            </button>
            
            {/* 배경음악 컨트롤 */}
            <div style={{ display: 'flex', alignItems: 'center', marginRight: '15px' }}>
              <span style={{ 
                fontSize: '12px', 
                fontWeight: 'bold', 
                color: '#374151', 
                marginRight: '8px',
                minWidth: '50px'
              }}>배경음악</span>
              
              <button
                onClick={toggleBgMute}
                className="mute-button"
                title={isBgMuted ? '배경음악 음소거 해제' : '배경음악 음소거'}
                style={{ marginRight: '8px' }}
              >
                <Image 
                  src={isBgMuted ? '/images/volume_off.png' : '/images/volume_on.png'}
                  alt={isBgMuted ? '음소거' : '소리 켜짐'}
                  width={20}
                  height={20}
                />
              </button>
              
              {isControlsVisible && (
                <>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={bgVolume}
                    onChange={(e) => handleBgVolumeChange(parseFloat(e.target.value))}
                    className="volume-slider"
                    style={{
                      background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${bgVolume * 100}%, #e5e7eb ${bgVolume * 100}%, #e5e7eb 100%)`,
                      width: '80px',
                      marginRight: '8px'
                    }}
                    title={`배경음악 볼륨: ${Math.round(bgVolume * 100)}%`}
                  />
                  
                  <span className="volume-percentage" style={{ fontSize: '12px', minWidth: '35px' }}>
                    {Math.round(bgVolume * 100)}%
                  </span>
                </>
              )}
            </div>
            
            {/* TTS 컨트롤 */}
            <div style={{ display: 'flex', alignItems: 'center', marginRight: '15px' }}>
              <span style={{ 
                fontSize: '12px', 
                fontWeight: 'bold', 
                color: '#374151', 
                marginRight: '8px',
                minWidth: '30px'
              }}>TTS</span>
              
              <button
                onClick={toggleTtsMute}
                className="mute-button"
                title={isTtsMuted ? 'TTS 음소거 해제' : 'TTS 음소거'}
                style={{ marginRight: '8px' }}
              >
                <Image 
                  src={isTtsMuted ? '/images/volume_off.png' : '/images/volume_on.png'}
                  alt={isTtsMuted ? '음소거' : '소리 켜짐'}
                  width={20}
                  height={20}
                />
              </button>
              
              {isControlsVisible && (
                <>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={ttsVolume}
                    onChange={(e) => handleTtsVolumeChange(parseFloat(e.target.value))}
                    className="volume-slider"
                    style={{
                      background: `linear-gradient(to right, #10b981 0%, #10b981 ${ttsVolume * 100}%, #e5e7eb ${ttsVolume * 100}%, #e5e7eb 100%)`,
                      width: '80px',
                      marginRight: '8px'
                    }}
                    title={`TTS 볼륨: ${Math.round(ttsVolume * 100)}%`}
                  />
                  
                  <span className="volume-percentage" style={{ fontSize: '12px', minWidth: '35px' }}>
                    {Math.round(ttsVolume * 100)}%
                  </span>
                </>
              )}
            </div>
            
            {/* 사운드바 토글 버튼 */}
            <button
              onClick={toggleControls}
              className="toggle-button"
              title={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
            >
              <Image 
                src={isControlsVisible ? '/images/left.png' : '/images/right.png'}
                alt={isControlsVisible ? '사운드바 숨기기' : '사운드바 보이기'}
                width={24}
                height={24}
              />
            </button>
          </div>
          
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
              clickEventForward={true}
              usePortrait={true}
              startPage={0}
              drawShadow={true}
              flippingTime={800}
              showPageCorners={true}
              disableFlipByClick={false}
              startZIndex={0}
              swipeDistance={30}
              style={{ margin: '0 auto' }}
              onFlip={onFlip}
              className="flipbook"
            >
              {/* 표지 */}
              <div className="bg-[#faf6ed] flex items-center justify-center text-white p-8">
                <div className="text-center" style={{
                  height: '100%',
                  padding: '100px 30px',
                  fontFamily: 'Ownglyph_ryurue-Rg',
                  color: 'black',
                }}>
                  <h2 className="text-4xl font-bold mb-4">{story?.title || '제목 없음'}</h2>
                  <p className="text-lg">이야기 속으로 들어가보아요!</p>
                </div>
              </div>

              {storyParagraph && storyParagraph.flatMap((storypage, index) => {
                const illust = illustration[index];
                return [
                  <div key={`image-${index}`} className="pageflip-page right-page" style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.3)'
                  }}>
                    <div className="page-content">
                      {illust ? (
                        <Image
                          src={illust.image_url ? `/images/${illust.image_url}` : '/images/soyee-secret.png'}
                          className="w-full h-full object-cover"
                          alt=""
                          width={384}
                          height={320}
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
                      backgroundColor: '#faf6ed',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between'
                    }}>
                      <div className="page-content" style={{
                        color: '#1a1a1a',
                        fontSize: '1.65rem',
                        fontWeight: '700',
                        lineHeight: '1.65',
                        letterSpacing: '0.3rem',
                        padding: '27px 54px',
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
                  color: 'black',
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