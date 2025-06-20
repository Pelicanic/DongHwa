// 작성자 : 최재우
// 마지막 수정일 : 2025-06-10
// DB 연동 완료

import React from 'react'
import Image from 'next/image';
import {StoryDTO} from '@/lib/type/story';
import axios from 'axios';

interface MainCardProps {
  posts: StoryDTO[];
}

const MainCard: React.FC<MainCardProps> = ({ posts }) => {
  
  // 카드 클릭 핸들러
  const handleCardClick = async (storyId: number) => {
    try {
      console.log(`카드 클릭: story_id = ${storyId}`);
      
      // 백엔드에 story_id 전송 (예시 API - 실제 API 엔드포인트로 변경 필요)
      const response = await axios.post('http://localhost:8721/api/v1/story/select/', {
        story_id: storyId,
        user_id: localStorage.getItem('user_id') || '774' // 사용자 ID
      });
      
      console.log('백엔드 응답:', response.data);
      
      // 성공적으로 전송되면 tasks_3로 이동
      if (response.status === 200) {
        // story 데이터를 sessionStorage에 저장 (필요한 경우)
        sessionStorage.setItem('selectedStoryId', storyId.toString());
        
        // tasks_3로 이동
        window.location.href = '/tasks_3';
      }
      
    } catch (error) {
      console.error('카드 클릭 오류:', error);
      alert('동화를 불러오는 중 오류가 발생했습니다.');
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 lg:gap-6">
        {
          posts.map(
            (post, idx) => (
              <div
                key={post.story_id ?? idx}
                className="main_card bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => post.story_id && handleCardClick(post.story_id)}
              >
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <Image
                    src={post.cover_img ? `/images/${post.cover_img}` : '/images/bg3.jpg'}
                    alt={post.title ? post.title : "제목 없음"}
                    width={400} // 실제 이미지 비율에 맞게 조정
                    height={320}
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="font-bold text-sm lg:text-base mb-1 line-clamp-2">{post.title || "제목 없음"}</h3>
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">{post.summary || "내용이 없습니다."}</p>
                <div className="flex items-center text-xs text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2"></div>
                  <span className="truncate">{post.author_name || "익명"}</span>
                </div>
              </div>
            )
          )
        }
      </div>
    </>
  );
};

export default MainCard;