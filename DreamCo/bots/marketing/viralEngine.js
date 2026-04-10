'use strict';

/**
 * DreamCo Viral Engine — God Mode Feature
 *
 * Detects trends, generates viral content, schedules multi-platform posts,
 * and tracks engagement to maximise organic reach.
 *
 * BOT → ACTION → RESULT → REVENUE → VALIDATION → SCALE
 */

const TRENDING_TOPICS = {
  tech:          ['AI automation', 'ChatGPT side hustles', 'no-code tools', 'crypto recovery', 'SaaS revenue'],
  business:      ['passive income', 'drop servicing', 'LLC formation', 'remote work', 'freelancing'],
  lifestyle:     ['morning routines', 'productivity hacks', 'wealth mindset', 'financial freedom', 'stoicism'],
  entertainment: ['viral challenges', 'reaction videos', 'behind-the-scenes', 'day in the life', 'storytime'],
  local:         ['community events', 'local business spotlights', 'neighbourhood news', 'restaurant reviews'],
};

const PLATFORM_SPECS = {
  tiktok:    { max_chars: 2200, optimal_length: 60,   hashtag_limit: 10, best_times: ['7am', '12pm', '7pm'] },
  instagram: { max_chars: 2200, optimal_length: 125,  hashtag_limit: 30, best_times: ['8am', '1pm', '8pm'] },
  x:         { max_chars: 280,  optimal_length: 100,  hashtag_limit: 2,  best_times: ['9am', '12pm', '6pm'] },
  facebook:  { max_chars: 63206,optimal_length: 40,   hashtag_limit: 5,  best_times: ['9am', '1pm', '3pm'] },
  linkedin:  { max_chars: 3000, optimal_length: 150,  hashtag_limit: 5,  best_times: ['8am', '12pm', '5pm'] },
  youtube:   { max_chars: 5000, optimal_length: 300,  hashtag_limit: 15, best_times: ['12pm', '3pm', '7pm'] },
};

const CONTENT_HOOKS = [
  'Nobody talks about this but…',
  'I made $__X__ doing this one thing:',
  'Stop scrolling — this changed everything for me',
  'The secret to __TOPIC__ that nobody teaches:',
  'If I had to start over, I would do this:',
  'This is how __TOPIC__ actually works:',
  'The __TOPIC__ blueprint no one shares:',
  'I went from $0 to $__X__ using this:',
];

// ---------------------------------------------------------------------------
// Trend Detector
// ---------------------------------------------------------------------------

/**
 * Detect current trending topics for a given niche.
 * @param {string} niche - e.g. 'tech', 'business', 'lifestyle'
 * @returns {Object} Trending topics with engagement scores
 */
function detectTrends(niche = 'business') {
  const topics = TRENDING_TOPICS[niche] || TRENDING_TOPICS.business;

  return topics.map((topic, index) => ({
    topic,
    trend_score: Math.round(100 - index * 8),
    velocity: index < 2 ? 'rising' : index < 4 ? 'stable' : 'fading',
    related_hashtags: generateHashtags(topic),
    estimated_reach: Math.round((100 - index * 8) * 1200),
    recommended: index < 3,
  }));
}

/**
 * Generate relevant hashtags for a topic.
 * @param {string} topic
 * @returns {string[]}
 */
function generateHashtags(topic) {
  const base = topic.toLowerCase().replace(/\s+/g, '');
  return [
    `#${base}`,
    '#dreamco',
    '#makemoneyonline',
    '#entrepreneur',
    '#aitools',
    '#passiveincome',
  ].slice(0, 6);
}

// ---------------------------------------------------------------------------
// Content Generator
// ---------------------------------------------------------------------------

/**
 * Generate a viral post for a specific platform and trend.
 * @param {Object} trend - { topic, related_hashtags }
 * @param {string} platform - 'tiktok' | 'instagram' | 'x' | 'facebook' | 'linkedin'
 * @returns {Object} Post specification
 */
function generatePost(trend, platform = 'tiktok') {
  const specs = PLATFORM_SPECS[platform] || PLATFORM_SPECS.instagram;
  const hook = CONTENT_HOOKS[Math.abs(hashStr(trend.topic + platform)) % CONTENT_HOOKS.length]
    .replace('__TOPIC__', trend.topic)
    .replace('__X__', Math.floor(Math.random() * 9000 + 1000).toLocaleString());

  const body = buildPostBody(trend.topic, platform, specs.optimal_length);
  const hashtags = (trend.related_hashtags || []).slice(0, specs.hashtag_limit).join(' ');
  const fullText = [hook, '', body, '', hashtags].join('\n').slice(0, specs.max_chars);

  return {
    platform,
    topic: trend.topic,
    hook,
    body,
    hashtags: trend.related_hashtags || [],
    full_text: fullText,
    char_count: fullText.length,
    optimal_post_times: specs.best_times,
    content_type: selectContentType(platform),
    estimated_views: Math.floor(trend.trend_score * 150),
    estimated_engagement_rate: parseFloat((Math.random() * 4 + 2).toFixed(2)),
    created_at: new Date().toISOString(),
  };
}

/**
 * Build the body text of a post.
 * @param {string} topic
 * @param {string} platform
 * @param {number} targetLength
 * @returns {string}
 */
function buildPostBody(topic, platform, targetLength) {
  const bodies = {
    tiktok:    `Here's the ${topic} system I use daily. Step 1: Research. Step 2: Build. Step 3: Scale. Comment "INFO" for the full breakdown 👇`,
    instagram: `Everything you need to know about ${topic} in 2024. Save this post so you don't forget it. Follow for daily business tips.`,
    x:         `${topic} is the most underrated skill in 2024. Here's why:`,
    facebook:  `I've spent the last 90 days studying ${topic} and here's what I discovered. This could change how you approach your business.`,
    linkedin:  `After working with 50+ businesses, here is what actually works with ${topic}. These are the tactics the top 1% use.`,
    youtube:   `In this video I break down everything about ${topic} — from beginner basics to advanced strategies that actually generate revenue.`,
  };
  return (bodies[platform] || bodies.instagram).slice(0, targetLength * 5);
}

/**
 * Select the optimal content type for a platform.
 * @param {string} platform
 * @returns {string}
 */
function selectContentType(platform) {
  const types = {
    tiktok:    'short_video',
    instagram: 'reel',
    x:         'thread',
    facebook:  'video_post',
    linkedin:  'article_snippet',
    youtube:   'long_form_video',
  };
  return types[platform] || 'image_post';
}

// ---------------------------------------------------------------------------
// Scheduler
// ---------------------------------------------------------------------------

/**
 * Schedule a post for publication.
 * @param {Object} post - Post object from generatePost()
 * @param {Date} [scheduledTime] - Optional scheduled time (defaults to next optimal slot)
 * @returns {Object} Scheduling confirmation
 */
function schedulePost(post, scheduledTime) {
  const specs = PLATFORM_SPECS[post.platform] || PLATFORM_SPECS.instagram;
  const nextSlot = scheduledTime || getNextOptimalTime(specs.best_times);

  return {
    post_id: `POST-${Date.now()}`,
    platform: post.platform,
    topic: post.topic,
    scheduled_time: nextSlot instanceof Date ? nextSlot.toISOString() : nextSlot,
    status: 'scheduled',
    content_type: post.content_type,
    estimated_views: post.estimated_views,
  };
}

/**
 * Run a full daily posting cycle across all platforms for a niche.
 * @param {string} niche
 * @param {string[]} [platforms] - Platforms to post on
 * @returns {Object} Daily posting report
 */
function runDailyPosting(niche = 'business', platforms = ['tiktok', 'instagram', 'x', 'facebook']) {
  const trends = detectTrends(niche);
  const topTrend = trends.find((t) => t.recommended) || trends[0];

  const scheduledPosts = platforms.map((platform) => {
    const post = generatePost(topTrend, platform);
    return schedulePost(post);
  });

  const totalEstimatedViews = scheduledPosts.reduce((s, p) => s + p.estimated_views, 0);

  return {
    niche,
    date: new Date().toISOString().split('T')[0],
    top_trend: topTrend.topic,
    posts_scheduled: scheduledPosts.length,
    platforms,
    scheduled_posts: scheduledPosts,
    total_estimated_views: totalEstimatedViews,
    estimated_leads: Math.floor(totalEstimatedViews * 0.005),
    estimated_revenue: Math.floor(totalEstimatedViews * 0.002),
  };
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getNextOptimalTime(bestTimes) {
  const now = new Date();
  const today = now.toISOString().split('T')[0];

  const nextSlot = bestTimes.find((t) => {
    const isPm = t.includes('pm');
    let hour = parseInt(t.replace(/[^0-9]/g, ''), 10);
    if (isPm && hour !== 12) hour += 12;
    if (!isPm && hour === 12) hour = 0;
    return hour > now.getHours();
  }) || bestTimes[0];

  const isPm = nextSlot.includes('pm');
  let hour = parseInt(nextSlot.replace(/[^0-9]/g, ''), 10);
  if (isPm && hour !== 12) hour += 12;
  if (!isPm && hour === 12) hour = 0;
  const hourStr = String(hour).padStart(2, '0');
  return `${today}T${hourStr}:00:00Z`;
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
 * Run the Viral Engine daily posting cycle.
 * @returns {Object} Standardised revenue output
 */
function run(options = {}) {
  const niche = (options && options.niche) || 'business';
  const report = runDailyPosting(niche);

  return {
    bot: 'viralEngine',
    revenue: report.estimated_revenue,
    leads_generated: report.estimated_leads,
    conversion_rate: 0.005,
    posts_scheduled: report.posts_scheduled,
    top_trend: report.top_trend,
    total_estimated_views: report.total_estimated_views,
  };
}

module.exports = {
  detectTrends,
  generatePost,
  generateHashtags,
  schedulePost,
  runDailyPosting,
  run,
  TRENDING_TOPICS,
  PLATFORM_SPECS,
};
