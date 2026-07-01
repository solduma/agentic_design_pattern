/**
 * KeyPoints — "이 장의 핵심" chapter-top callout
 *
 * Renders a styled callout box at the top of a chapter listing
 * the key takeaways. Accepts either a `items` prop (string array)
 * or child elements for custom content.
 *
 * @example
 * // With items prop:
 * <KeyPoints items={["에이전트는 도구를 호출합니다", "RAG는 검색을 강화합니다"]} />
 *
 * @example
 * // With children:
 * <KeyPoints>
 *   <ul>
 *     <li>에이전트는 도구를 호출합니다</li>
 *     <li>RAG는 검색을 강화합니다</li>
 *   </ul>
 * </KeyPoints>
 */

import React from 'react';
import styles from './KeyPoints.module.css';

export interface KeyPointsProps {
  /** Array of key point strings to render as a list */
  items?: string[];
  /** Optional heading text; defaults to "이 장의 핵심" */
  title?: string;
  /** Custom children content — used when `items` is not provided */
  children?: React.ReactNode;
}

export default function KeyPoints({
  items,
  title = '이 장의 핵심',
  children,
}: KeyPointsProps): React.ReactElement {
  return (
    <div className={styles.keyPoints}>
      <div className={styles.header}>
        <span className={styles.icon} aria-hidden="true">💡</span>
        <strong className={styles.title}>{title}</strong>
      </div>
      <div className={styles.body}>
        {items && items.length > 0 ? (
          <ul className={styles.list}>
            {items.map((item, idx) => (
              <li key={idx} className={styles.item}>{item}</li>
            ))}
          </ul>
        ) : (
          children
        )}
      </div>
    </div>
  );
}
