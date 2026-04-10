'use strict';

/**
 * DreamCo Auto Client Hunter — God Mode Feature
 *
 * AI-driven system that scrapes potential client info, scores leads,
 * and automatically generates and sends outreach proposals.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const BUSINESS_NICHES = [
  'restaurants', 'law firms', 'dental offices', 'real estate agents',
  'auto dealers', 'gyms', 'beauty salons', 'contractors', 'accountants',
  'insurance agents', 'mortgage brokers', 'e-commerce stores', 'startups',
];

const OUTREACH_CHANNELS = ['email', 'linkedin', 'sms', 'facebook_dm', 'instagram_dm'];

const PAIN_POINTS = {
  restaurants:       ['not enough reservations', 'no online ordering system', 'weak social media presence'],
  'law firms':       ['slow client intake', 'no automated follow-up', 'poor website SEO'],
  'dental offices':  ['appointment no-shows', 'no automated reminders', 'no online booking'],
  'real estate agents': ['not enough leads', 'slow CRM', 'no automated drip campaigns'],
  startups:          ['no marketing strategy', 'no sales funnel', 'no lead generation system'],
  default:           ['low visibility', 'manual processes', 'no automation', 'wasted ad spend'],
};

const PROPOSAL_TEMPLATES = {
  email: (lead, offer) => `
Subject: Quick question about ${lead.business_name}

Hi ${lead.contact_name || 'there'},

I noticed ${lead.business_name} could benefit from ${offer}.

We've helped similar businesses in ${lead.niche} increase revenue by 30-150% using AI automation.

Would you be open to a 15-minute call this week to explore this?

Best,
DreamCo AI Team
  `.trim(),

  linkedin: (lead, offer) => `
Hi ${lead.contact_name || 'there'} 👋

I came across ${lead.business_name} and was impressed by what you've built.

I help ${lead.niche} businesses like yours with ${offer}. Typically see results in the first 30 days.

Mind if I share a quick case study?
  `.trim(),

  sms: (lead, offer) => `Hi ${lead.contact_name || 'there'}, this is DreamCo AI — we help ${lead.niche} businesses automate ${offer}. Free audit this week? Reply YES`.trim(),
};

// ---------------------------------------------------------------------------
// Lead Scraper (simulated)
// ---------------------------------------------------------------------------

/**
 * Scrape and score potential client leads in a niche.
 * @param {string} niche - Business niche to target
 * @param {number} [count=10] - Number of leads to generate
 * @param {string} [location='United States'] - Target location
 * @returns {Object[]} Scored lead objects
 */
function huntLeads(niche = 'restaurants', count = 10, location = 'United States') {
  const leads = [];

  for (let i = 0; i < count; i++) {
    const lead = generateLead(niche, location, i);
    leads.push(lead);
  }

  // Sort by lead score descending
  leads.sort((a, b) => b.lead_score - a.lead_score);

  return {
    niche,
    location,
    total_found: leads.length,
    qualified: leads.filter((l) => l.lead_score >= 70).length,
    leads,
    hunt_timestamp: new Date().toISOString(),
  };
}

/**
 * Generate a single lead object.
 * @param {string} niche
 * @param {string} location
 * @param {number} index
 * @returns {Object}
 */
function generateLead(niche, location, index) {
  const names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Wilson', 'Moore'];
  const businessSuffixes = ['LLC', 'Inc', 'Co', 'Group', 'Solutions', 'Services', 'Agency', 'Studio'];
  const firstName = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'David', 'Barbara'];

  const lastName = names[index % names.length];
  const fName = firstName[index % firstName.length];
  const suffix = businessSuffixes[index % businessSuffixes.length];
  const businessName = `${lastName} ${niche.charAt(0).toUpperCase() + niche.slice(1).replace(/s$/, '')} ${suffix}`;
  const score = Math.min(100, 50 + Math.floor(Math.abs(hashStr(businessName)) % 50));

  const painPoints = PAIN_POINTS[niche] || PAIN_POINTS.default;

  return {
    lead_id: `LEAD-${Date.now()}-${index}`,
    business_name: businessName,
    contact_name: `${fName} ${lastName}`,
    email: `${fName.toLowerCase()}.${lastName.toLowerCase()}@${businessName.toLowerCase().replace(/\s+/g, '')}.com`,
    phone: `+1-${600 + index}-555-${1000 + index * 7}`,
    niche,
    location,
    website: `https://www.${businessName.toLowerCase().replace(/\s+/g, '')}.com`,
    lead_score: score,
    quality: score >= 80 ? 'hot' : score >= 65 ? 'warm' : 'cold',
    pain_points: painPoints.slice(0, 2),
    social_profiles: {
      linkedin: `linkedin.com/in/${fName.toLowerCase()}-${lastName.toLowerCase()}`,
      instagram: `@${fName.toLowerCase()}${lastName.toLowerCase()}`,
    },
    best_outreach_channel: OUTREACH_CHANNELS[index % OUTREACH_CHANNELS.length],
    discovered_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Proposal Generator
// ---------------------------------------------------------------------------

/**
 * Generate a personalised outreach proposal for a lead.
 * @param {Object} lead - Lead object from huntLeads()
 * @param {string} [service='AI business automation'] - Service to offer
 * @returns {Object} Proposal object with content for each channel
 */
function generateProposal(lead, service = 'AI business automation') {
  const channel = lead.best_outreach_channel || 'email';
  const template = PROPOSAL_TEMPLATES[channel] || PROPOSAL_TEMPLATES.email;

  return {
    proposal_id: `PROP-${Date.now()}`,
    lead_id: lead.lead_id,
    business_name: lead.business_name,
    contact_name: lead.contact_name,
    channel,
    service_offered: service,
    content: template(lead, service),
    pain_points_addressed: lead.pain_points || [],
    estimated_value_usd: estimateDealValue(lead),
    follow_up_sequence: buildFollowUpSequence(lead, service),
    created_at: new Date().toISOString(),
  };
}

/**
 * Simulate sending an outreach proposal.
 * @param {Object} lead
 * @param {Object} proposal
 * @returns {Object} Send confirmation
 */
function sendOutreach(lead, proposal) {
  const delivered = lead.lead_score >= 50; // Simulate delivery based on quality

  return {
    outreach_id: `OUT-${Date.now()}`,
    proposal_id: proposal.proposal_id,
    lead_id: lead.lead_id,
    channel: proposal.channel,
    status: delivered ? 'sent' : 'bounced',
    delivered,
    open_probability: delivered ? parseFloat((lead.lead_score / 100 * 0.4).toFixed(2)) : 0,
    response_probability: delivered ? parseFloat((lead.lead_score / 100 * 0.15).toFixed(2)) : 0,
    sent_at: new Date().toISOString(),
    follow_up_at: new Date(Date.now() + 3 * 86400000).toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Estimate the potential deal value for a lead.
 * @param {Object} lead
 * @returns {number}
 */
function estimateDealValue(lead) {
  const baseValues = {
    hot:  5000,
    warm: 2000,
    cold: 500,
  };
  return baseValues[lead.quality] || 1000;
}

/**
 * Build a follow-up email sequence.
 * @param {Object} lead
 * @param {string} service
 * @returns {Object[]}
 */
function buildFollowUpSequence(lead, service) {
  return [
    { day: 3,  message: `Following up on my message about ${service} for ${lead.business_name}` },
    { day: 7,  message: `Quick case study — how we helped a similar ${lead.niche} business grow 40%` },
    { day: 14, message: `Last check-in — free audit offer expires soon for ${lead.business_name}` },
  ];
}

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
 * Run the Auto Client Hunter with a default niche scan.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  const niche = (options && options.niche) || 'startups';
  const count = (options && options.count) || 15;

  const huntResult = huntLeads(niche, count);
  const qualifiedLeads = huntResult.leads.filter((l) => l.lead_score >= 65);
  const proposals = qualifiedLeads.slice(0, 5).map((l) => generateProposal(l));
  const outreaches = proposals.map((p, i) => sendOutreach(huntResult.leads[i], p));
  const sentCount = outreaches.filter((o) => o.delivered).length;

  return {
    bot: 'autoClientHunter',
    revenue: sentCount * 500,
    leads_generated: huntResult.qualified,
    conversion_rate: parseFloat((sentCount / count).toFixed(2)),
    proposals_sent: sentCount,
    top_niche: niche,
  };
}

module.exports = {
  huntLeads,
  generateLead,
  generateProposal,
  sendOutreach,
  estimateDealValue,
  buildFollowUpSequence,
  run,
  BUSINESS_NICHES,
  OUTREACH_CHANNELS,
  PAIN_POINTS,
};
