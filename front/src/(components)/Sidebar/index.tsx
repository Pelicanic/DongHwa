// 작성자 : 최재우
// 마지막 수정일 : 2025-06-18
// 마지막 수정 내용 : refresh 토큰을 한 번 사용하여 폐기 후 완전 로그아웃 처리
'use client';

import React, { useEffect, useState } from 'react';
import { Search, Home, Book, Tag, Users, CreditCard, Settings, X } from 'lucide-react';
import LinkButton from '@/(components)/Button/button';
import SidebarLink from '@/(components)/Button/sidebarlinkButton';

interface SidebarProps {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

const Sidebar = ({ isSidebarOpen, toggleSidebar }: SidebarProps) => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const checkLoginStatus = async () => {
    const access = localStorage.getItem('access');
    const refresh = localStorage.getItem('refresh');

    if (!access) return setIsLoggedIn(false);

    try {
      const res = await fetch('http://localhost:8721/member/status/', {
        method: 'GET',
        headers: { Authorization: `Bearer ${access}` }
      });

      if (res.ok) {
        setIsLoggedIn(true);
      } else if (refresh) {
        const refreshRes = await fetch('http://localhost:8721/member/token/refresh/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ refresh })
        });

        const data = await refreshRes.json();
        if (refreshRes.ok && data.access) {
          localStorage.setItem('access', data.access);
          setIsLoggedIn(true);
        } else {
          localStorage.removeItem('access');
          localStorage.removeItem('refresh');
          setIsLoggedIn(false);
        }
      }
    } catch {
      setIsLoggedIn(false);
    }
  };

  useEffect(() => {
    checkLoginStatus();

    const handleLoginEvent = () => checkLoginStatus();
    window.addEventListener("login", handleLoginEvent);

    return () => {
      window.removeEventListener("login", handleLoginEvent);
    };
  }, []);

  const handleLogout = async () => {
    const refresh = localStorage.getItem('refresh');

    if (refresh) {
      try {
        await fetch("http://localhost:8721/member/token/refresh/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ refresh }),
        });
      } catch (e) {
        console.warn("refresh 소진 실패 (무시 가능):", e);
      }
    }

    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("user_id");
    localStorage.removeItem("nickname");
    localStorage.removeItem("age");

    setIsLoggedIn(false);
    window.location.reload();
  };

  return (
    <aside
      className={`
        fixed top-0 left-0 z-40 h-screen w-64 bg-white shadow-lg border-r
        transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}
    >
      <div className="flex flex-col h-full">
        {/* 로고 */}
        <div className="p-4 border-b hidden lg:block">
          <div className="flex items-center">
            <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
              <X className="w-5 h-5 text-white" />
            </div>
            <div className='text-right w-1/2 ml-6'>
              <span className="font-bold text-lg">Pel-World.AI</span>
              <div className=" text-xs text-gray-500">For You</div>
            </div>
          </div>
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
        <div className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="검색"
              className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
            />
          </div>
        </div>

        {/* 메뉴 */}
        <nav className="flex-1 px-4 pb-4 overflow-y-auto">
          <div className="space-y-1">
            <SidebarLink href="/" icon={Home} label="홈" />
            <SidebarLink href="/overview" icon={Book} label="내 동화책" />
            <SidebarLink href="/user/favoriteTag" icon={Tag} label="좋아하는 동화책" />
            <SidebarLink href="/user/friends" icon={Users} label="친구" />
            <SidebarLink href="/user/mySubscription" icon={CreditCard} label="구독" />
            <SidebarLink href="/user/setting" icon={Settings} label="설정" />
          </div>
        </nav>

        {/* 로그인 / 로그아웃 버튼 */}
        <div className="p-4 space-y-2 border-t bg-white">
          {isLoggedIn ? (
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
      </div>
    </aside>
  );
};

export default Sidebar;
