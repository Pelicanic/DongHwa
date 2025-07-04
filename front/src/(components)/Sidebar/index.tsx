// 작성자 : 최재우
// 마지막 수정일 : 2025-06-18
// 마지막 수정 내용 : refresh 토큰을 한 번 사용하여 폐기 후 완전 로그아웃 처리
'use client';

import React, { useEffect, useState } from 'react';
import { Search, PlusCircle, Play, BookOpen, Library, Palette, X, Menu, LogOut, User, ArrowRight } from 'lucide-react';
import LinkButton from '@/(components)/Button/button';
import SidebarLink from '@/(components)/Button/sidebarlinkButton';
import Link from 'next/link';
import Image from 'next/image';
import { logout } from '@/lib/utils/logout';

interface SidebarProps {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
  isDesktopSidebarOpen?: boolean;
  toggleDesktopSidebar?: () => void;
}

const Sidebar = ({ isSidebarOpen, toggleSidebar, isDesktopSidebarOpen = true, toggleDesktopSidebar }: SidebarProps) => {
  // 초기 로그인 상태를 로컬스토리지에서 바로 읽어오기
  const getInitialLoginState = () => {
    if (typeof window === 'undefined') return false;
    const access = localStorage.getItem('access');
    const user_id = localStorage.getItem('user_id');
    return !!(access && user_id);
  };

  const [isLoggedIn, setIsLoggedIn] = useState(getInitialLoginState);
  const [isLoading, setIsLoading] = useState(true); // 로딩 상태 추가
  const [showContent, setShowContent] = useState(isDesktopSidebarOpen);

  // 사이드바 상태 변경 감지 및 애니메이션 제어
  useEffect(() => {
    if (isDesktopSidebarOpen) {
      // 사이드바가 열릴 때: 300ms 후 콘텐츠 표시
      const timer = setTimeout(() => {
        setShowContent(true);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      // 사이드바가 닫힐 때: 즉시 콘텐츠 숨김
      setShowContent(false);
    }
  }, [isDesktopSidebarOpen]);

  const checkLoginStatus = async () => {
    const access = localStorage.getItem('access');
    const user_id = localStorage.getItem('user_id');

    // 토큰과 사용자 ID가 있으면 로그인된 것으로 간주
    if (access && user_id) {
      setIsLoggedIn(true);
    } else {
      setIsLoggedIn(false);
    }
    
    // 초기 로딩 완료
    setIsLoading(false);
  };

  useEffect(() => {
    checkLoginStatus();

    // 로그인/로그아웃 이벤트 리스너
    const handleLoginEvent = () => {
      console.log('Login event detected');
      checkLoginStatus();
    };
    
    const handleLogoutEvent = () => {
      console.log('Logout event detected');
      setIsLoggedIn(false);
    };

    // localStorage 변경 감지
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access' || e.key === 'user_id') {
        console.log('Storage change detected:', e.key, e.newValue);
        checkLoginStatus();
      }
    };

    window.addEventListener("login", handleLoginEvent);
    window.addEventListener("logout", handleLogoutEvent);
    window.addEventListener("storage", handleStorageChange);

    // 주기적으로 로그인 상태 확인 (선택사항)
    const interval = setInterval(() => {
      checkLoginStatus();
    }, 5000); // 5초마다

    return () => {
      window.removeEventListener("login", handleLoginEvent);
      window.removeEventListener("logout", handleLogoutEvent);
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  const handleLogout = () => {
    // 로그아웃 이벤트 발생
    window.dispatchEvent(new Event('logout'));
    logout('user_action');
  };

  return (
    <aside
      className={`
        fixed top-0 left-0 z-40 h-screen bg-white shadow-lg border-r
        transition-all duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        ${isDesktopSidebarOpen ? 'lg:translate-x-0 lg:w-56' : 'lg:translate-x-0 lg:w-16'}
      `}
    >
      <div className="flex flex-col h-full">
        {/* 로고 */}
        <div className="p-4 border-b hidden lg:block">
          {isDesktopSidebarOpen && showContent ? (
            <div className="flex items-center justify-between animate-fade-in">
              <Link href="/" className="flex items-center cursor-pointer">
                <Image 
                  src="/images/pelicanic_icon.ico"
                  alt="Pel-World Logo"
                  width={32}
                  height={32}
                  className="w-8 h-8 rounded"
                />
                <div className='text-right transition-all duration-300 ease-in-out' style={{marginLeft: '1.0rem', width: 'calc(100% - 3rem)'}}>
                  <span className="font-bold" style={{fontSize: '0.99rem'}}>Pel-World.AI</span>
                  <div className=" text-xs text-gray-500">For You</div>
                </div>
              </Link>
              <button
                onClick={toggleDesktopSidebar}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          ) : (
            <div className="flex justify-center">
              <button
                onClick={toggleDesktopSidebar}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5 text-gray-600" />
              </button>
            </div>
          )}
        </div>

        {/* 닫기 버튼 */}
        <div className="p-4 border-b lg:hidden flex justify-end">
          <button
            onClick={toggleSidebar}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* 검색 */}
        {isDesktopSidebarOpen && showContent && (
          <div className="p-4 animate-fade-in">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="검색"
                className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    const searchTerm = (e.target as HTMLInputElement).value.trim();
                    if (searchTerm) {
                      window.location.href = `/user/search?q=${encodeURIComponent(searchTerm)}`;
                    }
                  }
                }}
              />
            </div>
          </div>
        )}

        {/* 메뉴 */}
        <nav className={`flex-1 pb-4 overflow-y-auto ${isDesktopSidebarOpen ? 'px-4' : 'px-1'}`}>
          <div className="space-y-1">
            <SidebarLink href="/tasks_1" icon={PlusCircle} label="동화책 만들기" isCollapsed={!isDesktopSidebarOpen} showLabel={showContent} />
            <SidebarLink href="/tasks_2" icon={ArrowRight} label="동화 이어 만들기" isCollapsed={!isDesktopSidebarOpen} showLabel={showContent} />
            <SidebarLink 
              href="/tasks_3" 
              icon={Play} 
              label="시연페이지" 
              isCollapsed={!isDesktopSidebarOpen} 
              showLabel={showContent}
              onClick={() => {
                // 시연페이지 클릭 시 story_id를 '2241'로 설정
                sessionStorage.setItem('selectedStoryId', '2241');
              }}
            />
            <SidebarLink href="/user/mybook" icon={BookOpen} label="나의 동화책" isCollapsed={!isDesktopSidebarOpen} showLabel={showContent} />
            <SidebarLink href="/user/exbook" icon={Library} label="기존 동화책" isCollapsed={!isDesktopSidebarOpen} showLabel={showContent} />
            <SidebarLink href="/user/libbook" icon={Palette} label="창작 동화책" isCollapsed={!isDesktopSidebarOpen} showLabel={showContent} />
          </div>
        </nav>

        {/* 로그인 / 로그아웃 버튼 */}
        <div className="p-4 space-y-2 border-t bg-white">
          {isDesktopSidebarOpen && showContent ? (
            <div className="animate-fade-in">
              {isLoading ? (
                // 로딩 중일 때 내용 숨김
                <div className="w-full py-2 text-center text-gray-400 text-sm">
                  로딩 중...
                </div>
              ) : isLoggedIn ? (
                <button
                  className="w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm font-medium"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              ) : (
                <>
                  <LinkButton
                    className="w-full py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 text-sm font-medium"
                    text='로그인'
                    href="/user/login"
                  />
                  <LinkButton
                    className="w-full py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 text-sm font-medium"
                    text='회원가입'
                    href="/user/signup"
                  />
                </>
              )}
            </div>
          ) : (
            // 축소된 상태에서는 아이콘만 표시
            <div className="flex flex-col space-y-2 items-center">
              {isLoading ? (
                // 로딩 중일 때 내용 숨김
                <div className="p-2">
                  <div className="w-5 h-5 text-gray-400">...</div>
                </div>
              ) : isLoggedIn ? (
                <button
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  onClick={handleLogout}
                  title="로그아웃"
                >
                  <LogOut className="w-5 h-5 text-gray-600" />
                </button>
              ) : (
                <>
                  <Link href="/user/login" title="로그인">
                    <div className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
                      <User className="w-5 h-5 text-gray-600" />
                    </div>
                  </Link>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
