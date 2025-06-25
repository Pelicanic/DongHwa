import axios from 'axios';
import { debugLog } from './logger';

const getBaseURL = () => {
  if (typeof window !== 'undefined') {
    // 클라이언트에서는 현재 host 기반으로 판단
    return window.location.hostname === 'localhost' 
      ? 'http://localhost:8721'
      : 'https://api.pel-world.com';  // 실제 도메인으로 대체
  }
  
  // 서버에서는 NODE_ENV 기반으로 판단
  return process.env.NODE_ENV === 'production'
    ? 'https://api.pel-world.com'  // 실제 도메인으로 대체
    : 'http://localhost:8721';
};

export const apiClient = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가 및 로깅
apiClient.interceptors.request.use(
  (config) => {
    // API 요청 로깅
    debugLog.api('API Request', {
      'URL': config.url || '',
      'Method': config.method?.toUpperCase() || 'POST',
      'Data': config.data
    });
    
    // 클라이언트에서만 localStorage 접근
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    debugLog.error('Request Error', error);
    return Promise.reject(error);
  }
);

// 응답 인터셉터 - 에러 핸들링 및 로깅
apiClient.interceptors.response.use(
  (response) => {
    // API 응답 로깅
    debugLog.api('API Response', {
      'URL': response.config.url || '',
      'Status': response.status,
      'Status Text': response.statusText,
      'Data': response.data
    });
    return response;
  },
  (error) => {
    // API 에러 로깅
    debugLog.error('API Error', error, {
      'URL': error.config?.url || 'Unknown',
      'Status': error.response?.status,
      'Response Data': error.response?.data,
      'Message': error.message
    });
    
    // 401 에러 시 로그인 페이지로 리다이렉트
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      debugLog.user('Auto logout due to 401 error');
      localStorage.removeItem('access');
      localStorage.removeItem('refresh');
      localStorage.removeItem('user_id');
      localStorage.removeItem('nickname');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API 엔드포인트 상수
export const API_ROUTES = {
  // 스토리 관련
  STORY_CREATE: '/api/v1/chat/story/',
  STORY_LIST: '/api/v1/list/story/',
  STORY_MAIN: '/api/v1/main/story/',
  STORY_BY_ID: '/api/v1/story/story/',
  USER_IN_PROGRESS_STORY: '/api/v1/user/in-progress-story/',
  
  // 단락 관련
  PARAGRAPH_QA: '/api/v1/paragraphQA/story/',
  STORY_PARAGRAPH: '/api/v1/storyParagraph/story/',
  
  // 일러스트 관련
  ILLUSTRATION: '/api/v1/illustration/story/',
  
  // 검색 관련
  SEARCH_STORIES: '/api/v1/search/story/',
  
  // 회원 관련
  LOGIN: '/member/login/',
  TEST_LOGIN: '/member/test-login/',
  SIGNUP: '/member/signup/',
} as const;
