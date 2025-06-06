'use client';

import { useEffect, useState } from 'react';
import '@/styles/globals.css';
import LinkButton from '@/(components)/Button/button';
import BackgroundSlideshow from '@/(components)/background/BackgroundSlideshow';
import AuroraBackground from '@/(components)/background/AuroraBackground';

const Main: React.FC = () => {
  const [nickname, setNickname] = useState('우리');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedNickname = localStorage.getItem('nickname');
      if (storedNickname) setNickname(storedNickname);
    }
  }, []);

  return (
    <div className="relative min-h-screen">
      {/* 🌄 배경 이미지 */}
      <AuroraBackground />
      <BackgroundSlideshow />

      {/* ✅ 콘텐츠 */}
      <div className="relative z-10 flex min-h-screen bg-white/70 backdrop-blur-sm">
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
                  href="/tasks"
                  className="bg-blue-500 hover:bg-blue-600 text-white px-4 sm:px-6 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors"
                />
                <LinkButton
                  text="동화 이어 만들기"
                  href="/"
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
              {/* Card 1 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow">
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <img
                    src="/images/tom-adventure.png"
                    alt="용감한 톰의 비밀섬 대모험"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="mb-2">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">신나는 모험 🚀</span>
                </div>
                <h3 className="font-bold text-sm lg:text-base mb-1 line-clamp-2">용감한 톰의 비밀섬 대모험</h3>
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">무서움을 이겨낸 톰이 친구들과 함께 신비한 섬을 탐험하며 마법의 열쇠를 찾아 떠나요!</p>
                <div className="flex items-center text-xs text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2"></div>
                  <span className="truncate">무명 작가</span>
                  <span className="ml-auto">Silver Tier</span>
                </div>
              </div>

              {/* Card 2 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow">
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <img
                    src="/images/dino-robot.png"
                    alt="디노, 착한 로봇이 되다"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="mb-2">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">로봇, 공룡 🦕</span>
                </div>
                <h3 className="font-bold text-sm lg:text-base mb-1 line-clamp-2">디노, 착한 로봇이 되다</h3>
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">변신하는 공룡 로봇 디노! 친구를 구하기 위해 진짜 착한 로봇이 되어가는 성장 이야기.</p>
                <div className="flex items-center text-xs text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2"></div>
                  <span className="truncate">사무르스 작가</span>
                  <span className="ml-auto">Gold Tier</span>
                </div>
              </div>

              {/* Card 3 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow">
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <img
                    src="/images/forest-party.png"
                    alt="숲 속 친구들의 생일 파티"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="mb-2">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">자연 🌿</span>
                </div>
                <h3 className="font-bold text-sm lg:text-base mb-1 line-clamp-2">숲 속 친구들의 생일 파티</h3>
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">숲 속 동물 친구들이 힘을 모아 여우의 생일 파티를 준비해요! 자연과 우정이 가득한 이야기.</p>
                <div className="flex items-center text-xs text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2"></div>
                  <span className="truncate">우숩 작가</span>
                  <span className="ml-auto">Platinum Tier</span>
                </div>
              </div>

              {/* Card 4 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow">
                <div className="w-full h-80 rounded-lg mb-4 overflow-hidden">
                  <img
                    src="/images/soyee-secret.png"
                    alt="소이와 친구들의 비밀 놀이"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="mb-2">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">우리들의 이야기 👫</span>
                </div>
                <h3 className="font-bold text-sm lg:text-base mb-1 line-clamp-2">소이와 친구들의 비밀 놀이</h3>
                <p className="text-xs text-gray-600 mb-3 line-clamp-2">소이와 유치원 친구들이 놀이터에서 발견한 비밀 상자! 일상 속 특별한 하루를 담은 이야기.</p>
                <div className="flex items-center text-xs text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2"></div>
                  <span className="truncate">직각 선구들</span>
                  <span className="ml-auto">Challenger Tier</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Main;
