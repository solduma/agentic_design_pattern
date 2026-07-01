// @ts-check

// Explicit sidebar structure based on manifest section order.

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  mainSidebar: [
    // Landing page
    {
      type: 'doc',
      id: 'intro',
      label: '소개',
    },
    // 전면부
    {
      type: 'category',
      label: '전면부',
      items: [
        { type: 'doc', id: 'intro/foreword' },
        { type: 'doc', id: 'intro/preface' },
        { type: 'doc', id: 'intro/frameworks-intro' },
      ],
    },
    // Part 1
    {
      type: 'category',
      label: 'Part 1: 기본 패턴',
      items: [
        { type: 'doc', id: 'part1/ch01' },
        { type: 'doc', id: 'part1/ch02' },
        { type: 'doc', id: 'part1/ch03' },
        { type: 'doc', id: 'part1/ch04' },
        { type: 'doc', id: 'part1/ch05' },
        { type: 'doc', id: 'part1/ch06' },
        { type: 'doc', id: 'part1/ch07' },
      ],
    },
    // Part 2
    {
      type: 'category',
      label: 'Part 2: 학습 및 적응',
      items: [
        { type: 'doc', id: 'part2/ch08' },
        { type: 'doc', id: 'part2/ch09' },
      ],
    },
    // Part 3
    {
      type: 'category',
      label: 'Part 3: 고급 제어',
      items: [
        { type: 'doc', id: 'part3/ch10' },
        { type: 'doc', id: 'part3/ch11' },
        { type: 'doc', id: 'part3/ch12' },
        { type: 'doc', id: 'part3/ch13' },
      ],
    },
    // Part 4
    {
      type: 'category',
      label: 'Part 4: 심화 패턴',
      items: [
        { type: 'doc', id: 'part4/ch14' },
        { type: 'doc', id: 'part4/ch15' },
        { type: 'doc', id: 'part4/ch16' },
        { type: 'doc', id: 'part4/ch17' },
        { type: 'doc', id: 'part4/ch18' },
        { type: 'doc', id: 'part4/ch19' },
        { type: 'doc', id: 'part4/ch20' },
        { type: 'doc', id: 'part4/ch21' },
      ],
    },
    // 부록
    {
      type: 'category',
      label: '부록',
      items: [
        { type: 'doc', id: 'appendix/appendix-a' },
        { type: 'doc', id: 'appendix/appendix-b' },
        { type: 'doc', id: 'appendix/appendix-c' },
        { type: 'doc', id: 'appendix/appendix-d' },
        { type: 'doc', id: 'appendix/appendix-e' },
        { type: 'doc', id: 'appendix/appendix-f' },
        { type: 'doc', id: 'appendix/appendix-g' },
      ],
    },
    // 후면부
    {
      type: 'category',
      label: '후면부',
      items: [
        { type: 'doc', id: 'back/conclusion' },
        { type: 'doc', id: 'back/faq' },
        { type: 'doc', id: 'back/gemini-transcript' },
        { type: 'doc', id: 'back/glossary' },
      ],
    },
  ],
};

export default sidebars;
