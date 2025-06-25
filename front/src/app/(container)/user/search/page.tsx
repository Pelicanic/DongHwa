'use client';

import { useEffect, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiClient, API_ROUTES } from '@/lib/api';
import MainCard from '@/(components)/Card/Cardbox';
import { storyDTO } from '@/lib/type/story';
import Loading from '@/(components)/Loading/loading';
import { requireLogin } from '@/lib/utils/auth';
import { Search, BookOpen, Library } from 'lucide-react';

interface PaginationInfo {
  current_page: number;
  page_size: number;
  total_count: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

const searchStories = async (query: string, page: number = 1): Promise<{stories: storyDTO[], pagination: PaginationInfo, search_query: string}> => {
  try {
    const res = await apiClient.post(API_ROUTES.SEARCH_STORIES, {
      query: query,
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
      },
      search_query: res.data.search_query || query
    };
  } catch (error) {
    console.error("동화 검색 중 오류 발생:", error);
    throw error;
  }
};

const SearchPage: React.FC = () => {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get('q') || '';
  
  const [stories, setStories] = useState<storyDTO[]>([]);
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
  const [currentSearchQuery, setCurrentSearchQuery] = useState(searchQuery);
  const [inputValue, setInputValue] = useState(searchQuery);

  // 로그인 확인
  useEffect(() => {
    requireLogin();
  }, []);

  const performSearch = async (query: string, page: number = 1) => {
    if (!query.trim()) {
      setError('검색어를 입력해주세요.');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await searchStories(query, page);
      setStories(result.stories);
      setPagination(result.pagination);
      setCurrentSearchQuery(result.search_query);
    } catch (error) {
      console.error("검색 중 오류 발생:", error);
      setError('검색 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // URL 파라미터 변경 시 검색 실행
  useEffect(() => {
    if (searchQuery) {
      setInputValue(searchQuery);
      performSearch(searchQuery);
    } else {
      setLoading(false);
    }
  }, [searchQuery]);

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= pagination.total_pages) {
      performSearch(currentSearchQuery, newPage);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const query = inputValue.trim();
    if (query) {
      // URL 업데이트
      window.history.pushState({}, '', `/user/search?q=${encodeURIComponent(query)}`);
      performSearch(query);
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
              ? 'bg-orange-500 text-white'
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

  // 카테고리별 결과 분석
  const categorizeResults = () => {
    const published = stories.filter(story => story.status === 'published');
    const completed = stories.filter(story => story.status === 'completed');
    return { published, completed };
  };

  const { published, completed } = categorizeResults();

  return (
    <div
      className="relative min-h-screen bg-cover bg-center bg-no-repeat filter contrast-100"
      style={{ backgroundImage: "url('/images/main-bg4.jpg')" }}
    >
      <div className="relative z-10 flex min-h-screen bg-white/20">
        <div className="flex-1 pt-16">
          <div className="p-4 sm:p-6 lg:p-8">
            {/* 검색 헤더 */}
            <div className="mb-8 lg:mb-12">
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-gray-900 mb-4 leading-tight">
                동화 검색
              </h1>
              <p className="text-sm sm:text-base text-gray-600 mb-6 leading-relaxed">
                제목이나 작성자 이름으로 원하는 동화를 찾아보세요!<br className="hidden sm:block" />
                공개된 동화와 완성된 동화에서 검색합니다.
              </p>

              {/* 검색 폼 */}
              <form onSubmit={handleSearch} className="mb-6">
                <div className="relative max-w-2xl">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="동화 제목이나 작성자 이름을 입력하세요..."
                    className="w-full pl-12 pr-20 py-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-lg bg-white/80 backdrop-blur-sm"
                  />
                  <button
                    type="submit"
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-orange-500 hover:bg-orange-600 text-white px-6 py-2 rounded-lg font-medium transition-colors"
                  >
                    검색
                  </button>
                </div>
              </form>

              {/* 검색 결과 요약 */}
              {currentSearchQuery && !loading && (
                <div className="bg-white/60 rounded-lg p-4 mb-6 inline-block">
                  <div className="flex items-center space-x-4 flex-wrap gap-2">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-orange-600">{pagination.total_count}</p>
                      <p className="text-sm text-gray-600">검색 결과</p>
                    </div>
                    
                    {published.length > 0 && (
                      <div className="text-center">
                        <p className="text-lg font-bold text-green-600">{published.length}</p>
                        <p className="text-xs text-gray-600">공개 동화</p>
                      </div>
                    )}
                    
                    {completed.length > 0 && (
                      <div className="text-center">
                        <p className="text-lg font-bold text-blue-600">{completed.length}</p>
                        <p className="text-xs text-gray-600">완성 동화</p>
                      </div>
                    )}
                    
                    {pagination.total_pages > 1 && (
                      <div className="text-center">
                        <p className="text-lg font-bold text-purple-600">{pagination.current_page}</p>
                        <p className="text-xs text-gray-600">{pagination.total_pages}페이지 중</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* 검색 결과 */}
            <div className="mb-6 lg:mb-8">
              {loading ? (
                <Loading />
              ) : error ? (
                <div className="text-center py-12">
                  <div className="bg-white/60 rounded-lg p-8 inline-block">
                    <p className="text-red-500 mb-4">{error}</p>
                    <button 
                      onClick={() => currentSearchQuery && performSearch(currentSearchQuery)} 
                      className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600"
                    >
                      다시 시도
                    </button>
                  </div>
                </div>
              ) : !currentSearchQuery ? (
                <div className="text-center py-12">
                  <div className="bg-white/60 rounded-lg p-8 inline-block">
                    <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">검색어를 입력하여 동화를 찾아보세요!</p>
                    <p className="text-sm text-gray-500 mb-6">제목이나 작성자 이름으로 검색할 수 있습니다.</p>
                    <div className="flex justify-center space-x-4">
                      <a 
                        href="/user/exbook" 
                        className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-flex items-center"
                      >
                        <BookOpen className="w-5 h-5 mr-2" />
                        공개 동화 보기
                      </a>
                      <a 
                        href="/user/libbook" 
                        className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-flex items-center"
                      >
                        <Library className="w-5 h-5 mr-2" />
                        완성 동화 보기
                      </a>
                    </div>
                  </div>
                </div>
              ) : stories.length === 0 ? (
                <div className="text-center py-12">
                  <div className="bg-white/60 rounded-lg p-8 inline-block">
                    <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600 mb-4">
                      '<span className="font-semibold text-orange-600">{currentSearchQuery}</span>' 에 대한 검색 결과가 없습니다.
                    </p>
                    <p className="text-sm text-gray-500 mb-6">다른 검색어로 시도해보세요.</p>
                    <div className="flex justify-center space-x-4">
                      <a 
                        href="/user/exbook" 
                        className="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-flex items-center"
                      >
                        <BookOpen className="w-5 h-5 mr-2" />
                        모든 공개 동화 보기
                      </a>
                      <a 
                        href="/user/libbook" 
                        className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg font-medium transition-colors inline-flex items-center"
                      >
                        <Library className="w-5 h-5 mr-2" />
                        모든 완성 동화 보기
                      </a>
                    </div>
                  </div>
                </div>
              ) : (
                <>
                  <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4">
                    '<span className="text-orange-600">{currentSearchQuery}</span>' 검색 결과
                  </h2>
                  
                  <div className="mb-6 flex flex-wrap gap-2">
                    <span className="bg-white/60 px-3 py-1 rounded-full text-sm text-gray-600">
                      총 {pagination.total_count}개의 동화
                    </span>
                    {published.length > 0 && (
                      <span className="bg-green-100 px-3 py-1 rounded-full text-sm text-green-700">
                        🌟 공개 동화 {published.length}개
                      </span>
                    )}
                    {completed.length > 0 && (
                      <span className="bg-blue-100 px-3 py-1 rounded-full text-sm text-blue-700">
                        ✅ 완성 동화 {completed.length}개
                      </span>
                    )}
                    {pagination.total_pages > 1 && (
                      <span className="bg-purple-100 px-3 py-1 rounded-full text-sm text-purple-700">
                        📄 {pagination.current_page}/{pagination.total_pages} 페이지
                      </span>
                    )}
                  </div>
                  
                  <div className='mainCard_box'>
                    <MainCard posts={stories} />
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

export default SearchPage;