
import '@/styles/globals.css';
import {X } from 'lucide-react';
import LinkButton from '@/(components)/Button/button';

const Main: React.FC = () => {

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 lg:ml-0 pt-16 lg:pt-0">
        <div className="p-4 sm:p-6 lg:p-8">
          {/* Header */}
          <div className="mb-8 lg:mb-12">
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
              여러분만의 동화 속으로<br />
              들어간 준비가 되었나요?
            </h1>
            <p className="text-sm sm:text-base text-gray-600 mb-6 leading-relaxed">
              Pel-World에서 상어 움직이는 물고, 스토리, 심화를 경험해 보세요!<br className="hidden sm:block" />
              상상했던 모든 것이 현실이 되는 즐거움을 느껴보세요!
            </p>
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
              <LinkButton 
                text='동화 만들어 보기'
                href="/tasks"
                className="bg-blue-500 hover:bg-blue-600 text-white px-4 sm:px-6 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors"
               />
              <LinkButton 
                text='동화 이어 만들기'
                href="/"
                className="border border-blue-500 text-blue-500 hover:bg-blue-50 px-4 sm:px-6 py-3 rounded-lg font-medium text-sm sm:text-base transition-colors"
              />
            </div>
          </div>

          {/* Category Section */}
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 lg:mb-8">당신만을 위한 추천 동화</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6">
              {/* Category Card 1 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 lg:p-6 hover:shadow-md transition-shadow">
                <div className="w-full h-24 sm:h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                  <X className="w-8 sm:w-12 h-8 sm:h-12 text-gray-400" />
                </div>
                <div className="mb-3">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">신나는 모험 🚀</span>
                </div>
                <h3 className="font-bold text-base lg:text-lg mb-2 line-clamp-2">용감한 톰이 도로로 모험을키 떠나요!</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-4 line-clamp-2 lg:line-clamp-3">
                  주인공이 새로운 곳을 탐험하거나, 어려운 문제를 해결하며 떠나는 이야기!
                </p>
                <div className="flex items-center text-xs sm:text-sm text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2 flex-shrink-0"></div>
                  <span className="truncate">무명 작가</span>
                  <span className="ml-auto flex-shrink-0">Silver Tier</span>
                </div>
              </div>

              {/* Category Card 2 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 lg:p-6 hover:shadow-md transition-shadow">
                <div className="w-full h-24 sm:h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                  <X className="w-8 sm:w-12 h-8 sm:h-12 text-gray-400" />
                </div>
                <div className="mb-3">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">로봇, 공룡 🦕</span>
                </div>
                <h3 className="font-bold text-base lg:text-lg mb-2 line-clamp-2">좋은 로봇이 된 공룡과 그가 되는</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-4 line-clamp-2 lg:line-clamp-3">
                  "멋진 로봇들이 변신하고, 거대한 공돌들이 살아 움직이는 신나는 이야기!"
                </p>
                <div className="flex items-center text-xs sm:text-sm text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2 flex-shrink-0"></div>
                  <span className="truncate">사무르스 작가</span>
                  <span className="ml-auto flex-shrink-0">Gold Tier</span>
                </div>
              </div>

              {/* Category Card 3 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 lg:p-6 hover:shadow-md transition-shadow">
                <div className="w-full h-24 sm:h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                  <X className="w-8 sm:w-12 h-8 sm:h-12 text-gray-400" />
                </div>
                <div className="mb-3">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">자연 🌿</span>
                </div>
                <h3 className="font-bold text-base lg:text-lg mb-2 line-clamp-2">숲 속 친구들과 함께하는 생명 파티</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-4 line-clamp-2 lg:line-clamp-3">
                  "정동하고 게임하는 일들이 게석 없어서 줄즐이 뭐! 타치는 이야기."
                </p>
                <div className="flex items-center text-xs sm:text-sm text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2 flex-shrink-0"></div>
                  <span className="truncate">우숩 작가</span>
                  <span className="ml-auto flex-shrink-0">Platinum Tier</span>
                </div>
              </div>

              {/* Category Card 4 */}
              <div className="bg-white rounded-lg shadow-sm border p-4 lg:p-6 hover:shadow-md transition-shadow">
                <div className="w-full h-24 sm:h-32 bg-gray-200 rounded-lg mb-4 flex items-center justify-center">
                  <X className="w-8 sm:w-12 h-8 sm:h-12 text-gray-400" />
                </div>
                <div className="mb-3">
                  <span className="text-xs sm:text-sm font-medium text-gray-900">Category</span>
                  <span className="ml-2 text-xs sm:text-sm text-gray-500">우리들의 이야기 👫</span>
                </div>
                <h3 className="font-bold text-base lg:text-lg mb-2 line-clamp-2">라현모 소이와 잎들의 놀 랄 역솨</h3>
                <p className="text-xs sm:text-sm text-gray-600 mb-4 line-clamp-2 lg:line-clamp-3">
                  "우리 가족, 네 친구, 유치원이나 학교에서 일어나는 일들을 담은 이야기."
                </p>
                <div className="flex items-center text-xs sm:text-sm text-gray-500">
                  <div className="w-4 h-4 bg-gray-300 rounded-full mr-2 flex-shrink-0"></div>
                  <span className="truncate">직각 선구들</span>
                  <span className="ml-auto flex-shrink-0">Challenger Tier</span>
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