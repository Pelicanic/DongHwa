"use client";

import axios from 'axios';
import React, { useRef, useState , useEffect, useCallback } from 'react';
import HTMLFlipBook from 'react-pageflip';
import '@/styles/book.css'; // CSS 스타일 파일
import '@/styles/soundbar.css'; // 사운드바 CSS 파일
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
  
  // 사운드바 관련 state 추가
  const [volume, setVolume] = useState<number>(0.3); // 볼륨 상태 (0.0 ~ 1.0)
  const [isMuted, setIsMuted] = useState<boolean>(false); // 음소거 상태
  const [previousVolume, setPreviousVolume] = useState<number>(0.3); // 음소거 전 볼륨
  const [isControlsVisible, setIsControlsVisible] = useState<boolean>(true); // 사운드바 표시 상태
  const [bgMusic, setBgMusic] = useState<HTMLAudioElement | null>(null);

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
        
        // DB에서 Mood 값 추출 - paragraph_no가 1인 ParagraphQA의 question_text에서 추출
        let extractedMood = '밝은'; // 기본값
        
        // ParagraphQA 데이터 가져오기
        const qaResponse = await axios.post('http://localhost:8721/api/v1/paragraphQA/story/', { story_id });
        const qaData = qaResponse.data.paragraphQA;
        const paragraphs = storyParagraphRes.data.storyParagraph;
        
        if (qaData && qaData.length > 0 && paragraphs && paragraphs.length > 0) {
          // paragraph_no가 1인 StoryParagraph 찾기
          const firstParagraph = paragraphs.find(p => p.paragraph_no === 1);
          if (firstParagraph) {
            // 해당 paragraph_id를 가진 ParagraphQA 찾기
            const firstParagraphQA = qaData.find(qa => qa.paragraph_id === firstParagraph.paragraph_id);
            if (firstParagraphQA && firstParagraphQA.question_text) {
              const questionText = firstParagraphQA.question_text;
              console.log('Original question_text:', questionText);
              
              // 'Mood: ' 또는 '[Mood] : ' 뒤의 값을 추출
              // 기존 형식: "Mood: 슬픈" 또는 새 형식: "[Mood] : 따뜻한"
              const moodMatch = questionText.match(/(?:Mood:|\[Mood\]\s*:)\s*([^,]+)/i);
              if (moodMatch && moodMatch[1]) {
                extractedMood = moodMatch[1].trim();
                console.log('Extracted mood from DB:', extractedMood);
              }
            }
          }
        }
        
        // 배경음악 설정 - DB에서 추출한 기분에 따라
        const musicMapping = {
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
        const selectedMood = extractedMood; // DB에서 추출한 기분 사용
        
        // 기본값으로 '밝은' 기분의 음악 사용 (fairy tale(Bright).mp3)
        const musicFile = (selectedMood && musicMapping[selectedMood]) 
          ? musicMapping[selectedMood] 
          : musicMapping["밝은"]; // 기본값: fairy tale(Bright).mp3
        
        console.log('Selected mood from DB:', selectedMood);
        console.log('Music file to play:', musicFile);
        
        // 항상 음악 재생 (기본값이라도)
        const audio = new Audio(`/bgsound/${musicFile}`);
        audio.loop = true;
        audio.volume = 0.3; // 볼륨 30%로 설정
        
        // 오디오 객체를 먼저 설정
        setBgMusic(audio);
        
        // 자동 재생 시도
        const playPromise = audio.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              console.log('배경음악이 자동으로 재생되었습니다.');
            })
            .catch(error => {
              console.log('자동 재생이 차단되었습니다. 사용자 상호작용 후 재생됩니다:', error);
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
        console.error("데이터를 가져오는 중 오류 발생:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchdata();
  }, []);
  

  const [currentPage, setCurrentPage] = useState(0);

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
          console.log('볼륨 조절 시 음악 재생 실패:', error);
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
            console.log('음소거 해제 시 음악 재생 실패:', error);
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

  // bgMusic이 변경될 때 볼륨 동기화
  useEffect(() => {
    if (bgMusic) {
      bgMusic.volume = volume;
    }
  }, [bgMusic, volume]);

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
          {/* 사운드바 */}
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
                  lineHeight: '1.65',
                  letterSpacing: '0.3rem', /* 글자 간격 추가 */
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