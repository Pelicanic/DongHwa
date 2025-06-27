import { apiClient, API_ROUTES } from '@/lib/api';
import { debugLog } from '@/lib/logger';

/**
 * 로그아웃 함수
 * - 서버에 로그아웃 요청
 * - 로컬 스토리지 정리
 * - 로그인 페이지로 리다이렉트
 */
export const logout = async (reason: string = 'user_action') => {
  try {
    debugLog.user('로그아웃 시작', { reason });
    
    // 서버에 로그아웃 요청
    await apiClient.post(API_ROUTES.LOGOUT);
    
    debugLog.user('서버 로그아웃 완료');
  } catch (error) {
    debugLog.error('서버 로그아웃 오류', error);
    // 서버 오류가 있어도 클라이언트 정리는 계속 진행
  } finally {
    // 로컬 스토리지 정리
    clearLocalStorage();
    
    // 로그인 페이지로 리다이렉트
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
};

/**
 * 로컬 스토리지 정리 함수
 */
export const clearLocalStorage = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user_id');
    localStorage.removeItem('nickname');
    
    debugLog.user('로컬 스토리지 정리 완료');
  }
};

/**
 * 브라우저/탭 완전 닫기 시에만 로그아웃 처리
 * visibilitychange + beforeunload 조합으로 정확한 감지
 */
export const setupPageCloseLogout = () => {
  if (typeof window === 'undefined') return;

  let isNavigating = false;
  let isTabHidden = false;

  // 탭이 숨겨졌는지 감지
  const handleVisibilityChange = () => {
    if (document.hidden) {
      isTabHidden = true;
      debugLog.user('탭이 숨겨짐 (다른 탭으로 이동 또는 최소화)');
    } else {
      isTabHidden = false;
      isNavigating = false; // 탭이 다시 보이면 내비게이션 플래그 리셋
      debugLog.user('탭이 다시 보임');
    }
  };

  // 페이지 이동 감지
  const handleClick = (e: Event) => {
    const target = e.target as HTMLElement;
    const link = target.closest('a');
    
    if (link && link.href) {
      // 내부 링크인지 확인
      const isInternalLink = link.href.startsWith(window.location.origin) || 
                            link.href.startsWith('/') || 
                            link.href.startsWith('./') || 
                            link.href.startsWith('../');
      
      if (isInternalLink && !link.target) {
        isNavigating = true;
        debugLog.user('내부 페이지 이동 감지');
        
        // 3초 후 플래그 리셋 (페이지 로드가 실패할 경우 대비)
        setTimeout(() => {
          isNavigating = false;
        }, 3000);
      }
    }
  };

  // 폼 제출 감지
  const handleSubmit = () => {
    isNavigating = true;
    debugLog.user('폼 제출 감지');
    
    setTimeout(() => {
      isNavigating = false;
    }, 3000);
  };

  // 브라우저 뒤로가기/앞으로가기 감지
  const handlePopState = () => {
    isNavigating = true;
    debugLog.user('브라우저 히스토리 이동 감지');
    
    setTimeout(() => {
      isNavigating = false;
    }, 3000);
  };

  // beforeunload: 페이지를 떠날 때 발생
  const handleBeforeUnload = () => {
    // 페이지 이동 중이면 로그아웃하지 않음
    if (isNavigating) {
      debugLog.user('페이지 이동으로 인한 beforeunload - 로그아웃 제외');
      return;
    }

    // 탭이 숨겨진 상태가 아니면 (새로고침이나 다른 사이트 이동) 로그아웃하지 않음
    if (!isTabHidden) {
      debugLog.user('새로고침 또는 외부 사이트 이동 - 로그아웃 제외');
      return;
    }

    // 로그인되어 있는지 확인
    const token = localStorage.getItem('access');
    if (!token) return;

    debugLog.user('브라우저/탭 닫기로 판단 - 로그아웃 처리');
    
    // 동기적으로 로그아웃 요청
    const logoutData = JSON.stringify({});
    const logoutUrl = `${apiClient.defaults.baseURL}${API_ROUTES.LOGOUT}`;
    
    try {
      navigator.sendBeacon(logoutUrl, logoutData);
    } catch (error) {
      debugLog.error('sendBeacon 로그아웃 오류', error);
    }
    
    // 로컬 스토리지 정리
    clearLocalStorage();
  };

  // 이벤트 등록
  document.addEventListener('visibilitychange', handleVisibilityChange);
  document.addEventListener('click', handleClick, true); // capture phase에서 감지
  document.addEventListener('submit', handleSubmit);
  window.addEventListener('popstate', handlePopState);
  window.addEventListener('beforeunload', handleBeforeUnload);
  
  // 클린업 함수
  return () => {
    document.removeEventListener('visibilitychange', handleVisibilityChange);
    document.removeEventListener('click', handleClick, true);
    document.removeEventListener('submit', handleSubmit);
    window.removeEventListener('popstate', handlePopState);
    window.removeEventListener('beforeunload', handleBeforeUnload);
  };
};
