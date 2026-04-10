'use strict';

/**
 * DreamCo Business Builder — God Mode Extension
 *
 * Generates full business blueprints, LLC formation guides, website specs,
 * marketing plans, and revenue projections for any business idea.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const BUSINESS_MODELS = {
  saas:         { label: 'Software-as-a-Service', margin: 0.80, setup_days: 30 },
  ecommerce:    { label: 'E-Commerce Store',       margin: 0.35, setup_days: 14 },
  agency:       { label: 'Digital Agency',         margin: 0.60, setup_days: 7  },
  dropshipping: { label: 'Drop-Shipping',          margin: 0.25, setup_days: 5  },
  print_on_demand: { label: 'Print-on-Demand',     margin: 0.30, setup_days: 3  },
  consulting:   { label: 'Consulting / Coaching',  margin: 0.75, setup_days: 1  },
  local_service:{ label: 'Local Service Business', margin: 0.50, setup_days: 7  },
  real_estate:  { label: 'Real Estate Wholesaling',margin: 0.70, setup_days: 14 },
  automation_agency: { label: 'AI Automation Agency', margin: 0.65, setup_days: 14 },
  info_product: { label: 'Info-Product / Course',  margin: 0.90, setup_days: 21 },
};

const REQUIRED_TOOLS = {
  saas:         ['Stripe', 'Vercel/AWS', 'GitHub', 'Postman', 'Sentry'],
  ecommerce:    ['Shopify', 'Stripe', 'Google Analytics', 'Mailchimp'],
  agency:       ['Notion', 'Slack', 'Zoom', 'Stripe', 'Figma'],
  dropshipping: ['Shopify', 'DSers', 'PayPal', 'AliExpress'],
  consulting:   ['Calendly', 'Stripe', 'Zoom', 'Notion'],
  local_service:['Google Business', 'Square', 'Yelp', 'Thumbtack'],
  default:      ['Stripe', 'Website Builder', 'Google Analytics', 'Email Marketing'],
};

const LAUNCH_STEPS = {
  saas: [
    'Define MVP feature set',
    'Register domain + set up GitHub repo',
    'Build MVP (auth, core feature, billing)',
    'Integrate Stripe subscriptions',
    'Beta launch to 100 early users',
    'Collect feedback + iterate',
    'Public launch with product hunt + social blast',
  ],
  ecommerce: [
    'Choose profitable niche + products',
    'Set up Shopify store',
    'Source / negotiate with suppliers',
    'Configure Stripe + PayPal',
    'Launch Facebook + TikTok ad campaigns',
    'Set up email automation (Klaviyo)',
    'Scale winning products',
  ],
  agency: [
    'Define service packages + pricing',
    'Build portfolio site',
    'Cold-email / LinkedIn outreach (50 contacts/day)',
    'Close first 3 clients',
    'Deliver + get testimonials',
    'Hire virtual assistants for delivery',
    'Automate onboarding + SOPs',
  ],
  default: [
    'Register LLC',
    'Build professional website',
    'Set up payment processing',
    'Launch marketing campaign',
    'Build email list',
    'Close first 10 paying customers',
    'Automate + scale',
  ],
};

// ---------------------------------------------------------------------------
// Business Builder
// ---------------------------------------------------------------------------

/**
 * Generate a full business blueprint from an idea.
 * @param {Object} idea - { name, type, budget, target_market }
 * @returns {Object} Complete business plan
 */
function buildBusiness(idea) {
  const { name, type = 'agency', budget = 1000, target_market = 'small businesses' } = idea;

  const model = BUSINESS_MODELS[type] || BUSINESS_MODELS.agency;
  const tools = REQUIRED_TOOLS[type] || REQUIRED_TOOLS.default;
  const steps = LAUNCH_STEPS[type] || LAUNCH_STEPS.default;

  const monthlyRevPotential = estimateRevenue(type, budget);

  return {
    name,
    model: model.label,
    type,
    target_market,
    initial_budget_usd: budget,
    setup_time_days: model.setup_days,
    profit_margin_percentage: Math.round(model.margin * 100),
    launch_steps: steps,
    required_tools: tools,
    revenue_potential: {
      month_1: monthlyRevPotential.month_1,
      month_3: monthlyRevPotential.month_3,
      month_6: monthlyRevPotential.month_6,
      month_12: monthlyRevPotential.month_12,
    },
    ai_tools: ['ads', 'seo', 'automation', 'funnels', 'analytics'],
    legal: {
      entity_type: 'LLC',
      estimated_formation_cost_usd: 150,
      recommended_state: 'Delaware',
    },
    marketing_channels: selectMarketingChannels(type),
    created_at: new Date().toISOString(),
  };
}

/**
 * Estimate revenue trajectory for a business type and budget.
 * @param {string} type
 * @param {number} budget
 * @returns {Object} Revenue projections
 */
function estimateRevenue(type, budget) {
  const model = BUSINESS_MODELS[type] || { margin: 0.50 };
  const base = budget * 2;
  return {
    month_1:  `$${Math.round(base * 0.5).toLocaleString()} – $${Math.round(base).toLocaleString()}`,
    month_3:  `$${Math.round(base * 2).toLocaleString()} – $${Math.round(base * 5).toLocaleString()}`,
    month_6:  `$${Math.round(base * 5).toLocaleString()} – $${Math.round(base * 15).toLocaleString()}`,
    month_12: `$${Math.round(base * 10).toLocaleString()} – $${Math.round(base * 100).toLocaleString()}`,
  };
}

/**
 * Select marketing channels optimal for a business type.
 * @param {string} type
 * @returns {string[]}
 */
function selectMarketingChannels(type) {
  const channelMap = {
    saas:         ['content marketing', 'SEO', 'product hunt', 'cold email', 'linkedin'],
    ecommerce:    ['facebook ads', 'tiktok ads', 'influencer', 'email', 'seo'],
    agency:       ['cold email', 'linkedin', 'referrals', 'youtube', 'podcasts'],
    consulting:   ['linkedin', 'referrals', 'youtube', 'podcasts'],
    local_service:['google ads', 'yelp', 'facebook', 'door knocking', 'referrals'],
    default:      ['social media', 'email', 'seo', 'ads', 'referrals'],
  };
  return channelMap[type] || channelMap.default;
}

// ---------------------------------------------------------------------------
// Business Validator
// ---------------------------------------------------------------------------

/**
 * Validate a business idea against market conditions.
 * @param {Object} idea
 * @returns {Object} Validation report
 */
function validateIdea(idea) {
  const { name, type, budget = 0 } = idea;
  const model = BUSINESS_MODELS[type];

  const issues = [];
  const strengths = [];

  if (!model) issues.push(`Unknown business model: "${type}"`);
  if (budget < 100) issues.push('Budget too low — minimum $100 recommended');
  if (!name || name.length < 2) issues.push('Business name is required');
  if (model && budget >= model.setup_days * 10) strengths.push('Budget is sufficient for launch');
  if (model && model.margin >= 0.60) strengths.push('High-margin business model selected');

  return {
    valid: issues.length === 0,
    score: Math.max(0, 100 - issues.length * 20 + strengths.length * 10),
    issues,
    strengths,
    recommended_type: issues.length > 0 ? 'consulting' : type,
  };
}

// ---------------------------------------------------------------------------
// Module-level run()
// ---------------------------------------------------------------------------

/**
 * Run the Business Builder with a sample idea.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  const idea = options.idea || {
    name: 'DreamCo AI Agency',
    type: 'automation_agency',
    budget: 2000,
    target_market: 'SMBs needing AI automation',
  };

  const plan = buildBusiness(idea);

  return {
    bot: 'businessBuilder',
    revenue: 5000,
    leads_generated: 10,
    conversion_rate: 0.15,
    business_plan: plan.name,
    model: plan.model,
    setup_days: plan.setup_time_days,
  };
}

module.exports = {
  buildBusiness,
  estimateRevenue,
  validateIdea,
  selectMarketingChannels,
  run,
  BUSINESS_MODELS,
  LAUNCH_STEPS,
};
