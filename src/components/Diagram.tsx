/**
 * Diagram — image/Mermaid wrapper keyed by manifest image ID
 *
 * Renders a figure element with a Korean caption. When `src` is provided,
 * it displays the image (PNG/SVG). Without `src`, it renders a labeled
 * placeholder showing the `id` for later wiring by T8 integration.
 *
 * ID format: `img-p{page}-{idx}` (e.g., `img-p51-0`)
 *
 * @example
 * // With image src:
 * <Diagram
 *   id="img-p51-0"
 *   src="/img/diagrams/img-p51-0.png"
 *   caption="그림 3.1 — 프롬프트 체이닝 흐름도"
 *   alt="프롬프트 체이닝: 단계별 LLM 호출 다이어그램"
 * />
 *
 * @example
 * // Placeholder (src not yet wired by T8):
 * <Diagram id="img-p51-0" caption="그림 3.1 — 프롬프트 체이닝 흐름도" />
 *
 * @example
 * // Mermaid slot (render a Mermaid diagram as children):
 * <Diagram id="img-p51-0" caption="그림 3.1 — 시퀀스 다이어그램">
 *   {`graph LR\n  A --> B`}
 * </Diagram>
 */

import React from 'react';
import styles from './Diagram.module.css';

export interface DiagramProps {
  /** Globally unique manifest image ID (e.g., "img-p51-0") */
  id: string;
  /** Image URL (PNG/SVG). If omitted, renders a placeholder with the id. */
  src?: string;
  /** Korean caption shown below the image/diagram */
  caption?: string;
  /** Accessible alt text for the image */
  alt?: string;
  /** Children can be used to pass a Mermaid diagram component or custom content */
  children?: React.ReactNode;
}

export default function Diagram({
  id,
  src,
  caption,
  alt,
  children,
}: DiagramProps): React.ReactElement {
  const content = (() => {
    if (children) {
      return <div className={styles.mermaidSlot}>{children}</div>;
    }
    if (src) {
      return (
        <img
          src={src}
          alt={alt || caption || id}
          className={styles.image}
          loading="lazy"
        />
      );
    }
    // Placeholder for T8 integration
    return (
      <div className={styles.placeholder} aria-label={`다이어그램 플레이스홀더: ${id}`}>
        <span className={styles.placeholderIcon} aria-hidden="true">🖼</span>
        <code className={styles.placeholderId}>{id}</code>
        <span className={styles.placeholderHint}>다이어그램 에셋 연결 대기 중</span>
      </div>
    );
  })();

  return (
    <figure
      className={styles.figure}
      data-diagram-id={id}
      id={`diagram-${id}`}
    >
      {content}
      {caption && (
        <figcaption className={styles.caption}>{caption}</figcaption>
      )}
    </figure>
  );
}
