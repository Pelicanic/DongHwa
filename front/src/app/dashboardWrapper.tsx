'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from '@/(components)/Sidebar/index';
import MobileHeader from '@/(components)/Header/mobileHeader';
import LogoutOnCloseProvider from '@/(components)/LogoutOnCloseProvider';


const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isDesktopSidebarOpen, setIsDesktopSidebarOpen] = useState(true);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  const closeSidebar = () => setIsSidebarOpen(false);
  const toggleDesktopSidebar = () => setIsDesktopSidebarOpen(prev => !prev);

  useEffect(() => {
    // Close sidebar when navigating to a new page
  }, [isSidebarOpen]);

  useEffect(() => {
    // Close sidebar when the pathname changes
    closeSidebar();
  }, [pathname]);
  
  return (
    <div className="relative min-h-screen bg-gray-50">
      {/* Mobile Header */}
      <MobileHeader isSidebarOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      
      {/* Desktop Layout Container */}
      <div className="flex">
        {/* Sidebar */}
        <Sidebar 
          isSidebarOpen={isSidebarOpen} 
          toggleSidebar={closeSidebar}
          isDesktopSidebarOpen={isDesktopSidebarOpen}
          toggleDesktopSidebar={toggleDesktopSidebar}
        />
        
        {/* Sidebar Spacer for Desktop */}
        <div className={`hidden lg:block flex-shrink-0 transition-all duration-300 ${isDesktopSidebarOpen ? 'w-56' : 'w-16'}`} />

        {/* Main Content Area */}
        <main className="flex-1 min-w-0">
          <div className="w-full h-full overflow-x-hidden">
            {children}
          </div>
        </main>
      </div>

      {/* Overlay for mobile */}
      {isSidebarOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={closeSidebar}
        />
      )}
    </div>
  );
};

const DashboardWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      {/* 페이지 닫기 시 자동 로그아웃 설정 */}
      <LogoutOnCloseProvider />
      <DashboardLayout>{children}</DashboardLayout>
    </>
  );
};

export default DashboardWrapper;
