// @ts-check

// Sidebar for "The New SDLC With Vibe Coding" (Google, May 2026).
// Section order follows the paper's top-level headings (manifest section order).

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  sdlcSidebar: [
    {
      type: 'doc',
      id: 'intro',
      label: '소개',
    },
    {
      type: 'category',
      label: '본문',
      collapsed: false,
      items: [
        { type: 'doc', id: 'introduction' },
        { type: 'doc', id: 'syntax-to-intent' },
        { type: 'doc', id: 'context-engineering' },
        { type: 'doc', id: 'new-sdlc' },
        { type: 'doc', id: 'harness-engineering' },
        { type: 'doc', id: 'developer-role' },
        { type: 'doc', id: 'coding-agents' },
        { type: 'doc', id: 'economics' },
        { type: 'doc', id: 'where-to-start' },
        { type: 'doc', id: 'conclusion' },
      ],
    },
    {
      type: 'category',
      label: '참고',
      items: [
        { type: 'doc', id: 'endnotes' },
      ],
    },
  ],
};

export default sidebars;
