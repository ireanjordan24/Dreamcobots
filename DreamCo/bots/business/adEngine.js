'use strict';

/**
 * DreamCo Ad Engine — God Mode Extension
 *
 * Generates multi-platform ad campaigns, estimates reach, calculates ROI,
 * and tracks performance for the DreamCo Money Operating System.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const AD_PLATFORMS = ['facebook', 'tiktok', 'instagram', 'google', 'youtube', 'x', 'linkedin'];

const AD_FORMATS = {
  facebook:   ['carousel', 'video', 'single_image', 'stories'],
  tiktok:     ['in_feed', 'branded_hashtag', 'topview'],
  instagram:  ['reels', 'stories', 'feed', 'explore'],
  google:     ['search', 'display', 'shopping', 'performance_max'],
  youtube:    ['skippable', 'non_skippable', 'bumper', 'masthead'],
  x:          ['promoted_tweet', 'promoted_trend', 'promoted_account'],
  linkedin:   ['sponsored_content', 'message_ads', 'dynamic_ads'],
};

const BUDGET_TIERS = {
  starter:    { min: 5,   max: 50,   label: 'Starter'    },
  growth:     { min: 50,  max: 500,  label: 'Growth'     },
  scale:      { min: 500, max: 5000, label: 'Scale'      },
  enterprise: { min: 5000, max: 50000, label: 'Enterprise' },
};

const CPM_BENCHMARKS = {
  facebook:  7.5,
  tiktok:    3.5,
  instagram: 8.0,
  google:    12.0,
  youtube:   9.5,
  x:         6.0,
  linkedin:  28.0,
};

// ---------------------------------------------------------------------------
// Ad Generator
// ---------------------------------------------------------------------------

/**
 * Generate a multi-platform ad campaign for a business.
 * @param {Object} business - Business info { name, offer, niche, budget }
 * @returns {Object} Campaign specification with headlines, targeting, and reach
 */
function generateAd(business) {
  const { name, offer, niche = 'general', budget = 100 } = business;

  const platforms = selectOptimalPlatforms(niche, budget);
  const campaigns = platforms.map((platform) => buildCampaign(platform, name, offer, budget));
  const totalReach = campaigns.reduce((sum, c) => sum + c.estimated_reach, 0);
  const expectedRevenue = Math.floor(totalReach * 0.002 * (budget / 100));

  return {
    business_name: name,
    niche,
    budget_usd: budget,
    platforms,
    campaigns,
    total_estimated_reach: totalReach,
    expected_revenue_usd: expectedRevenue,
    roi_percentage: budget > 0 ? Math.round(((expectedRevenue - budget) / budget) * 100) : 0,
    created_at: new Date().toISOString(),
  };
}

/**
 * Select the best platforms based on niche and budget.
 * @param {string} niche
 * @param {number} budget
 * @returns {string[]} Ordered platform list
 */
function selectOptimalPlatforms(niche, budget) {
  const nicheMap = {
    ecommerce:   ['facebook', 'instagram', 'google', 'tiktok'],
    b2b:         ['linkedin', 'google', 'x', 'youtube'],
    entertainment: ['tiktok', 'youtube', 'instagram', 'x'],
    local:       ['facebook', 'google', 'instagram'],
    saas:        ['google', 'linkedin', 'x', 'youtube'],
    general:     ['facebook', 'google', 'instagram', 'tiktok'],
  };

  const base = nicheMap[niche] || nicheMap.general;

  if (budget < BUDGET_TIERS.growth.min) return base.slice(0, 2);
  if (budget < BUDGET_TIERS.scale.min)  return base.slice(0, 3);
  return base;
}

/**
 * Build a single-platform campaign specification.
 * @param {string} platform
 * @param {string} businessName
 * @param {string} offer
 * @param {number} totalBudget
 * @returns {Object}
 */
function buildCampaign(platform, businessName, offer, totalBudget) {
  const formats = AD_FORMATS[platform] || ['standard'];
  const format = formats[Math.floor(Math.abs(hashStr(offer + platform)) % formats.length)];
  const cpm = CPM_BENCHMARKS[platform] || 8.0;
  const platformBudget = Math.round(totalBudget / 2);
  const impressions = Math.floor((platformBudget / cpm) * 1000);

  return {
    platform,
    format,
    headline: `${businessName} — ${offer}`,
    description: `Discover ${offer} before it ends. Trusted by thousands.`,
    call_to_action: 'Shop Now',
    budget_usd: platformBudget,
    cpm_usd: cpm,
    estimated_impressions: impressions,
    estimated_reach: Math.floor(impressions * 0.7),
    estimated_clicks: Math.floor(impressions * 0.025),
    estimated_conversions: Math.floor(impressions * 0.003),
  };
}

// ---------------------------------------------------------------------------
// ROI Analyser
// ---------------------------------------------------------------------------

/**
 * Analyse past campaign performance and generate optimisation recommendations.
 * @param {Object} campaign - Campaign with actual metrics
 * @returns {Object} Analysis and recommendations
 */
function analysePerformance(campaign) {
  const { spend = 0, revenue = 0, clicks = 0, impressions = 0, conversions = 0 } = campaign;

  const roi = spend > 0 ? ((revenue - spend) / spend) * 100 : 0;
  const ctr = impressions > 0 ? (clicks / impressions) * 100 : 0;
  const cvr = clicks > 0 ? (conversions / clicks) * 100 : 0;
  const cpc = clicks > 0 ? spend / clicks : 0;
  const cpa = conversions > 0 ? spend / conversions : 0;

  const recommendations = [];
  if (roi < 100) recommendations.push('Increase bid on top-performing ad sets');
  if (ctr < 1.5) recommendations.push('A/B test new creative assets');
  if (cvr < 2.0) recommendations.push('Optimise landing page copy and CTA');
  if (cpc > 2.0)  recommendations.push('Refine audience targeting to reduce CPC');

  return {
    roi_percentage: Math.round(roi),
    ctr_percentage: Math.round(ctr * 100) / 100,
    cvr_percentage: Math.round(cvr * 100) / 100,
    cpc_usd: Math.round(cpc * 100) / 100,
    cpa_usd: Math.round(cpa * 100) / 100,
    performance_grade: roi >= 200 ? 'A' : roi >= 100 ? 'B' : roi >= 50 ? 'C' : 'D',
    recommendations,
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function hashStr(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}

// ---------------------------------------------------------------------------
// Module-level run()
// ---------------------------------------------------------------------------

/**
 * Run the Ad Engine with a sample campaign.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  const business = options.business || {
    name: 'DreamCo',
    offer: 'AI-powered business automation',
    niche: 'saas',
    budget: 250,
  };

  const campaign = generateAd(business);

  return {
    bot: 'adEngine',
    revenue: campaign.expected_revenue_usd,
    leads_generated: campaign.campaigns.reduce((s, c) => s + c.estimated_conversions, 0),
    conversion_rate: 0.3,
    campaign_id: `AD-${Date.now()}`,
    platforms_activated: campaign.platforms,
    total_reach: campaign.total_estimated_reach,
  };
}

module.exports = {
  generateAd,
  analysePerformance,
  selectOptimalPlatforms,
  buildCampaign,
  run,
  AD_PLATFORMS,
  AD_FORMATS,
  CPM_BENCHMARKS,
};
