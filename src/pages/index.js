import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import React from 'react';
import PortfolioTimeline from '@site/src/components/PortfolioTimeline';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header 
      style={{
        width: '100%',
        padding: '6rem 0', 
        position: 'relative',
        backgroundImage: `linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7)), url('/img/banner-bg.webp')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center 40%',
        backgroundRepeat: 'no-repeat',
        textAlign: 'center',
      }}
    >
      <div className="container" style={{ position: 'relative', zIndex: 1, maxWidth: '500px', margin: '0 auto', background: 'rgba(0, 0, 0, 0.01)', padding: '2.5rem', borderRadius: '12px', backdropFilter: 'blur(4px)', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
        <h1 style={{ fontSize: '4rem', fontWeight: '800', color: '#ffffff', marginBottom: '2rem', textShadow: '0px 2px 4px rgba(0, 0, 0, 0.5)' }}>
          {siteConfig.title}
        </h1>
        <p style={{ fontSize: '1.7rem', fontWeight: '600', color: '#f3f4f6', maxWidth: '400px', margin: '0 auto', opacity: '0.95', marginBottom: '2rem', textShadow: '0px 2px 4px rgba(0, 0, 0, 0.5)' }}>
          {siteConfig.tagline}
        </p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/Introduction"
            style={{ 
              fontSize: '1.1rem', 
              padding: '0.75rem 2rem',
              backgroundColor: '#1394E6', 
              borderColor: '#60A5FA',
              color: '#ffffff',
              fontWeight: '600'
            }}
          >
            My Case Studies
            <svg style={{ marginLeft: '10px', width: '20px', height: '15px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
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
      title={`Home`}
      description="Jay Pitkänen - I build AI Implementations that solve real world business problems">
      <HomepageHeader />
      <main>
        <section style={{ padding: '4rem 0 2rem 0', textAlign: 'center' }}>
          <div className="container">
            <h2 style={{ fontSize: '2.0rem', maxWidth: '900px', margin: '0 auto', fontWeight: '700', lineHeight: '1.2' }}>
              Secure, Smart and Efficient AI Solutions
            </h2>
          </div>
          <p style={{ fontSize: '1.2rem', color: 'var(--ifm-color-focus)', maxWidth: '800px', margin: '1.5rem auto 0 auto', lineHeight: '1.6', opacity: '0.9' }}>
            Real AI integration goes beyond chatbot wrappers and forced tool adoption.
          </p>
          <p style={{ fontSize: '1.2rem', color: 'var(--ifm-color-focus)', maxWidth: '700px', margin: '1.5rem auto 0 auto', lineHeight: '1.6', opacity: '0.9' }}>
            I design and implement workflow automation systems that turn messy, unstructured business operations into precise, reliable data pipelines. Using cloud AI, local models, or both.
          </p>
          <p style={{ fontSize: '1.2rem', color: 'var(--ifm-color-focus)', maxWidth: '800px', margin: '1.5rem auto 0 auto', lineHeight: '1.6', opacity: '0.9' }}>
            The result: operational delays measured in days become processes measured in minutes, with the compliance and security constraints your industry actually requires.            
          </p>
          <p style={{ fontSize: '1.2rem', color: 'var(--ifm-color-focus)', maxWidth: '800px', margin: '1.5rem auto 0 auto', lineHeight: '1.6', opacity: '0.9' }}>
            AI isn't a panacea. <strong>It's a precision instrument .</strong>
          </p>
        </section>

        <HomepageFeatures />

        <hr style={{ margin: '2rem auto', maxWidth: '80%', opacity: '0.2' }} />

        {/* Section: Why AI Projects Fail */}
        <section style={{ padding: '1rem 0' }}>
          <div className="container" style={{ maxWidth: '800px' }}>
            <Heading as="h2" style={{ marginBottom: '1.5rem', textAlign: 'center', fontSize: '1.8rem' }}>
              How I Actually Work
            </Heading>
            <blockquote style={{ 
              fontSize: '1.1rem', 
              fontStyle: 'normal', 
              borderLeft: '4px solid var(--ifm-color-primary)', 
              padding: '1.5rem', 
              backgroundColor: 'var(--ifm-background-color-neutral)', 
              borderRadius: '4px',
              lineHeight: '1.6'
            }}>
              <p style={{ marginBottom: '1.5rem' }}>
                Most AI projects fail because the solution ignores the reality of the business it's supposed to serve.
              </p>
              <p><strong>My operating rules are simple:</strong></p>
              <ul style={{ paddingLeft: '1.2rem' }}>
                <li style={{ marginBottom: '0.5rem' }}><strong>Work with what exists:</strong> If your solution requires a multi-million dollar software migration, it's a bad solution.</li>
                <li style={{ marginBottom: '0.5rem' }}><strong>Respect the IT department:</strong> Build sandboxed, zero-footprint tools that pass security audits on day one.</li>
                <li><strong>Treat AI as the brain, not the body:</strong> Combine local models with hardware and basic automation to solve hyper-specific problems cleanly.</li>
              </ul>
              <p>The goal isn't to force AI into your business. It's to find where AI removes a real bottleneck - and then build exactly that.</p>
            </blockquote>
          </div>
        </section>

        <hr style={{ margin: '2rem auto', maxWidth: '80%', opacity: '0.2' }} />
          <div className="container" style={{ padding: '1rem 0', maxWidth: '900px' }}>
            <Heading as="h1" style={{ textAlign: 'center', fontSize: '3rem' }}>
              Hi, I'm Jay
            </Heading>
          </div>
        <section style={{ padding: '1rem 0', display: 'flex', justifyContent: 'center' }}>
          <div className="container" style={{ maxWidth: '900px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '3rem', flexWrap: 'wrap' }}>
            <div style={{ flexShrink: 0 }}>
              <img 
                src="/img/headshot.webp" 
                alt="Jay Pitkänen" 
                style={{ width: '350px', height: '350px', borderRadius: '50%', objectFit: 'cover' }} 
              />
            </div>
            <div style={{ textAlign: 'center' }}>
              <p style={{ margin: '0 0 1rem 0', color: '#4b5563' }}>Need help with AI implementation?</p>
              <a href="https://www.linkedin.com/in/jaypitkanen/" style={{ fontSize: '1.1rem', fontWeight: '600', color: '#3B82F6', textDecoration: 'none' }}>
<img src="/img/LI-In-Bug.png" alt="LinkedIn" style={{ width: '24px', height: '24px' }} />
              Connect With Me on LinkedIn &rarr;
              </a>
            </div>
          </div>
        </section>

        <section style={{ padding: '1rem 0' }}>
          <div className="container" style={{ maxWidth: '800px' }}>
            <Heading as="h2" style={{ marginBottom: '1.5rem', textAlign: 'center', fontSize: '1.8rem' }}>
              I Solve Your AI Implementation Problems
            </Heading>
            <blockquote style={{
              fontSize: '1.1rem',
              fontStyle: 'normal',
              borderLeft: '4px solid var(--ifm-color-primary)',
              padding: '1.5rem',
              backgroundColor: 'var(--ifm-background-color-neutral)',
              borderRadius: '4px',
              lineHeight: '1.6'
            }}>
              <p><strong>Not sure what to call what you need?</strong></p>
              <p>That's fine. Here's how other people have described it:</p>
              <ul style={{ paddingLeft: '1.2rem' }}>
                <li style={{ marginBottom: '0.5rem' }}><strong>"We need someone to figure out what to build"</strong> I map the workflow, identify the friction points, choose the right stack, and prove the concept before you spend a dollar on scaling.</li>
                <li style={{ marginBottom: '0.5rem' }}><strong>"We need someone to make the business case"</strong> I translate operational bottlenecks into ROI projections and build the case for AI automation in language your CFO and IT department can both act on.</li>
                <li><strong>"We need someone who can speak engineer"</strong> I think in business value and user outcomes, but I can hand a developer a blueprint they can actually build from.</li>
              </ul>
              <p>The goal isn't to force AI into your business. It's to find where AI removes a real bottleneck - and then build exactly that.</p>
            </blockquote>
          </div>
          <div className={styles.buttons}>
          <Link
          className="button button--secondary button--lg"
          to="/docs/Introduction"
          style={{
            fontSize: '1.1rem',
          padding: '0.75rem 2rem',
          backgroundColor: '#1394E6',
          borderColor: '#60A5FA',
          color: '#ffffff',
          fontWeight: '600'
          }}
          >
          My Case Studies
          <svg style={{ marginLeft: '10px', width: '20px', height: '15px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
          </Link>
          </div>
        </section>

        {/* Section: Who is Jay? */}
        <section style={{ marginTop: '2rem' }}>
          <div className="container" style={{ maxWidth: '800px' }}>
            <Heading as="h2" style={{ marginBottom: '1.5rem', textAlign: 'center', fontSize: '1.8rem' }}>
              Career Milestones and Highlights
            </Heading>
              <p style={{ marginBottom: '1rem' }}>
                I'm a marketer, product designer, builder, and creator. My brain has never been very good at the whole "stick to the status quo, don't rock the boat, get a traditional career"-sort of thing. 
              </p>
              <p style={{ marginBottom: '1rem' }}>
                When I wanted to study SEO and blogging, Aalto University didn't even recognize the concept of <strong> "content marketing." </strong> I eventually realized I wasn't built for a university degree, even if one existed to suit me. No, the marketing tech was out there, and I needed to find it.
              </p>
              <p style={{ marginBottom: '1rem' }}>
                It took a few years, but eventually I found my people: <strong> Dreamers. Shapers. Singers. Makers. </strong>
              </p>
              <p style={{ marginBottom: '1rem' }}>
                And we've done some amazing stuff together.
              </p>
              <p style={{ marginBottom: '1rem' }}>
                My professional career is hardly traditional, but I pride myself on my record of using emerging cutting edge tech to create clever solutions to complex business problems.
              </p>
              <p style={{ marginBottom: '0rem' }}>
                Here are some of my major achievements over the years:
              </p>
          </div>
         <div className="container" style={{ maxWidth: '900px' }}>
          <PortfolioTimeline />
         </div>

         <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/Introduction"
            style={{ 
              fontSize: '1.1rem', 
              padding: '0.75rem 2rem',
              backgroundColor: '#1394E6', 
              borderColor: '#60A5FA',
              color: '#ffffff',
              fontWeight: '600',
              marginBottom: '5rem'
            }}
          >
            My Case Studies
            <svg style={{ marginLeft: '10px', width: '20px', height: '15px' }} fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          </Link>
         </div>
        </section>
      </main>
    </Layout>
  );
}
