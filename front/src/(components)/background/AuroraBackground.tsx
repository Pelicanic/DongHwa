'use client';

// 작성자 : 최준혁
// 기능 : AuroraBackground 컴포넌트
// 마지막 수정일 : 2025-06-06
const AuroraBackground = () => {
  return (
    <div className="fixed inset-0 z-0 overflow-hidden">
      {/* 움직이는 오로라 */}
      <div className="absolute inset-0 animate-aurora bg-[radial-gradient(ellipse_at_top_left,_var(--tw-gradient-stops))] from-pink-200/40 via-purple-300/20 to-indigo-200/30 blur-[120px] opacity-40 mix-blend-screen" />
    </div>
  );
};

export default AuroraBackground;
