'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Image from "next/image";
import Link from "next/link";

const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  const closeSidebar = () => setIsSidebarOpen(false);

  useEffect(() => {
    // 경로 변경 시 사이드바 닫기
    closeSidebar();
  }, [pathname]);
  
  return (
    <div className="min-h-screen flex flex-col lg:flex-row">

      <div className="lg:hidden bg-white border-b px-4 py-3 flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <Image
            src="/logo.png"
            alt="Logo"
            width={32}
            height={32}
            className="w-8 h-8"
            priority
          />
          <span className="text-lg font-bold">Pel-World</span>
        </div>
        <button 
          onClick={toggleSidebar}
          className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* 사이드바 */}
      <aside className={`
        w-64 bg-white border-r border-gray-200 shadow-lg
        lg:fixed lg:top-0 lg:left-0 lg:h-full lg:block
        ${isSidebarOpen ? 'block' : 'hidden lg:block'}
        fixed inset-y-0 left-0 z-40 transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="h-full flex flex-col fixed overflow-y-auto w-full">
          {/* 데스크톱 로고 헤더 */}
          <div className="hidden lg:block p-3 border-b">
            <div className="text-center flex items-center justify-between space-x-2">
              <Link href="/" className="flex items-center space-x-2">
                <div>
                  <Image
                    src="/logo.png"
                    alt="Logo"
                    width={48}
                    height={48}
                    priority
                  />
                </div>
                <div className="text-lg font-bold">Pel-World</div>
              </Link>
              {/* 사이드바 토글 버튼 */}
              <div className='sidebar-toggle border w-8'></div>
            </div>
          </div>
          
          {/* 사이드바 네비게이션 */}
          <nav className="flex-1 p-4">
            {/* 여기에 네비게이션 메뉴 항목들 추가 */}
            <div className="space-y-2">
              <div>
                <div>카테고리</div>
                <div>
                  <div>전체 카테고리</div>
                  <div>하위 카테고리 1</div>
                  <div>하위 카테고리 2</div>
                </div>
              </div>
              <Link href="/profile" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">
                나의 동화책
              </Link>
              <Link href="/profile" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">
                동화책 만들기
              </Link>
              <Link href="/profile" className="block px-3 py-2 text-gray-700 hover:bg-gray-100 rounded">
                시연 페이지
              </Link>
            </div>
          </nav>
          <div className="p-4 border-t text-center text-gray-500">
            <div>로그인</div>
            <div>회원가입</div>
          </div>
        </div>
      </aside>
      {/* 사이드바 여백 */}
      <div className='w-64'/>
      
      {/* 메인 콘텐츠 영역 */}
      <main className="flex-1 min-w-0 overflow-hidden">
            {children}
      </main>
      
      {/* 모바일 오버레이 */}
      {isSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30 transition-opacity duration-300"
          onClick={closeSidebar}
        />
      )}
    </div>
  );
};

export default DashboardLayout;