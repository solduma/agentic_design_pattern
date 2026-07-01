/**
 * Site component exports for @site/src/components
 *
 * KeyPoints, OriginalText, ChapterNav — presentational
 * Diagram, CrossRef — stubs (actual content rewritten into MDX by integrate_site.py)
 */
import React from 'react';

/**
 * KeyPoints — renders a highlighted bullet list of key takeaways.
 */
export function KeyPoints({ items = [] }) {
  if (!items || items.length === 0) return null;
  return (
    <div className="key-points admonition admonition-tip alert alert--success">
      <div className="admonition-heading">
        <h5>핵심 포인트</h5>
      </div>
      <div className="admonition-content">
        <ul>
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

/**
 * OriginalText — shows the original English excerpt in a collapsible block.
 */
export function OriginalText({ children }) {
  if (!children) return null;
  return (
    <details className="original-text">
      <summary>원문 (Original Text)</summary>
      <div style={{ fontStyle: 'italic', color: 'var(--ifm-color-content-secondary)' }}>
        {children}
      </div>
    </details>
  );
}

/**
 * ChapterNav — renders prev/next chapter navigation links.
 */
export function ChapterNav({ prev, next }) {
  return (
    <nav className="chapter-nav" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem', paddingTop: '1rem', borderTop: '1px solid var(--ifm-color-emphasis-300)' }}>
      <div>
        {prev && (
          <a href={prev.href}>← {prev.label}</a>
        )}
      </div>
      <div>
        {next && (
          <a href={next.href}>{next.label} →</a>
        )}
      </div>
    </nav>
  );
}

/**
 * Diagram — stub component.
 * Actual diagram content is inlined into MDX files by integrate_site.py.
 * This stub exists so that any remaining <Diagram /> calls don't crash.
 */
export function Diagram({ id }) {
  if (!id) return null;
  return (
    <figure>
      <figcaption>다이어그램 {id} (준비 중)</figcaption>
    </figure>
  );
}

/**
 * CrossRef — stub component.
 * Actual cross-references are rewritten by integrate_site.py.
 * This stub exists so that any remaining <CrossRef /> calls don't crash.
 */
export function CrossRef({ id, label }) {
  const display = label || id || '';
  return <span>{display}</span>;
}
