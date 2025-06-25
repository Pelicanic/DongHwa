// 백엔드 스타일 디버그 로거
const DEBUG = process.env.NODE_ENV === 'development';

// 페이지별 디버그 설정
const getPageDebug = (pageName: string) => {
  if (!DEBUG) return false;
  
  // localStorage에서 페이지별 디버그 설정 확인
  const pageDebugSettings = JSON.parse(localStorage.getItem('pageDebug') || '{}');
  
  // 전체 디버그가 활성화되어 있으면 모든 페이지 활성화
  if (localStorage.getItem('debug') === 'all') return true;
  
  // 페이지별 설정 확인 (기본값: true)
  return pageDebugSettings[pageName] !== false;
};

// 페이지별 디버그 설정 함수
export const setPageDebug = (pageName: string, enabled: boolean) => {
  if (typeof window === 'undefined') return;
  
  const pageDebugSettings = JSON.parse(localStorage.getItem('pageDebug') || '{}');
  pageDebugSettings[pageName] = enabled;
  localStorage.setItem('pageDebug', JSON.stringify(pageDebugSettings));
  
  console.log(`%c[DEBUG SETTING] ${pageName} 페이지 디버그: ${enabled ? 'ON' : 'OFF'}`, 
    `color: ${enabled ? 'green' : 'red'}; font-weight: bold;`);
};

// 전체 디버그 제어 함수
export const setGlobalDebug = (enabled: boolean) => {
  if (typeof window === 'undefined') return;
  
  if (enabled) {
    localStorage.setItem('debug', 'all');
    console.log('%c[DEBUG SETTING] 전체 디버그: ON', 'color: green; font-weight: bold;');
  } else {
    localStorage.removeItem('debug');
    localStorage.removeItem('pageDebug');
    console.log('%c[DEBUG SETTING] 전체 디버그: OFF', 'color: red; font-weight: bold;');
  }
};

// 페이지별 디버거 생성 함수
export const createPageDebugger = (pageName: string) => {
  const isPageDebugEnabled = () => getPageDebug(pageName);
  
  return {
    // 기본 디버그 출력
    log: (title: string, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "-".repeat(50));
        console.log(`[${pageName.toUpperCase()}] ${title}`);
        console.log("-".repeat(50));
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("-".repeat(50) + "\n");
      }
    },
    
    // API 관련 디버그
    api: (title: string, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "=".repeat(60));
        console.log(`[${pageName.toUpperCase()}-API] ${title}`);
        console.log("=".repeat(60));
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("=".repeat(60) + "\n");
      }
    },
    
    // 스토리 관련 디버그
    story: (title: string, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "*".repeat(60));
        console.log(`[${pageName.toUpperCase()}-STORY] ${title}`);
        console.log("*".repeat(60));
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("*".repeat(60) + "\n");
      }
    },
    
    // 사용자 액션 디버그
    user: (title: string, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "#".repeat(50));
        console.log(`[${pageName.toUpperCase()}-USER] ${title}`);
        console.log("#".repeat(50));
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("#".repeat(50) + "\n");
      }
    },
    
    // 오디오 관련 디버그
    audio: (title: string, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "~".repeat(50));
        console.log(`[${pageName.toUpperCase()}-AUDIO] ${title}`);
        console.log("~".repeat(50));
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("~".repeat(50) + "\n");
      }
    },
    
    // 에러 디버그
    error: (title: string, error?: any, data?: Record<string, any>) => {
      if (isPageDebugEnabled()) {
        console.log("\n" + "!".repeat(60));
        console.log(`[${pageName.toUpperCase()}-ERROR] ${title}`);
        console.log("!".repeat(60));
        if (error) {
          console.log("Error:");
          console.log(error);
        }
        if (data) {
          Object.entries(data).forEach(([key, value]) => {
            console.log(`${key}:`);
            console.log(value);
          });
        }
        console.log("!".repeat(60) + "\n");
      }
    }
  };
};

// 기존 전역 디버그 (하위 호환성)
export const debugLog = createPageDebugger('GLOBAL');

// 개발자 도구에서 쉽게 접근할 수 있도록 전역 객체에 추가
if (typeof window !== 'undefined' && DEBUG) {
  (window as any).setPageDebug = setPageDebug;
  (window as any).setGlobalDebug = setGlobalDebug;
  (window as any).createPageDebugger = createPageDebugger;
  
  // 현재 설정 확인 함수
  (window as any).getDebugSettings = () => {
    console.log('%c=== DEBUG SETTINGS ===', 'color: blue; font-weight: bold;');
    console.log('Global Debug:', localStorage.getItem('debug'));
    console.log('Page Debug Settings:', JSON.parse(localStorage.getItem('pageDebug') || '{}'));
  };
  
  // 빠른 설정 함수들
  (window as any).debugOnly = (pageName: string) => {
    setGlobalDebug(false);
    setPageDebug(pageName, true);
    console.log(`%c[DEBUG] Only ${pageName} page enabled`, 'color: green; font-weight: bold;');
  };
  
  (window as any).debugAll = () => {
    setGlobalDebug(true);
    console.log('%c[DEBUG] All pages enabled', 'color: green; font-weight: bold;');
  };
  
  (window as any).debugOff = () => {
    setGlobalDebug(false);
    console.log('%c[DEBUG] All pages disabled', 'color: red; font-weight: bold;');
  };
  
  // 사용 가능한 명령어 도움말
  (window as any).debugHelp = () => {
    console.log(`%c
=== PAGE DEBUG SYSTEM HELP ===

🔧 기본 명령어:
  debugAll()                    // 모든 페이지 디버그 ON
  debugOff()                    // 모든 페이지 디버그 OFF
  debugOnly('TASKS_1')          // 특정 페이지만 ON
  getDebugSettings()            // 현재 설정 확인

📄 개별 페이지 제어:
  setPageDebug('TASKS_1', true)   // Tasks_1 ON
  setPageDebug('TASKS_2', false)  // Tasks_2 OFF
  setPageDebug('LOGIN', true)     // Login ON

🎯 사용 예시:
  debugOnly('TASKS_1')          // Tasks_1만 디버그
  debugOnly('TASKS_2')          // Tasks_2만 디버그
  debugAll()                    // 모든 로그 보기
  debugOff()                    // 모든 로그 끄기

📊 로그 카테고리:
  [TASKS_1-USER] 사용자 액션
  [TASKS_2-API] API 호출
  [TASKS_3-AUDIO] 오디오 이벤트
  [LOGIN-ERROR] 에러 로그
`, 'color: #333; line-height: 1.5;');
  };
  
  // 초기 안내 메시지
  console.log('%c🐛 Page Debug System Ready!', 'color: green; font-size: 16px; font-weight: bold;');
  console.log('%c💡 Type debugHelp() for available commands', 'color: blue;');
}


export default debugLog;
