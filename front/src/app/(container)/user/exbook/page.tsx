'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import MainCard from '@/(components)/Card/Cardbox';
import { storyDTO } from '@/lib/type/story';
import Loading from '@/(components)/Loading/loading';

interface PaginationInfo {
  current_page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

const getPublishedStories = async (page: number = 1): Promise<{stories: storyDTO[], pagination: PaginationInfo}> => {
  try {
    const res = await axios.post('http://localhost:8721/api/v1/list/story/', {
      status: 'published',
      page: page,
      page_size: 10
    });
    
    return {
      stories: res.data.stories || [],
      pagination: res.data.pagination || {
        current_page: 1,
        page_size: 10,
        total_count: 0,
        total_pages: 1,
        has_next: false,
        has_previous: false
      }
    };
  } catch (error) {
    console.error("공개된 동화를 가져오는 중 오류 발생:", error);
    throw error;
  }
};

const ExBook: React.FC = () => {
  const [publishedStories, setPublishedStories] = useState<storyDTO[]>([]);
  const [pagination, setPagination] = useState<PaginationInfo>({
    current_page: 1,
    page_size: 10,
    total_count: 0,
    total_pages: 1,
    has_next: false,
    has_previous: false
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPublishedStories = async (page: number = 1) => {
    try {
      setLoading(true);
      setError(null);
      const result = await getPublishedStories(page);
      setPublishedStories(result.stories);
      setPagination(result.pagination);
    } catch (error) {
      console.error("데이터를 가져오는 중 오류 발생:", error);
      setError('동화를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPublishedStories();
  }, []);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      fetchPublishedStories(newPage);
      // 페이지 변경 시 스크롤을 맨 위로
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const renderPagination = () => {
    if (pagination.total_pages <= 1) return null;

    const pages = [];
    const currentPage = pagination.current_page;
    const totalPages = pagination.total_pages;
    
    // 이전 버튼
    pages.push(
      <button
        key="prev"
        onClick={() => handlePageChange(currentPage - 1)}
        disabled={!pagination.has_previous}
        className={`px-3 py-2 mx-1 rounded-lg transition-colors ${
          pagination.has_previous 
            ? 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300' 
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        이전
      </button>
    );

    // 페이지 번호들
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);

    // 시작 페이지 조정
    if (endPage - startPage < 4 && totalPages > 5) {
      if (currentPage <= 3) {
        endPage = Math.min(totalPages, 5);
      } else if (currentPage >= totalPages - 2) {
        startPage = Math.max(1, totalPages - 4);
      }
    }

    // 첫 페이지와 ... 추가
    if (startPage > 1) {
      pages.push(
        <button
          key={1}
          onClick={() => handlePageChange(1)}
          className="px-3 py-2 mx-1 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300 transition-colors"
        >
          1
        </button>
      );
      if (startPage > 2) {
        pages.push(
          <span key="dots1" className="px-3 py-2 mx-1 text-gray-500">
            ...
          </span>
        );
      }
    }

    // 페이지 번호
    for (let i = startPage; i <= endPage; i++) {
      pages.push(
        <button
          key={i}
          onClick={() => handlePageChange(i)}
          className={`px-3 py-2 mx-1 rounded-lg transition-colors ${
            i === currentPage
              ? 'bg-green-500 text-white'
              : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300'
          }`}
        >
          {i}
        </button>
      );
    }

    // 마지막 페이지와 ... 추가
    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        pages.push(
          <span key="dots2" className="px-3 py-2 mx-1 text-gray-500">
            ...
          </span>
        );
      }
      pages.push(
        <button
          key={totalPages}
          onClick={() => handlePageChange(totalPages)}
          className="px-3 py-2 mx-1 rounded-lg bg-white text-gray-700 hover:bg-gray-100 border border-gray-300 transition-colors"
        >
          {totalPages}
        </button>
      );
    }

    // 다음 버튼
    pages.push(
      <button
        key="next"
        onClick={() => handlePageChange(currentPage + 1)}
        disabled={!pagination.has_next}
        className={`px-3 py-2 mx-1 rounded-lg transition-colors ${
          pagination.has_next 
            ? 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-300' 
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
        }`}
      >
        다음
      </button>
    );

    return (
      <div className="flex justify-center items-center mt-8 flex-wrap">
        {pages}
      </div>
    );
  };

  if (loading) {
    return <Loading />;
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-500 mb-4">{error}</p>
          <button 
            onClick={() => fetchPublishedStories()} 
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="relative min-h-screen bg-cover bg-center bg-no-repeat filter contrast-100"
      style={{ backgroundImage: "url('/images/task3-bg1.jpg')" }}
    >
      <div className="relative z-10 flex min-h-screen bg-white/20">
        <div className="flex-1 pt-16">
          <div className="p-4 sm:p-6 lg:p-8">
            <div className="mb-8 lg:mb-12">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
                모든 어린이를 위한<br />
                공개된 동화책
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mb-6 leading-relaxed">
                다른 작가들이 만든 멋진 동화들을 만나보세요!<br className="hidden sm:block" />
                상상력 가득한 이야기들이 여러분을 기다리고 있습니다.
              </p>
              
              <div className="bg-white/60 rounded-lg p-4 mb-6 inline-block">
                <div className="flex items-center space-x-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{pagination.total_count}</p>
                    <p className="text-sm text-gray-600">공개된 동화</p>
                  </div>
                  
                  {pagination.total_pages > 1 && (
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-600">{pagination.current_page}</p>
                      <p className="text-sm text-gray-600">{pagination.total_pages}페이지 중</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="mb-6 lg:mb-8">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">
                공개된 동화 모음
              </h2>
              
              {publishedStories.length === 0 ? (
                <div className="text-center py-12">
                  <div className="bg-white/60 rounded-lg p-8 inline-block">
                    <p className="text-gray-600 mb-4">아직 공개된 동화가 없습니다.</p>
                    <p className="text-sm text-gray-500 mb-6">첫 번째 공개 동화를 기다려주세요!</p>
                    <a 
                      href="/tasks_1" 
                      className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-block"
                    >
                      나도 동화 만들기
                    </a>
                  </div>
                </div>
              ) : (
                <>
                  <div className="mb-6 flex flex-wrap gap-2">
                    <span className="bg-white/60 px-3 py-1 rounded-full text-sm text-gray-600">
                      총 {pagination.total_count}개의 동화
                    </span>
                    <span className="bg-green-100 px-3 py-1 rounded-full text-sm text-green-700">
                      🌟 모두 공개
                    </span>
                    {pagination.total_pages > 1 && (
                      <span className="bg-purple-100 px-3 py-1 rounded-full text-sm text-purple-700">
                        📄 {pagination.current_page}/{pagination.total_pages} 페이지
                      </span>
                    )}
                  </div>
                  
                  <div className='mainCard_box'>
                    <MainCard posts={publishedStories} />
                  </div>

                  {/* 페이징 컨트롤 */}
                  {renderPagination()}
                </>
              )}
            </div>
            
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExBook;