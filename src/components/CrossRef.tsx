/**
 * CrossRef — inline cross-reference link
 *
 * Renders an anchor link to a target section/figure/table within the site.
 * If the target `id` is not yet resolvable to a known href, it renders
 * the label with a `data-xref-id` attribute so T8 integration can wire
 * it up later by scanning for unresolved refs.
 *
 * The `id` matches slugs registered in the cross-reference registry
 * built by T1 (manifest cross-reference registry).
 *
 * @example
 * // Resolved cross-reference:
 * <CrossRef id="sec-prompt-chaining" label="프롬프트 체이닝" href="/docs/part1/chapter1#prompt-chaining" />
 *
 * @example
 * // Unresolved (href omitted — T8 will wire it):
 * <CrossRef id="img-p51-0" label="그림 3.1" />
 *
 * @example
 * // Figure reference:
 * <CrossRef id="fig-3-1" label="그림 3.1 — 프롬프트 체이닝 흐름도" href="#diagram-img-p51-0" />
 */

import React from 'react';
import styles from './CrossRef.module.css';

export interface CrossRefProps {
  /** Cross-reference registry ID (matches manifest registry slug) */
  id: string;
  /** Human-readable label text */
  label: string;
  /**
   * Resolved href (anchor or path). When omitted, the component renders
   * as a styled span with data-xref-id for T8 post-processing.
   */
  href?: string;
}

export default function CrossRef({ id, label, href }: CrossRefProps): React.ReactElement {
  if (href) {
    return (
      <a
        href={href}
        className={styles.link}
        data-xref-id={id}
      >
        {label}
      </a>
    );
  }

  // Unresolved — T8 integration will replace or wire these
  return (
    <span
      className={styles.unresolved}
      data-xref-id={id}
      title={`교차 참조 미연결: ${id}`}
    >
      {label}
    </span>
  );
}
