// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).

import {themes as prismThemes} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Agentic Design Patterns',
  tagline: '한국어 에이전트 설계 패턴 문서',
  favicon: 'img/favicon.ico',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'https://solduma.github.io',
  baseUrl: '/agentic_design_pattern/',

  organizationName: 'solduma',
  projectName: 'agentic_design_pattern',

  onBrokenLinks: 'throw',

  // Single Korean locale — NOT a multi-locale translation pipeline.
  // Using i18n solely to set htmlLang="ko" for correct CJK rendering.
  i18n: {
    defaultLocale: 'ko',
    locales: ['ko'],
  },

  // Mermaid support (first-party Docusaurus theme)
  markdown: {
    mermaid: true,
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  themes: ['@docusaurus/theme-mermaid'],

  // Second documentation set: "The New SDLC With Vibe Coding" (Google, May 2026).
  // Separate docs instance — its own sidebar, terms, and /sdlc/ route — sharing
  // one build and one Pagefind search index with the Agentic Design Patterns docs.
  plugins: [
    [
      '@docusaurus/plugin-content-docs',
      {
        id: 'sdlc',
        path: 'sdlc-docs',
        routeBasePath: 'sdlc',
        sidebarPath: './sidebars-sdlc.js',
        editUrl:
          'https://github.com/solduma/agentic_design_pattern/tree/main/site/',
      },
    ],
  ],

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/solduma/agentic_design_pattern/tree/main/site/',
          routeBasePath: 'docs',
        },
        blog: false, // Blog not needed for this documentation site
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: 'img/docusaurus-social-card.jpg',

      // Light/dark toggle enabled (default in classic theme)
      colorMode: {
        defaultMode: 'light',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },

      navbar: {
        title: 'Agentic Design Patterns',
        logo: {
          alt: 'Agentic Design Patterns Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'mainSidebar',
            position: 'left',
            label: '에이전트 설계 패턴',
          },
          {
            type: 'docSidebar',
            sidebarId: 'sdlcSidebar',
            docsPluginId: 'sdlc',
            position: 'left',
            label: 'The New SDLC',
          },
          {
            to: '/search',
            label: '검색',
            position: 'right',
          },
          {
            href: 'https://github.com/solduma/agentic_design_pattern',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },

      footer: {
        style: 'dark',
        links: [
          {
            title: '문서',
            items: [
              {
                label: '소개',
                to: '/docs/intro',
              },
            ],
          },
          {
            title: '더 보기',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/solduma/agentic_design_pattern',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Agentic Design Patterns. Docusaurus로 제작.`,
      },

      // Code highlighting: Prism (Docusaurus default, no Shiki).
      // Binding decision recorded in CONTRIBUTING.md.
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'json', 'yaml'],
      },

      // Mermaid diagram font — Noto Sans KR for Korean label rendering (no tofu □)
      mermaid: {
        theme: {light: 'neutral', dark: 'dark'},
        options: {
          fontFamily: "'Noto Sans KR', sans-serif",
        },
      },
    }),
};

export default config;
