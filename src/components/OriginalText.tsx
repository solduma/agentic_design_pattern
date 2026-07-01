/**
 * OriginalText — "원문 펼치기" collapsible original-English block
 *
 * Wraps the original English source text in a `<details>` element
 * so readers can compare it with the Korean translation.
 *
 * @example
 * <OriginalText>
 *   Prompt chaining decomposes a task into a sequence of steps,
 *   where each LLM call processes the output of the previous one.
 * </OriginalText>
 *
 * @example
 * // Custom title:
 * <OriginalText title="Original (English)">
 *   The agent uses tools to interact with external systems.
 * </OriginalText>
 */

import React from 'react';
import styles from './OriginalText.module.css';

export interface OriginalTextProps {
  /** Summary label shown on the collapsed toggle; defaults to "원문 펼치기" */
  title?: string;
  /** The original English content */
  children: React.ReactNode;
}

export default function OriginalText({
  title = '원문 펼치기',
  children,
}: OriginalTextProps): React.ReactElement {
  return (
    <details className={styles.details}>
      <summary className={styles.summary}>
        <span className={styles.icon} aria-hidden="true">📄</span>
        {title}
      </summary>
      <div className={styles.content} lang="en">
        {children}
      </div>
    </details>
  );
}
