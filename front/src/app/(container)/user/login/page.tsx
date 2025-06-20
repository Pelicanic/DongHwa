'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

const Login: React.FC = () => {
  const router = useRouter();
  const [loginId, setLoginId] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const res = await fetch('http://localhost:8721/member/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ login_id: loginId, password: password })
      });

      const data = await res.json();

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
            className="w-full bg-blue-100 text-gray-800 font-semibold py-2 rounded-full hover:bg-blue-200 transition-colors"
          >
            Log in
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
