// 작성자 : 최재우
// 마지막 수정일 : 2025-06-10
// 마지막 수정 내용 : 
// 화면 크기에 따른 반응형 디자인 수정
// {/* 추천 카드 리스트 */} 의 div에 클래스 추가 / lg:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4
// DB 연동 완료

'use client';

import { useEffect, useState } from 'react';
import { apiClient, API_ROUTES } from '@/lib/api';
import LinkButton from '@/(components)/Button/button';
import MainCard from '@/(components)/Card/Cardbox';
import { storyDTO } from '@/lib/type/story';
import Loading from '@/(components)/Loading/loading';

const storyResponse = async (): Promise<storyDTO[]> => {
  const user_id = 772;
  const res = await apiClient.post(API_ROUTES.STORY_MAIN, { user_id });
  return res.data.stories;
};

const Main: React.FC = () => {
  const [nickname, setNickname] = useState('우리');
  const [posts, setPosts] = useState<storyDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStories = async () => {
      try {
        const storedNickname = localStorage.getItem('nickname');
        if (storedNickname) setNickname(storedNickname);
        const boards = await storyResponse();
        setPosts(boards);
      } catch (error) {
        console.error("데이터를 가져오는 중 오류 발생:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStories();
  }, []);

  return (
    <>
      {loading ? (
        <Loading/>
      ) : (

        // 배경 필터와 대비 강화 적용, 블러 제거, 투명도 낮춤
        <div
          className="relative min-h-screen bg-cover bg-center bg-no-repeat filter contrast-100"
          style={{ backgroundImage: "url('/images/main-bg7.jpg')" }}
        >
          {/* ✅ 콘텐츠 */}
          <div className="relative z-10 flex min-h-screen bg-white/20">
            <div className="flex-1 pt-16">
              <div className="p-4 sm:p-6 lg:p-8">
                {/* Header */}
                <div className="mb-8 lg:mb-12">
                  <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
                    여러분만의 동화 속으로<br />
                    들어갈 준비가 되었나요?
                  </h1>
                  <p className="text-sm sm:text-base text-gray-600 mb-6 leading-relaxed">
                    Pel-World에서 상어와 물고기 친구들과 함께 신나는 모험을 떠나보세요!<br className="hidden sm:block" />
                    나만의 이야기가 시작되는 마법 같은 세계가 펼쳐집니다!
                  </p>
                  <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
                    <LinkButton
                      text="동화 만들어 보기"
                      href="/tasks_1"
                      className="bg-blue-500 hover:bg-blue-600 text-white px-4 sm:px-6 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors"
                    />
                    <LinkButton
                      text="동화 이어 만들기"
                      href="/tasks_2"
                      className="border border-blue-500 text-blue-500 hover:bg-blue-50 px-4 sm:px-6 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors"
                    />
                 
                  </div>

                </div>

                {/* 🌟 추천 동화 제목 복구 */}
                <div className="mb-6 lg:mb-8">
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
                    {nickname} 어린이를 위한 추천 동화
                  </h2>
                </div>
                {/* 추천 카드 리스트 */}
                <div className='mainCard_box'>
                  <MainCard posts={posts} />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default Main;
