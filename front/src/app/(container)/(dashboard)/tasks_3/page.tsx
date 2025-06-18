'use client';

import axios from 'axios';
import React,{ useEffect, useState } from 'react';
import '@/styles/tasks_3.css';
import PageFlip from '@/(components)/Book/PageFlip';
import { illustrationDTO } from '@/lib/type/illustration';
import { storyParagraphDTO } from '@/lib/type/storyParagraph';



const illustrationResponse = async (): Promise<illustrationDTO[]> => {
  const story_id = '2073';
  const res = await axios.post('http://localhost:8721/api/v1/illustration/story/', { story_id });
  return res.data.illustration;
};

const storyParagraphResponse = async (): Promise<storyParagraphDTO[]> => {
  const story_id = '2073';
  const res = await axios.post('http://localhost:8721/api/v1/storyParagraph/story/', { story_id });
  return res.data.storyParagraph;
};


const TasksPage = () => {
  // 양쪽 페이지로 보기 위한 동화책 데이터
  const [illustration, setIllustration] = useState<illustrationDTO[]>([]);
  const [storyParagraph, setStoryParagraph] = useState<storyParagraphDTO[]>([]);

  useEffect(() => {
    
    // API 호출하여 데이터 가져오기
    const fetchdata = async () => {
      const illustration = await illustrationResponse();
      const storyParagraph = await storyParagraphResponse();
      setIllustration(illustration);
      setStoryParagraph(storyParagraph);
    };
    fetchdata();
  }, []);


  return (
    <div className='container'>
      <div className='container_box'>
        <div className='container_box_main'>
          <PageFlip
            illustration={illustration}
            storyParagraph={storyParagraph}
            width={320}           // 한 페이지 너비 조정
            height={450}          // 페이지 높이 조정
            size="stretch"
            drawShadow={true}
            flippingTime={1000}
            usePortrait={false}   // 양쪽 보기에서는 landscape 모드 // true: 한페이지 false : 두페이지
            autoSize={false}
            // mobileScrollSupport={true}
            // swipeDistance={50}
            // useMouseEvents={true}
            // clickEventForward={true}
            maxShadowOpacity={0.4}
            showCover={true}
          />
        </div>
      </div>
      
      {/* 종료 버튼 (필요시 활성화) */}
      {/* <div className='container_box_btn_fixed'>
        <button className="exit-btn">
          책 닫기
        </button>
      </div> */}
    </div>
  );
};

export default TasksPage;