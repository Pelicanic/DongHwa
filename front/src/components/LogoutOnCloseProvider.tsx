'use client';

import { useEffect } from 'react';
import { setupPageCloseLogout } from '@/lib/utils/logout';

/**
 * 페이지 닫기 시 자동 로그아웃을 설정하는 컴포넌트
 */
const LogoutOnCloseProvider: React.FC = () => {
  useEffect(() => {
    // 페이지 닫기 시 로그아웃 설정
    const cleanup = setupPageCloseLogout();
    
    // 컴포넌트 언마운트 시 이벤트 리스너 제거
    return cleanup;
  }, []);

  // 이 컴포넌트는 UI를 렌더링하지 않음
  return null;
};

export default LogoutOnCloseProvider;
