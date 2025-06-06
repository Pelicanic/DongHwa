'use client';

import { useEffect, useState } from 'react';

const backgrounds = [
  '/images/aurora1.png',
  '/images/bg1.jpg',
  '/images/aurora3.png',
];

const BackgroundSlideshow = () => {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const timer = setInterval(() => {
      setFade(false); // fade out
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % backgrounds.length);
        setFade(true); // fade in
      }, 1000); // 1s fade
    }, 10000); // every 10s

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="fixed inset-0 z-0">
      {/* 배경 이미지 */}
      <div
        className={`absolute inset-0 transition-opacity duration-1000 ${
          fade ? 'opacity-10' : 'opacity-0'
        }`}
        style={{
          backgroundImage: `url(${backgrounds[index]})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          filter: 'blur(10px)',
        }}
      />

      {/* 💫 밝은 오로라 느낌 그라디언트 오버레이 */}
      <div className="absolute inset-0 pointer-events-none animate-pulse bg-gradient-to-tr from-pink-300/30 via-purple-300/20 to-fuchsia-300/30 mix-blend-screen blur-2xl" />
    </div>
  );
};

export default BackgroundSlideshow;
