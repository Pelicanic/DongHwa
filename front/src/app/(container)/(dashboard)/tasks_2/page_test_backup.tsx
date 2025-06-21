"use client";

import axios from 'axios';
import React, { useState, useEffect, useCallback } from 'react';
import '@/styles/tasks_2.css';
import Loading from '@/(components)/Loading/loading';

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
        
        // 🚨 강제 디버깅 - 이 코드가 실행되면 알럿이 나타납니다
        alert('🚨 새로운 디버깅 코드가 실행되었습니다!');
        console.log("🔥 illustrationResponse:", illustrationResponse);
        console.log("🔥 illustrationResponse.data:", illustrationResponse.data);
        
        setParagraphQA(qaResponse.data.paragraphQA);
        setStoryParagraph(paragraphResponse.data.storyParagraph);
        
        // illustrationResponse.data를 직접 사용
        if (illustrationResponse.data && Array.isArray(illustrationResponse.data)) {
          setIllustrations(illustrationResponse.data);
          console.log("✅ illustrations 설정 성공:", illustrationResponse.data);
          alert(`✅ illustrations 설정 성공! 개수: ${illustrationResponse.data.length}`);
        } else {
          setIllustrations([]);
          console.log("❌ illustrations 비어있음");
          alert('❌ illustrations 데이터가 비어있습니다!');
        }
        
        // 마지막 paragraph_no 찾기
        const paragraphs = paragraphResponse.data.storyParagraph;
        if (paragraphs.length > 0) {
          const maxParagraphNo = Math.max(...paragraphs.map(p => p.paragraph_no));
          const lastIndex = paragraphs.findIndex(p => p.paragraph_no === maxParagraphNo);
          setLastParagraphIndex(lastIndex >= 0 ? lastIndex : paragraphs.length - 1);
        }

      } catch (err) {
        console.error(err);
        alert('❌ 데이터 로드 오류: ' + err.message);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  return { storyData, paragraphQA, storyParagraph, illustrations, loading, lastParagraphIndex };
};

const ImageCarousel: React.FC<ImageCarouselProps> = () => {
  const [currentSlide, setCurrentSlide] = useState<number>(0);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const { paragraphQA, storyParagraph, illustrations, loading, lastParagraphIndex } = useStoryData();

  // 마지막 paragraph 인덱스로 초기 슬라이드 설정
  useEffect(() => {
    if (!loading && storyParagraph.length > 0) {
      setCurrentSlide(lastParagraphIndex);
    }
  }, [loading, lastParagraphIndex, storyParagraph.length]);

  // 각 슬라이드별 사용자 답변을 저장하는 state
  const [userAnswers, setUserAnswers] = useState<{[key: number]: string}>({});
  // 현재 선택된 선택지를 저장하는 state
  const [selectedChoices, setSelectedChoices] = useState<{[key: number]: number | null}>({});
  
  const totalSlides = storyParagraph.length;

  // 배경 이미지 URL 가져오기 함수
  const getBackgroundImage = (slideIndex: number) => {
    console.log(`🔍 === Slide ${slideIndex + 1} 배경 이미지 검색 ===`);
    console.log('illustrations 배열 길이:', illustrations.length);
    console.log('illustrations 전체 내용:', illustrations);
    
    if (illustrations.length === 0) {
      console.log('⚠️ illustrations 배열이 비어있습니다!');
      alert('⚠️ illustrations 배열이 비어있습니다!');
      return '/images/signup-bg1.jpg';
    }
    
    // storyParagraph 배열에서 현재 슬라이드의 paragraph_id 가져오기
    const currentParagraph = storyParagraph[slideIndex];
    const paragraphId = currentParagraph?.paragraph_id;
    
    console.log('찾고 있는 paragraphId:', paragraphId, '(타입:', typeof paragraphId, ')');
    
    // illustrations 배열에서 해당 paragraph_id와 일치하는 이미지 찾기
    const illustration = illustrations.find(ill => {
      console.log('비교:', ill.paragraph_id, '(타입:', typeof ill.paragraph_id, ') vs', paragraphId);
      const illId = parseInt(ill.paragraph_id?.toString() || '0');
      const currId = parseInt(paragraphId?.toString() || '0');
      console.log('숫자 변환 후:', illId, 'vs', currId);
      return illId === currId;
    });
    
    console.log('찾은 illustration:', illustration);
    
    const imageUrl = illustration?.image_url || '/images/signup-bg1.jpg';
    console.log('최종 imageUrl:', imageUrl);
    console.log('==========================================');
    
    return imageUrl;
  };

  // 선택지 클릭 핸들러
  const handleChoiceClick = useCallback((slideIndex: number, choiceIndex: number, choiceText: string) => {
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      if (choiceText.trim() === '') {
        delete newAnswers[slideIndex];
      } else {
        newAnswers[slideIndex] = choiceText;
      }
      return newAnswers;
    });
    
    setSelectedChoices(prev => ({
      ...prev,
      [slideIndex]: choiceIndex
    }));
  }, []);

  // input 값 변경 핸들러
  const handleInputChange = useCallback((slideIndex: number, value: string) => {
    setUserAnswers(prev => {
      const newAnswers = { ...prev };
      if (value.trim() === '') {
        delete newAnswers[slideIndex];
      } else {
        newAnswers[slideIndex] = value;
      }
      return newAnswers;
    });
    
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
          <div className="content">
            <div className="intro-section">
              {/* 공백 */}
            </div>
            
            <div className="carousel">
              <div className="slides-box">
                <div className="slide active">
                  <div className="slide-content">
                    <div className='container_box'> 
                      <div className='container_box_left'>
                        <div className='container_box_left_inner'>
                          <div className='container_box_left_inner_text'>
                            테스트 페이지입니다. 배경 이미지가 적용되었는지 확인하세요.
                            <br/>
                            개발자 도구 콘솔을 확인해보세요.
                          </div>
                        </div>
                      </div>
                      <div className='container_box_right'>
                        <div className='container_box_right_inner'>
                          <div className='container_box_right_inner_box'>
                            <div className='container_box_right_inner_box_ai'>
                              테스트 메시지: Illustrations 데이터가 로드되었는지 확인 중...
                            </div>
                            <div className='container_box_right_inner_box_user'>
                              <p>Illustrations 개수: {illustrations.length}</p>
                              <p>현재 슬라이드: {currentSlide + 1}</p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ImageCarousel;