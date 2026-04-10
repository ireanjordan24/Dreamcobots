'use strict';

/**
 * DreamCo Auto Closer — God Mode Feature
 *
 * Automates deal negotiation, client booking, and contract generation
 * via an AI-driven chat interface.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const NEGOTIATION_STAGES = ['discovery', 'proposal', 'objection_handling', 'pricing', 'closing', 'closed', 'lost'];

const OBJECTION_RESPONSES = {
  'too expensive': [
    'I understand budget is a concern. We offer flexible payment plans and a ROI guarantee.',
    'Our average client sees 3x ROI in the first 90 days — let me show you the numbers.',
    'We can start with a smaller pilot package to prove value first.',
  ],
  'not interested': [
    'Totally fair! Can I ask — is it the timing, or a specific concern about the service?',
    'I hear you. What would need to be true for you to consider this in 3 months?',
    'No problem at all. Can I send a quick case study in case your situation changes?',
  ],
  'need to think': [
    'Of course! What specific questions can I answer to help you decide?',
    'Absolutely — what information would be most helpful for your decision?',
    'I understand. Is there a specific concern I can address right now?',
  ],
  'already have solution': [
    'Great! What are you currently using? I\'d love to understand how we compare.',
    'That\'s helpful to know. Many of our clients switched from similar solutions — mind if I share why?',
    'Completely understand. Are you happy with the results you\'re getting?',
  ],
  default: [
    'That\'s a great point — let me address that directly.',
    'I appreciate your candour. Here\'s how we\'ve handled that for other clients:',
    'Totally valid concern. Let me walk you through how we solve that.',
  ],
};

const CLOSING_SCRIPTS = {
  summary_close:      'Based on everything we\'ve discussed, it sounds like [SERVICE] is a perfect fit for [BUSINESS]. Shall we get started today?',
  urgency_close:      'We have a limited-time launch offer that expires at end of week. I\'d hate for you to miss out — can we lock in your spot now?',
  assumptive_close:   'I\'ll send over the contract and we can kick off onboarding by [DATE]. Does that work for you?',
  alternative_close:  'Would you prefer to start with the Starter package at $[PRICE_LOW]/mo, or go straight to Pro at $[PRICE_HIGH]/mo?',
};

// ---------------------------------------------------------------------------
// Negotiation Engine
// ---------------------------------------------------------------------------

/**
 * Start a new negotiation session with a lead.
 * @param {Object} lead - Lead object { lead_id, business_name, contact_name, niche }
 * @param {string} [service='AI automation package']
 * @returns {Object} Deal record (negotiation session)
 */
function startNegotiation(lead, service = 'AI automation package') {
  return {
    deal_id: `DEAL-${Date.now()}`,
    lead_id: lead.lead_id,
    business_name: lead.business_name,
    contact_name: lead.contact_name || 'Client',
    service,
    stage: 'discovery',
    proposed_price_usd: estimatePrice(lead),
    agreed_price_usd: null,
    messages: [
      {
        role: 'agent',
        content: `Hi ${lead.contact_name || 'there'}! Thanks for taking the time to chat. I'd love to learn more about ${lead.business_name} and see how we can help. What's your biggest challenge right now?`,
        timestamp: new Date().toISOString(),
      },
    ],
    objections_raised: [],
    objections_handled: 0,
    started_at: new Date().toISOString(),
    closed_at: null,
    status: 'open',
  };
}

/**
 * Process a client message and generate the next AI response.
 * @param {Object} deal - Deal record from startNegotiation()
 * @param {string} userMessage - Client's latest message
 * @returns {Object} Updated deal record with new AI response
 */
function negotiate(deal, userMessage) {
  const updatedDeal = { ...deal, messages: [...deal.messages] };

  // Add user message
  updatedDeal.messages.push({
    role: 'client',
    content: userMessage,
    timestamp: new Date().toISOString(),
  });

  // Detect stage and generate response
  const { response, newStage } = generateNegotiationResponse(userMessage, deal.stage, deal);

  updatedDeal.messages.push({
    role: 'agent',
    content: response,
    timestamp: new Date().toISOString(),
  });

  updatedDeal.stage = newStage;

  // Track objections
  const objection = detectObjection(userMessage);
  if (objection) {
    updatedDeal.objections_raised = [...(deal.objections_raised || []), objection];
    updatedDeal.objections_handled = (deal.objections_handled || 0) + 1;
  }

  return updatedDeal;
}

/**
 * Close a deal and generate a booking confirmation.
 * @param {Object} deal
 * @returns {Object} Updated deal with closed status
 */
function closeDeal(deal) {
  return {
    ...deal,
    stage: 'closed',
    status: 'won',
    agreed_price_usd: deal.proposed_price_usd,
    closed_at: new Date().toISOString(),
    messages: [
      ...deal.messages,
      {
        role: 'agent',
        content: `Excellent! 🎉 We're thrilled to welcome ${deal.business_name} to DreamCo. I'm sending the contract now — please sign within 24 hours to secure your spot. Looking forward to delivering amazing results!`,
        timestamp: new Date().toISOString(),
      },
    ],
  };
}

/**
 * Book a client after a deal is closed.
 * @param {Object} deal
 * @returns {Object} Booking confirmation
 */
function bookClient(deal) {
  const onboardingDate = new Date(Date.now() + 2 * 86400000).toISOString().split('T')[0];

  return {
    booking_id: `BOOK-${Date.now()}`,
    deal_id: deal.deal_id,
    business_name: deal.business_name,
    contact_name: deal.contact_name,
    service: deal.service,
    price_usd: deal.agreed_price_usd || deal.proposed_price_usd,
    onboarding_date: onboardingDate,
    kickoff_call: `${onboardingDate}T14:00:00Z`,
    contract_sent: true,
    status: 'booked',
    booked_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Estimate the service price for a lead.
 * @param {Object} lead
 * @returns {number}
 */
function estimatePrice(lead) {
  const basePrices = { hot: 2500, warm: 1500, cold: 500 };
  return basePrices[lead && lead.quality] || 1000;
}

/**
 * Detect objections in a client message.
 * @param {string} message
 * @returns {string|null}
 */
function detectObjection(message) {
  const lower = message.toLowerCase();
  if (lower.includes('expensive') || lower.includes('price') || lower.includes('cost')) return 'too expensive';
  if (lower.includes('not interested') || lower.includes('no thanks')) return 'not interested';
  if (lower.includes('think') || lower.includes('consider') || lower.includes('later')) return 'need to think';
  if (lower.includes('already') || lower.includes('have a solution') || lower.includes('using')) return 'already have solution';
  return null;
}

/**
 * Generate the next negotiation response and stage.
 * @param {string} userMessage
 * @param {string} currentStage
 * @param {Object} deal
 * @returns {{ response: string, newStage: string }}
 */
function generateNegotiationResponse(userMessage, currentStage, deal) {
  const objection = detectObjection(userMessage);
  const lower = userMessage.toLowerCase();

  if (objection) {
    const responses = OBJECTION_RESPONSES[objection] || OBJECTION_RESPONSES.default;
    return {
      response: responses[Math.abs(hashStr(userMessage)) % responses.length],
      newStage: 'objection_handling',
    };
  }

  if (lower.includes('yes') || lower.includes('sounds good') || lower.includes('let\'s do it') || lower.includes("let's do")) {
    const stageIdx = NEGOTIATION_STAGES.indexOf(currentStage);
    const nextStage = NEGOTIATION_STAGES[Math.min(stageIdx + 1, NEGOTIATION_STAGES.length - 3)];

    if (nextStage === 'pricing') {
      return {
        response: CLOSING_SCRIPTS.alternative_close
          .replace('[PRICE_LOW]', deal.proposed_price_usd * 0.6)
          .replace('[PRICE_HIGH]', deal.proposed_price_usd),
        newStage: 'pricing',
      };
    }

    if (nextStage === 'closing') {
      return {
        response: CLOSING_SCRIPTS.assumptive_close
          .replace('[DATE]', new Date(Date.now() + 2 * 86400000).toISOString().split('T')[0]),
        newStage: 'closing',
      };
    }

    return {
      response: `Great! The next step is to go over our ${deal.service} package in detail. Can I walk you through the deliverables?`,
      newStage: nextStage,
    };
  }

  const stageResponses = {
    discovery: `Tell me more about that. How long has that been a challenge for ${deal.business_name}?`,
    proposal:  `Based on what you've shared, I think our ${deal.service} would be perfect. Here's what's included: [custom deliverables based on your needs]. Does that align with what you're looking for?`,
    pricing:   `Our investment starts at $${deal.proposed_price_usd}/month with a 90-day ROI guarantee. How does that fit your budget?`,
    closing:   CLOSING_SCRIPTS.summary_close.replace('[SERVICE]', deal.service).replace('[BUSINESS]', deal.business_name),
  };

  return {
    response: stageResponses[currentStage] || `I appreciate you sharing that. Let me make sure I fully understand your situation before we move forward.`,
    newStage: currentStage,
  };
}

function hashStr(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

// ---------------------------------------------------------------------------
// Module-level run()
// ---------------------------------------------------------------------------

/**
 * Run the Auto Closer with a sample negotiation.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  const lead = (options && options.lead) || {
    lead_id: 'LEAD-SAMPLE',
    business_name: 'Sample Startup LLC',
    contact_name: 'Alex',
    quality: 'hot',
    niche: 'startups',
  };

  let deal = startNegotiation(lead);
  deal = negotiate(deal, "Yes, we definitely need help with our marketing automation.");
  deal = negotiate(deal, "How much does this cost?");
  deal = negotiate(deal, "Sounds good, let's move forward.");
  const booking = bookClient(closeDeal(deal));

  return {
    bot: 'autoCloser',
    revenue: booking.price_usd,
    leads_generated: 1,
    conversion_rate: 0.25,
    deal_id: deal.deal_id,
    booking_id: booking.booking_id,
    stage: 'closed',
  };
}

module.exports = {
  startNegotiation,
  negotiate,
  closeDeal,
  bookClient,
  estimatePrice,
  detectObjection,
  run,
  NEGOTIATION_STAGES,
  OBJECTION_RESPONSES,
  CLOSING_SCRIPTS,
};
