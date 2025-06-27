import Swal from 'sweetalert2';

// 로그인 상태 확인 함수
export const checkLoginStatus = (): boolean => {
  if (typeof window === 'undefined') return false;
  
  const userId = localStorage.getItem('user_id');
  const accessToken = localStorage.getItem('access');
  const nickname = localStorage.getItem('nickname');
  
  return !!(userId && accessToken && nickname);
};

// 로그인 확인 및 리다이렉트 함수
export const requireLogin = async (redirectUrl: string = '/'): Promise<boolean> => {
  const isLoggedIn = checkLoginStatus();
  
  if (!isLoggedIn) {
    const result = await Swal.fire({
      title: '로그인 필요',
      text: '이 페이지를 이용하려면 로그인이 필요합니다.',
      icon: 'warning',
      confirmButtonText: '메인으로',
      confirmButtonColor: '#3b82f6',
      allowOutsideClick: false,
      allowEscapeKey: false
    });
    
    // 사용자가 확인 버튼을 누른 후에 이동
    if (result.isConfirmed) {
      window.location.href = redirectUrl;
    }
    
    return false;
  }
  
  return true;
};
