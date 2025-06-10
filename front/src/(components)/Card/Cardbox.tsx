// 작성자 : 최재우
// 마지막 수정일 : 2025-06-10
// DB 연동 완료

import React from 'react'
import Image from 'next/image';

interface ApiStoryResponse {
  story_id: string | number;
  title: string;
  summary: string;
  author_name: string;
  cover_img?: string;
}

interface MainCardProps {
  posts: ApiStoryResponse[];
}

const MainCard: React.FC<MainCardProps> = ({ posts }) => {
  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4 gap-4 lg:gap-6">
        {
          posts.map(
            (post, idx) => (
              <div
                key={post.story_id ?? idx}
                className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow"
              >
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <Image
                    src={post.cover_img ? `/images/${post.cover_img}` : '/images/bg3.jpg'}
                    alt={post.title}
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