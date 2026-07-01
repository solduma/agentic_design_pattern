/**
 * ChapterNav — previous/next chapter navigation cards
 *
 * Renders a two-column navigation bar at the bottom of a chapter
 * with prev/next links displayed as cards. Either `prev` or `next`
 * (or both) can be omitted.
 *
 * @example
 * <ChapterNav
 *   prev={{ title: "1장 — 프롬프트 체이닝", href: "/docs/part1/chapter1" }}
 *   next={{ title: "3장 — 라우팅", href: "/docs/part1/chapter3" }}
 * />
 *
 * @example
 * // First chapter — no prev:
 * <ChapterNav next={{ title: "2장 — 병렬화", href: "/docs/part1/chapter2" }} />
 *
 * @example
 * // Last chapter — no next:
 * <ChapterNav prev={{ title: "20장 — 탐색", href: "/docs/part4/chapter20" }} />
 */

import React from 'react';
import styles from './ChapterNav.module.css';

export interface ChapterNavItem {
  /** Chapter/section title displayed on the card */
  title: string;
  /** Navigation href */
  href: string;
}

export interface ChapterNavProps {
  /** Previous chapter link */
  prev?: ChapterNavItem;
  /** Next chapter link */
  next?: ChapterNavItem;
}

export default function ChapterNav({ prev, next }: ChapterNavProps): React.ReactElement {
  return (
    <nav className={styles.nav} aria-label="챕터 이동">
      <div className={styles.side}>
        {prev ? (
          <a href={prev.href} className={`${styles.card} ${styles.prevCard}`}>
            <span className={styles.direction} aria-hidden="true">◀</span>
            <span className={styles.cardContent}>
              <span className={styles.label}>이전 챕터</span>
              <span className={styles.title}>{prev.title}</span>
            </span>
          </a>
        ) : (
          <span className={styles.empty} />
        )}
      </div>

      <div className={`${styles.side} ${styles.sideRight}`}>
        {next ? (
          <a href={next.href} className={`${styles.card} ${styles.nextCard}`}>
            <span className={styles.cardContent}>
              <span className={styles.label}>다음 챕터</span>
              <span className={styles.title}>{next.title}</span>
            </span>
            <span className={styles.direction} aria-hidden="true">▶</span>
          </a>
        ) : (
          <span className={styles.empty} />
        )}
      </div>
    </nav>
  );
}
