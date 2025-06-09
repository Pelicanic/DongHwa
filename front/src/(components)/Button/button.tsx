// 작성자 : 최재우
// 마지막 수정일 : 2025-06-04
// 마지막 수정 내용 : 버튼 태그와 link 태그의 스타일을 통일하여 일관성 있는 디자인 적용

import React from 'react';
import Link from 'next/link';

interface ButtonProps {
  href?: string;
  className?: string;
  text: string;
  size?: 'small' | 'common' | 'large';
  hide?: boolean;
  onClick?: (event: React.MouseEvent<HTMLButtonElement | HTMLAnchorElement>) => void;
  id?: string;
  external?: boolean; // 외부 링크 여부
  target?: '_blank' | '_self' | '_parent' | '_top';
}

const LinkButton: React.FC<ButtonProps> = ({ 
  href, 
  className = "", 
  text, 
  size = "common", 
  hide = false, 
  onClick, 
  id,
  external = false,
  target
}) => {
  // size에 따른 클래스 추가 (예시)
  const sizeClasses = {
    small: 'px-3 py-1 text-sm',
    common: 'px-4 py-2 text-base',
    large: 'px-6 py-3 text-lg'
  };

  const combinedClassName = `${className} ${sizeClasses[size]}`.trim();
  const style = hide ? { display: 'none' } : undefined;

  // // 외부 링크이거나 http로 시작하는 경우 a 태그 사용
  // if (external || href?.startsWith('http') || href?.startsWith('mailto:')) {
  //   return (
  //     <a
  //       href={href}
  //       className={combinedClassName}
  //       style={style}
  //       onClick={onClick}
  //       id={id}
  //       target={target || (external ? '_blank' : undefined)}
  //       rel={external ? 'noopener noreferrer' : undefined}
  //     >
  //       {text}
  //     </a>
  //   );
  // }

  // 내부 링크인 경우 Next.js Link 사용
  if (href) {
    return (
      <Link 
        href={href}
        className={combinedClassName}
        style={{...style, display: 'inline-block', textAlign: 'center'}}
        onClick={onClick}
        id={id}
      >
        {text}
      </Link>
    );
  }

  // href가 없으면 button 태그 사용
  return (
    <button
      type="button"
      className={combinedClassName}
      style={style}
      onClick={onClick}
      id={id}
    >
      {text}
    </button>
  );
};

export default LinkButton;

// 사용 예시
// export const ButtonExamples = () => {
//   return (
//     <div className="space-y-4">
//       {/* 내부 링크 - Link 컴포넌트 사용 */}
//       <LinkButton 
//         href="/about" 
//         text="About Page" 
//         className="bg-blue-500 text-white rounded"
//         size="common"
//       />

//       {/* 외부 링크 - a 태그 사용 */}
//       <LinkButton 
//         href="https://google.com" 
//         text="Google" 
//         external={true}
//         className="bg-green-500 text-white rounded"
//       />

//       {/* 버튼 동작 - button 태그 사용 */}
//       <LinkButton 
//         text="Click Me" 
//         onClick={(e) => console.log('Clicked!')}
//         className="bg-purple-500 text-white rounded"
//       />

//       {/* 동적 라우트 */}
//       <LinkButton 
//         href="/products/123" 
//         text="Product Detail"
//         className="bg-gray-500 text-white rounded"
//       />

//       {/* 쿼리 파라미터 포함 */}
//       <LinkButton 
//         href={{
//           pathname: '/search',
//           query: { category: 'books', sort: 'newest' }
//         } as any}
//         text="Search Books"
//         className="bg-yellow-500 text-black rounded"
//       />
//     </div>
//   );
// };