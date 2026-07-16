import React from 'react';

const milestones = [
  { year: '2026', title: 'Non-Invasive LLM JetKVM Hardware Interface'},
  { year: '2025', title: 'Stable Diffusion Forge - Consistent Image Avatar'}, 
  { year: '2024', title: 'Local Chat LLM - Governance and Character Bible' },
  { year: '2023', title: 'Langchain LLM Generation Pipeline For Human-Like SEO Content' },
  { year: '2021', title: 'E-commerce Automation And Product Pipeline' },
  { year: '2020', title: 'Web App Infrastructure For 1500+ Active Users' },
  { year: '2019', title: 'Enigmatic Man-Relationship Coaching Youtube Channel' },
  { year: '2017', title: 'incaseofcamping.com Blog Startup and Exit' },
  { year: '2015', title: '6-Figure Sales Funnels With Wordpress' },
];

export default function PortfolioTimeline() {
  return (
    <div className="container">
      <div className="custom-timeline">
        {milestones.map((item, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-marker"></div>
            <div className="timeline-content">
              <div className="timeline-year">{item.year}</div>
              <div className="timeline-title">{item.title}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
