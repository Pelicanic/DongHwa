// 페이지별 디버그 관리 시스템 사용 가이드

/*
브라우저 콘솔에서 사용 가능한 명령어들:

1. 전체 디버그 제어
   - setGlobalDebug(true)   // 모든 페이지 디버그 ON
   - setGlobalDebug(false)  // 모든 페이지 디버그 OFF

2. 페이지별 디버그 제어
   - setPageDebug('TASKS_1', true)   // Tasks_1 페이지만 ON
   - setPageDebug('TASKS_1', false)  // Tasks_1 페이지만 OFF
   - setPageDebug('TASKS_2', true)   // Tasks_2 페이지만 ON
   - setPageDebug('TASKS_3', false)  // Tasks_3 페이지만 OFF

3. 여러 페이지 선택적 활성화
   setPageDebug('TASKS_1', true);
   setPageDebug('TASKS_2', true);
   setPageDebug('TASKS_3', false);
   setPageDebug('LOGIN', false);

4. 현재 설정 확인
   console.log(JSON.parse(localStorage.getItem('pageDebug') || '{}'));

5. 페이지별 로그 출력 예시
   [TASKS_1] 선택지 클릭           // Tasks_1 페이지의 사용자 액션
   [TASKS_2-API] API 응답 데이터    // Tasks_2 페이지의 API 관련
   [TASKS_3-AUDIO] 배경음악 설정    // Tasks_3 페이지의 오디오 관련
   [LOGIN-ERROR] 로그인 실패       // Login 페이지의 에러
*/

// 페이지별 디버거 사용 예제:

// === tasks_1/page.tsx ===
import { createPageDebugger } from '@/lib/logger';

const Tasks1Page = () => {
  const debug = createPageDebugger('TASKS_1');
  
  const handleSubmit = () => {
    debug.story('스토리 생성 시작', {
      'User Answers': userAnswers,
      'Total Questions': totalSlides
    });
  };
};

// === tasks_2/page.tsx ===
import { createPageDebugger } from '@/lib/logger';

const Tasks2Page = () => {
  const debug = createPageDebugger('TASKS_2');
  
  const playAudio = () => {
    debug.audio('배경음악 재생', {
      'Music File': musicFile,
      'Volume': volume
    });
  };
};

// === login/page.tsx ===
import { createPageDebugger } from '@/lib/logger';

const LoginPage = () => {
  const debug = createPageDebugger('LOGIN');
  
  const handleLogin = async () => {
    debug.user('로그인 시도', {
      'Login ID': loginId
    });
    
    try {
      // API 호출...
    } catch (error) {
      debug.error('로그인 실패', error, {
        'Login ID': loginId,
        'Timestamp': new Date().toISOString()
      });
    }
  };
};

// === 개발자 도구에서 실시간 제어 ===
/*
// 현재 Tasks_1 페이지에서 작업 중이고, 다른 페이지 로그는 보고 싶지 않을 때:
setPageDebug('TASKS_1', true);
setPageDebug('TASKS_2', false);
setPageDebug('TASKS_3', false);
setPageDebug('LOGIN', false);

// API 관련 문제를 디버깅할 때, 모든 페이지의 API 로그만 보고 싶을 때:
// (이 경우 각 페이지에서 debug.api() 호출만 표시됨)
setGlobalDebug(true); // 먼저 전체 활성화

// 특정 페이지의 특정 기능만 디버깅하고 싶을 때:
setPageDebug('TASKS_2', true);  // Tasks_2의 오디오 문제만 확인
setPageDebug('TASKS_1', false);
setPageDebug('TASKS_3', false);

// 모든 디버그 끄기:
setGlobalDebug(false);
*/

export {}; // 모듈로 만들기 위한 export