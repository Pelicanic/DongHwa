'use client';

import React, { useState } from 'react';

function PageWithModal() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  return (
    <div className="relative min-h-screen bg-gray-50">
      {/* 페이지 콘텐츠 */}
      <div className="p-8">
        <h1>메인 페이지</h1>
        <button onClick={() => setIsModalOpen(true)}>
          모달 열기
        </button>
      </div>
      
      {/* 모달 - relative 부모를 기준으로 배치 */}
      {isModalOpen && (
        <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg">
            모달 내용
          </div>
        </div>
      )}
    </div>
  );
}