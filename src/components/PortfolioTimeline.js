import React from 'react';

const milestones = [
  { year: '2026', title: 'Developed AI-guided Safety Audit Data Pipeline'},
  { year: '2025', title: 'Developed Non-Invasive LLM JetKVM Hardware Interface'},
  { year: '2024', title: 'Developed Custom React/Python account management dashboard'},
  { year: '2024', title: 'Coached 6 remote writers to integrate Langchain LLM Generation Pipeline into daily asynchronous workflow'},
  { year: '2022', title: 'E-commerce Automation And Product Pipeline'},
  { year: '2022', title: '$150k to $600k by developing, launching, and managing ongoing support for a digital course product'},
  { year: '2020', title: 'Developed Web App Infrastructure For 1500+ Active Users'},
  { year: '2019', title: 'Created Enigmatic Man-Relationship Coaching Youtube Channel'},
  { year: '2017', title: 'incaseofcamping.com Blog Startup and Exit'},
  { year: '2017', title: 'Recruited, onboarded, and developed a team of 6 content writers at in-person residency program in Lisbon'},
  { year: '2015', title: '6-Figure Sales Funnels With Wordpress'},
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
