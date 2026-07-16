// sidebars.js
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'Introduction',
      label: 'Case Studies - Start Here'
    },
    {
      type: 'category',
      label: 'AI Safety Audit Engine',
      link: {
        type: 'doc',
        id: 'case_study2/AI Safety Audit Engine',
      },
      items: [
        'case_study2/Ingestion First Architecture',
        'case_study2/The Automation Loop',
        'case_study2/Financials and Calculating ROI',
        'case_study2/Future Strategy and Scale',
        'case_study2/Deployment Issues',
      ],
    },
    {
      type: 'category',
      label: 'AI Legacy Hardware Bridge',
      link: {
        type: 'doc',
        id: 'jetkvm_llm/AI Legacy Hardware Bridge',
      },
      items: [
        'jetkvm_llm/The Legacy Software Trap',
        'jetkvm_llm/Non-Invasive Architecture',
        'jetkvm_llm/The Automation Loop',
        'jetkvm_llm/Future Strategy and Scale',
      ],
    },
    {
      type: 'doc',
      id: 'case_study3/AI Legislation Update Agent',
      label: 'AI Legislation Update Agent',
    },
    {
      type: 'doc',
      id: 'case_study4/AI ERP Maintenance Matching Agent',
      label: 'AI ERP Maintenance Matching Agent',
    },
    {
      type: 'doc',
      id: 'case_study5/AI Demographic Localizer',
      label: 'AI Demographic Localizer',
    },
  ],
};

module.exports = sidebars;
