// 작성자 : 최재우
// 마지막 수정일 : 2025-06-03
// 마지막 수정 내용 : 모바일 헤더 컴포넌트 작성

import React from 'react';
import { Menu } from 'lucide-react';
import Image from 'next/image';

interface MobileHeaderProps {
  isSidebarOpen: boolean;
  toggleSidebar: () => void;
}

const MobileHeader = ({ toggleSidebar }: MobileHeaderProps) => {
  return (
    <header className="lg:hidden fixed top-0 left-0 right-0 bg-white shadow-sm border-b z-50 h-16">
      <div className="flex items-center justify-between px-4 h-full">
        <button
          onClick={toggleSidebar}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          aria-label="Toggle menu"
        >
          <Menu className="w-6 h-6 text-gray-600" />
        </button>
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-black rounded flex items-center justify-center">
            <Image 
              src="/images/pelicanic_icon.ico" 
              alt="Pelicanic Icon" 
              width={20} 
              height={20} 
              className="w-5 h-5"
            />
          </div>
          <span className="font-bold text-lg">Pel-World.AI</span>
        </div>
        <div className="w-10" /> {/* Placeholder for balance */}
      </div>
    </header>
  );
};

export default MobileHeader;