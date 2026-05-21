const fs = require('fs');
const versions = fs.readFileSync('../../version.txt', 'utf8').split('\n');

const baseUrl = process.env.BASE_URL || '/';

/** @type {import('@docusaurus/types').DocusaurusConfig} */
module.exports = {
  future: {
    experimental_faster: true,
  },
  title: 'Fanoni Imaging',
  tagline: 'Clinical imaging platform documentation',
  organizationName: 'Fanoni',
  projectName: 'fanoni-imaging',
  baseUrl,
  baseUrlIssueBanner: false,
  url: 'https://docs.fanoni.ai',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  favicon: 'img/favicon.ico',
  themes: ['@docusaurus/theme-live-codeblock'],
  plugins: [
    'docusaurus-plugin-image-zoom',
    [
      '@docusaurus/plugin-ideal-image',
      {
        quality: 70,
        max: 1030,
        min: 640,
        steps: 2,
      },
    ],
  ],
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          path: 'docs',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: ({ docPath }) =>
            `https://github.com/Fanoni-ai/fanoni-imaging/edit/master/platform/docs/docs/${docPath}`,
          showLastUpdateAuthor: true,
          showLastUpdateTime: true,
          lastVersion: 'current',
          versions: {
            current: {
              label: `${versions[0]} (Latest)`,
            },
          },
        },
        theme: {
          customCss: [require.resolve('./src/css/custom.css')],
        },
      },
    ],
  ],
  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      liveCodeBlock: {
        playgroundPosition: 'bottom',
      },
      docs: {
        sidebar: {
          hideable: true,
          autoCollapseCategories: true,
        },
      },
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
      },
      prism: {
        theme: require('prism-react-renderer').themes.github,
        darkTheme: require('prism-react-renderer').themes.dracula,
        additionalLanguages: ['diff'],
      },
      navbar: {
        hideOnScroll: false,
        logo: {
          alt: 'Fanoni Imaging',
          src: 'img/fanoni-logo-light.svg',
          srcDark: 'img/fanoni-logo.svg',
        },
        items: [
          {
            position: 'left',
            to: '/',
            activeBaseRegex: '^(/next/|/)$',
            label: 'Docs',
          },
          {
            to: '/components',
            label: 'Components',
            position: 'left',
          },
          {
            to: '/help',
            label: 'Help',
            position: 'left',
          },
          {
            href: 'https://imaging.fanoni.ai',
            label: 'Open Viewer',
            target: '_blank',
            position: 'left',
          },
          {
            type: 'docsVersionDropdown',
            position: 'right',
            dropdownActiveClassDisabled: true,
          },
          {
            href: 'https://github.com/Fanoni-ai/fanoni-imaging',
            position: 'right',
            className: 'header-github-link',
            'aria-label': 'GitHub Repository',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Learn',
            items: [
              { label: 'Introduction', to: '/' },
              { label: 'Getting Started', to: 'development/getting-started' },
              { label: 'FAQ', to: '/faq' },
              { label: 'Resources', to: '/resources' },
            ],
          },
          {
            title: 'Platform',
            items: [
              { label: 'Fanoni Imaging Viewer', href: 'https://imaging.fanoni.ai' },
              { label: 'Fanoni EHR', href: 'https://ehr.fanoni.ai' },
            ],
          },
          {
            title: 'More',
            items: [
              { label: 'GitHub', href: 'https://github.com/Fanoni-ai/fanoni-imaging' },
            ],
          },
        ],
        copyright: `Fanoni Imaging is built on OHIF, open source software released under the MIT license.`,
      },
    }),
};
