'use client';

import React, { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Sidebar from '@/(components)/Sidebar/index';
import Navbar from '@/(components)/Navbar/index';
import MobileHeader from '@/(components)/Header/mobileHeader';


const DashboardLayout = ({ children }: { children: React.ReactNode }) => {
  const pathname = usePathname();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const toggleSidebar = () => setIsSidebarOpen(prev => !prev);
  const closeSidebar = () => setIsSidebarOpen(false);

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
        <Sidebar isSidebarOpen={isSidebarOpen} toggleSidebar={closeSidebar} />
        
        {/* Sidebar Spacer for Desktop */}
        <div className="hidden lg:block w-64 flex-shrink-0" />

        {/* Main Content Area */}
        <main className="flex-1 min-w-0">
          <div className="pt-16 lg:pt-0">
            {pathname !== '/' && <Navbar />}
            <div className="p-4 sm:p-6 lg:p-8">
              {children}
            </div>
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
      <DashboardLayout>{children}</DashboardLayout>
  );
};

export default DashboardWrapper;
