'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, API_ROUTES } from '@/lib/api';

const Login: React.FC = () => {
  const router = useRouter();
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await apiClient.post(API_ROUTES.LOGIN, {
        login_id: loginId, 
        password: password 
      });

      const data = res.data;

      if (data.success) {
        localStorage.setItem('user_id', data.data.user_id.toString());
        localStorage.setItem('access', data.data.access);
        localStorage.setItem('refresh', data.data.refresh);
        localStorage.setItem('nickname', data.data.nickname);
        window.dispatchEvent(new Event('login'));
        router.push('/');
      } else {
        setError(data.message || '로그인 실패');
      }
    } catch {
      setError('서버 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleTestLogin = async () => {
    setError('');
    setTestLoading(true);

    try {
      const res = await apiClient.post(API_ROUTES.TEST_LOGIN, {});
      const data = res.data;

      if (data.success) {
        localStorage.setItem('user_id', data.data.user_id.toString());
        localStorage.setItem('access', data.data.access);
        localStorage.setItem('refresh', data.data.refresh);
        localStorage.setItem('nickname', data.data.nickname);
        window.dispatchEvent(new Event('login'));
        router.push('/');
      } else {
        setError(data.message || '테스트 로그인 실패');
      }
    } catch {
      setError('테스트 로그인 중 오류가 발생했습니다.');
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div
      className="
        min-h-screen
        bg-[url('/images/login-bg.jpg')]
        bg-cover
        bg-center
        flex flex-col items-center justify-start
        pt-28 px-4
      "
    >
      <div className="w-full max-w-5xl flex justify-center items-center mb-10 px-4">
        <h1 className="text-2xl font-bold text-gray-700">동화책 생성서비스</h1>
      </div>

      <div className="bg-white/60 backdrop-blur-md w-full max-w-lg rounded-xl p-10 shadow-lg text-center">
        <h2 className="text-2xl font-semibold mb-6 text-gray-800">Welcome back</h2>

        <form className="space-y-4 text-left" onSubmit={handleSubmit}>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">ID</label>
            <input
              type="text"
              placeholder="ID"
              value={loginId}
              onChange={(e) => setLoginId(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700">Password</label>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border rounded-lg px-3 py-2"
              required
            />
          </div>
          {error && <div className="text-red-500 text-sm font-medium">{error}</div>}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-100 text-gray-800 font-semibold py-2 rounded-full hover:bg-blue-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '로그인 중...' : 'Log in'}
          </button>
        </form>
        
        {/* Test Login 버튼 */}
        {/* <div className="mt-4">
          <button
            onClick={handleTestLogin}
            disabled={testLoading || loading}
            className="w-full bg-orange-100 text-gray-800 font-semibold py-2 rounded-full hover:bg-orange-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-orange-300"
          >
            {testLoading ? '테스트 로그인 중...' : 'Test Login'}
          </button>
          <p className="text-xs text-gray-500 mt-2 text-center">
            개발/테스트용 자동 로그인
          </p>
        </div> */}
      </div>
    </div>
  );
};

export default Login;
