import React, {useEffect, useRef} from 'react';
import Layout from '@theme/Layout';

/**
 * Pagefind search page.
 * Pagefind index is generated post-build by `pagefind --site build` (see package.json build script).
 * The UI is loaded at runtime from /pagefind/pagefind-ui.js produced by the build step.
 */
export default function SearchPage() {
  const searchContainerRef = useRef(null);

  useEffect(() => {
    // Load pagefind UI script dynamically (only exists in production build)
    const script = document.createElement('script');
    script.src = '/pagefind/pagefind-ui.js';
    script.onload = () => {
      if (window.PagefindUI && searchContainerRef.current) {
        new window.PagefindUI({
          element: searchContainerRef.current,
          showSubResults: true,
          translations: {
            placeholder: '한국어로 검색...',
            zero_results: '[QUERY] 에 대한 결과가 없습니다.',
          },
        });
      }
    };
    document.body.appendChild(script);

    // Load pagefind UI styles
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = '/pagefind/pagefind-ui.css';
    document.head.appendChild(link);

    return () => {
      document.body.removeChild(script);
      document.head.removeChild(link);
    };
  }, []);

  return (
    <Layout title="검색" description="문서 전체 검색">
      <div className="container margin-top--lg margin-bottom--xl">
        <h1>검색</h1>
        <p>
          한국어 키워드로 전체 문서를 검색할 수 있습니다.
          원서의 색인(Index) 대신 이 검색 기능을 이용하십시오.
        </p>
        <div ref={searchContainerRef} id="pagefind-search" />
      </div>
    </Layout>
  );
}
