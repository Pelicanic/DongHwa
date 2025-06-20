"use client";

import React, { useState } from 'react';
import Sidebar from '../Sidebar/Sidebar';
import './Header.css';

interface HeaderProps {
  title?: string;
}

const Header: React.FC<HeaderProps> = ({ title = "동화 만들기" }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <>
      {/* 헤더 */}
      <div className="app-header">
        <div className="header-left">
          <button 
            className="menu-button"
            onClick={toggleSidebar}
            aria-label="메뉴 열기"
          >
            <div className="hamburger">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </button>
          <div className="logo">
            {/* <img src="/logo.png" alt="로고" className="logo-image" /> */}
            <div className="logo-placeholder">🏠</div>
            <span className="logo-text">{title}</span>
          </div>
        </div>
      </div>

      {/* 사이드바 */}
      <Sidebar isOpen={sidebarOpen} onClose={closeSidebar} />
      
      {/* 오버레이 */}
      {sidebarOpen && (
        <div 
          className="sidebar-overlay" 
          onClick={closeSidebar}
        />
      )}
    </>
  );
};

export default Header;
