'use client';

import { useEffect, useState } from 'react';
import { apiClient, API_ROUTES } from '@/lib/api';
import MainCard from '@/(components)/Card/Cardbox';
import { storyDTO } from '@/lib/type/story';
import Loading from '@/(components)/Loading/loading';
import { requireLogin } from '@/lib/utils/auth';

const getMyCompletedStories = async (): Promise<storyDTO[]> => {
  try {
    // 세션에서 user_id 가져오기 (실제 세션 관리 방식에 따라 수정 필요)
    const user_id = sessionStorage.getItem('user_id') || localStorage.getItem('user_id'); 
    
    console.log('로그인된 user_id:', user_id);
    
    // 기존 API 호출 - 사용자의 모든 동화 조회
    const res = await apiClient.post(API_ROUTES.STORY_MAIN, { 
      user_id: user_id
    });
    
    console.log('사용자의 모든 동화 데이터:', res.data);
    
    // 프론트엔드에서 status가 'completed'인 동화만 필터링
    const allStories = res.data.stories || [];
    const completedStories = allStories.filter((story: storyDTO) => 
      story.status === 'completed'
    );
    
    console.log('완성된 동화만 필터링:', completedStories);
    
    return completedStories;
  } catch (error) {
    console.error("나의 동화를 가져오는 중 오류 발생:", error);
    throw error;
  }
};

const MyBook: React.FC = () => {
  const [nickname, setNickname] = useState('');
  const [myStories, setMyStories] = useState<storyDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 로그인 확인
  useEffect(() => {
    requireLogin();
  }, []);

  useEffect(() => {
    const fetchMyStories = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 닉네임 가져오기
        const storedNickname = localStorage.getItem('nickname') || sessionStorage.getItem('nickname') || '사용자';
        setNickname(storedNickname);
        
        // 나의 완성된 동화 불러오기
        const stories = await getMyCompletedStories();
        setMyStories(stories);
        
        console.log('불러온 나의 동화 수:', stories.length);
        
      } catch (error) {
        console.error("데이터를 가져오는 중 오류 발생:", error);
        setError('동화를 불러오는 중 오류가 발생했습니다.');
      } finally {
        setLoading(false);
      }
    };

    fetchMyStories();
  }, []);

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button 
            onClick={() => window.location.reload()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="relative min-h-screen bg-cover bg-center bg-no-repeat filter contrast-100"
      style={{ backgroundImage: "url('/images/bgsample1.jpg')" }}
    >
      {/* 콘텐츠 */}
      <div className="relative z-10 flex min-h-screen bg-white/20">
        <div className="flex-1 pt-16">
          <div className="p-4 sm:p-6 lg:p-8">
            {/* Header */}
            <div className="mb-8 lg:mb-12">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
                {nickname}님의 동화책
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mb-6 leading-relaxed">
                지금까지 완성하신 동화들을 모아보았습니다.<br className="hidden sm:block" />
                소중한 추억이 담긴 나만의 동화책을 다시 읽어보세요!
              </p>
              
              {/* 통계 정보 */}
              <div className="bg-white/60 rounded-lg p-4 mb-6 inline-block">
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{myStories.length}</p>
                    <p className="text-sm text-gray-600">완성된 동화</p>
                  </div>
                </div>
              </div>
            </div>

            {/* 내 동화 리스트 */}
            <div className="mb-6 lg:mb-8">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">
                나의 완성된 동화
              </h2>
              
              {myStories.length === 0 ? (
                <div className="text-center py-12">
                  <div className="bg-white/60 rounded-lg p-8 inline-block">
                    <p className="text-gray-600 mb-4">아직 완성된 동화가 없습니다.</p>
                    <p className="text-sm text-gray-500 mb-6">첫 번째 동화를 만들어보세요!</p>
                    <a 
                      href="/tasks_1" 
                      className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-block"
                    >
                      동화 만들기
                    </a>
                  </div>
                </div>
              ) : (
                <div className='mainCard_box'>
                  <MainCard posts={myStories} />
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyBook;