'use client';

import React, { useState } from 'react';
import { apiClient, API_ROUTES } from '@/lib/api';
import Swal from 'sweetalert2';

interface FormData {
  login_id: string;
  nickname: string;
  email: string;
  password: string;
  password_confirm: string;
}

const SignupForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({
    login_id: '',
    nickname: '',
    email: '',
    password: '',
    password_confirm: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async () => {
    const { login_id, nickname, email, password, password_confirm } = formData;

    if (!login_id || !nickname || !email || !password || !password_confirm) {
      await Swal.fire({
        icon: 'warning',
        title: '입력 오류',
        text: '모든 항목을 입력해주세요.',
        confirmButtonColor: '#3085d6'
      });
      return;
    }

    if (password !== password_confirm) {
      await Swal.fire({
        icon: 'error',
        title: '비밀번호 불일치',
        text: '비밀번호가 서로 일치하지 않습니다.',
        confirmButtonColor: '#3085d6'
      });
      return;
    }

    try {
      // 1. 비밀번호 복잡도 체크
      const complexityRes = await apiClient.post(API_ROUTES.SIGNUP, {
        action: 'check_password_strength', 
        password 
      });
      const complexity = complexityRes.data;
      if (!complexity.success) {
        await Swal.fire({
          icon: 'error',
          title: '비밀번호 보안 오류',
          text: '비밀번호가 너무 약합니다. 영문, 숫자, 특수문자를 조합해 8자 이상을 사용해주세요.',
          confirmButtonColor: '#3085d6'
        });
        return;
      }

      // 2. ID 중복 체크
      const idCheckRes = await apiClient.post(API_ROUTES.SIGNUP, {
        action: 'check_login_id', 
        login_id 
      });
      const idCheck = idCheckRes.data;
      if (!idCheck.success) {
        await Swal.fire({
          icon: 'error',
          title: '아이디 중복',
          text: '이미 사용 중인 아이디입니다.',
          confirmButtonColor: '#3085d6'
        });
        return;
      }

      // 3. 닉네임 중복 체크
      const nicknameCheckRes = await apiClient.post(API_ROUTES.SIGNUP, {
        action: 'check_nickname', 
        nickname 
      });
      const nicknameCheck = nicknameCheckRes.data;
      if (!nicknameCheck.success) {
        await Swal.fire({
          icon: 'error',
          title: '닉네임 중복',
          text: '이미 사용 중인 닉네임입니다.',
          confirmButtonColor: '#3085d6'
        });
        return;
      }

      // 4. 이메일 중복 체크
      const emailCheckRes = await apiClient.post(API_ROUTES.SIGNUP, {
        action: 'check_email', 
        email 
      });
      const emailCheck = emailCheckRes.data;
      if (!emailCheck.success) {
        await Swal.fire({
          icon: 'error',
          title: '이메일 중복',
          text: '이미 사용 중인 이메일입니다. 다른 이메일을 사용해주세요.',
          confirmButtonColor: '#3085d6'
        });
        return;
      }

      // 5. 최종 회원가입 요청
      const signupRes = await apiClient.post(API_ROUTES.SIGNUP, {
        action: 'signup',
        login_id,
        nickname,
        email,
        password,
        password_confirm
      });

      const result = signupRes.data;
      if (result.success) {
        // 회원가입 성공 후 자동 로그인 상태로 설정
        localStorage.setItem('user_id', result.data.user_id.toString());
        // 로그인 이벤트 발생
        window.dispatchEvent(new Event('login'));
        
        await Swal.fire({
          icon: 'success',
          title: '회원가입 성공! 🎉',
          text: 'Pel-World에서 마음껏 동화를 만들어보세요!',
          confirmButtonColor: '#3085d6',
          confirmButtonText: '시작하기!'
        });
        // 메인 페이지로 이동
        window.location.href = '/';
      } else {
        await Swal.fire({
          icon: 'error',
          title: '회원가입 실패',
          text: result.message,
          confirmButtonColor: '#3085d6'
        });
      }
    } catch (error) {
      await Swal.fire({
        icon: 'error',
        title: '서버 오류',
        text: '서버와 통신 중 오류가 발생했습니다.',
        confirmButtonColor: '#3085d6'
      });
      console.error('Signup error:', error);
    }
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center"
      style={{ backgroundImage: "url('/images/signup-bg1.jpg')",
        backgroundSize: 'cover',
        backgroundPosition: 'center'
       }}
    >
      <div className="flex bg-white rounded-lg shadow-lg overflow-hidden p-4 w-full md:w-3/4 lg:w-2/3 xl:w-1/2 2xl:w-1/3">
        <div className="w-full p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-8 text-center">회원가입</h1>

          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="login_id" className="block text-sm font-medium text-gray-700 mb-1">ID</label>
                <input
                  type="text"
                  id="login_id"
                  name="login_id"
                  value={formData.login_id}
                  onChange={handleInputChange}
                  placeholder="아이디를 입력하세요"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
                />
              </div>
              <div>
                <label htmlFor="nickname" className="block text-sm font-medium text-gray-700 mb-1">Nickname</label>
                <input
                  type="text"
                  id="nickname"
                  name="nickname"
                  value={formData.nickname}
                  onChange={handleInputChange}
                  placeholder="닉네임을 입력하세요"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="이메일을 입력하세요"
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="비밀번호를 입력하세요"
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
              />
            </div>

            <div>
              <label htmlFor="password_confirm" className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
              <input
                type="password"
                id="password_confirm"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleInputChange}
                placeholder="비밀번호 확인"
                className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700"
              />
            </div>

            <button
              onClick={handleSubmit}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 font-medium transition-colors"
            >
              회원가입하기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SignupForm;
