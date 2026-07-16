import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'The Goal',
    imgSrc: 'img/hunting-ai.jpeg',
    description: (
      <>
        No AI hype. Just ROI. I don't build tech for the sake of tech. I find the exact friction points in your business and deploy AI to erase them.
      </>
    ),
  },
  {
    title: 'The Method',
    imgSrc: 'img/prototype.jpeg',
    description: (
      <>
        I design for reality. I build lightweight, rapid prototypes to prove a concept works before asking a company to spend a single dollar on scaling it.
      </>
    ),
  },
  {
    title: 'The Grind',
    imgSrc: 'img/sisyphus.jpeg',
    description: (
      <>
        I don't just talk strategy. I bring receipts. Check out the <a href="/docs/Introduction">Case Studies</a> to see exactly how my AI solutions fit into real-world operational constraints.
      </>
    ),
  },
];

function Feature({Svg, imgSrc, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        {Svg ? (
          <Svg className={styles.featureSvg} role="img" />
        ) : (
          <img 
            src={imgSrc} 
            className={styles.featureSvg} 
            alt={title} 
            style={{ width: '300px', height: '200px', objectFit: 'contain' }}
          />
        )} 
     </div>
      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
