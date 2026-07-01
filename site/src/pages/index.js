import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <Heading as="h1" className="hero__title">
          {siteConfig.title}
        </Heading>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            문서 보기
          </Link>
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="LLM 기반 에이전트 설계 패턴 한국어 문서">
      <HomepageHeader />
      <main>
        <section className="container margin-top--lg margin-bottom--xl">
          <div className="row">
            <div className="col col--8 col--offset-2">
              <p>
                이 사이트는 에이전트 설계 패턴(Agentic Design Patterns)의 한국어 문서입니다.
                LLM 기반 에이전트 시스템을 설계할 때 반복적으로 나타나는 구조적 해결책을 담고 있습니다.
              </p>
            </div>
          </div>
        </section>
      </main>
    </Layout>
  );
}
