'use strict';

/**
 * DreamCo Firebase Schemas
 *
 * Plain-object schema definitions for all Firestore collections used by the
 * DreamCo Money Operating System.  Import these in Firebase initialisation
 * code and validation helpers.
 */

const dealSchema = {
  collection: 'deals',
  fields: {
    deal_id: 'string',
    title: 'string',
    store: 'string',
    category: 'string',
    original_price: 'number',
    sale_price: 'number',
    savings: 'number',
    savings_pct: 'number',
    coupon_code: 'string',
    cashback_pct: 'number',
    affiliate_commission: 'number',
    created_at: 'timestamp',
    user_id: 'string',
    status: 'string',
  },
  indexes: ['store', 'category', 'created_at', 'user_id', 'status'],
  requiredFields: ['deal_id', 'title', 'store', 'sale_price'],
};

const flipSchema = {
  collection: 'flips',
  fields: {
    flip_id: 'string',
    name: 'string',
    source: 'string',
    category: 'string',
    buy_price: 'number',
    estimated_sell_price: 'number',
    profit: 'number',
    profit_pct: 'number',
    location: 'string',
    condition: 'string',
    status: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['source', 'category', 'location', 'created_at', 'user_id'],
  requiredFields: ['flip_id', 'name', 'buy_price', 'estimated_sell_price'],
};

const pennyDealSchema = {
  collection: 'pennyDeals',
  fields: {
    penny_id: 'string',
    name: 'string',
    store: 'string',
    clearance_price: 'number',
    resale_value: 'number',
    profit: 'number',
    profit_pct: 'number',
    sku: 'string',
    status: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['store', 'created_at', 'user_id', 'status'],
  requiredFields: ['penny_id', 'name', 'store', 'clearance_price', 'resale_value'],
};

const receiptSchema = {
  collection: 'receipts',
  fields: {
    receipt_id: 'string',
    store: 'string',
    purchase_amount: 'number',
    total_cashback: 'number',
    cashback_apps: 'array',
    status: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['store', 'created_at', 'user_id', 'status'],
  requiredFields: ['receipt_id', 'store', 'purchase_amount'],
};

const legalPayoutSchema = {
  collection: 'legalPayouts',
  fields: {
    payout_id: 'string',
    case_name: 'string',
    payout_type: 'string',
    amount: 'number',
    deadline: 'timestamp',
    status: 'string',
    source_url: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['payout_type', 'deadline', 'status', 'created_at', 'user_id'],
  requiredFields: ['payout_id', 'case_name', 'amount', 'deadline'],
};

const grantSchema = {
  collection: 'grants',
  fields: {
    grant_id: 'string',
    name: 'string',
    amount: 'number',
    category: 'string',
    eligibility: 'string',
    deadline: 'timestamp',
    application_cost: 'number',
    net_profit: 'number',
    status: 'string',
    source_url: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['category', 'deadline', 'status', 'created_at', 'user_id'],
  requiredFields: ['grant_id', 'name', 'amount', 'deadline'],
};

const fiverrGigSchema = {
  collection: 'fiverrGigs',
  fields: {
    gig_id: 'string',
    title: 'string',
    category: 'string',
    price: 'number',
    delivery_days: 'number',
    platform: 'string',
    orders_completed: 'number',
    revenue: 'number',
    status: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['category', 'platform', 'created_at', 'user_id', 'status'],
  requiredFields: ['gig_id', 'title', 'price', 'platform'],
};

const realEstateSchema = {
  collection: 'realEstate',
  fields: {
    property_id: 'string',
    address: 'string',
    property_type: 'string',
    list_price: 'number',
    estimated_value: 'number',
    equity: 'number',
    roi_pct: 'number',
    deal_type: 'string',
    status: 'string',
    location: 'string',
    created_at: 'timestamp',
    user_id: 'string',
  },
  indexes: ['property_type', 'deal_type', 'location', 'status', 'created_at', 'user_id'],
  requiredFields: ['property_id', 'address', 'list_price'],
};

const ALL_SCHEMAS = {
  deals: dealSchema,
  flips: flipSchema,
  pennyDeals: pennyDealSchema,
  receipts: receiptSchema,
  legalPayouts: legalPayoutSchema,
  grants: grantSchema,
  fiverrGigs: fiverrGigSchema,
  realEstate: realEstateSchema,
};

module.exports = {
  dealSchema,
  flipSchema,
  pennyDealSchema,
  receiptSchema,
  legalPayoutSchema,
  grantSchema,
  fiverrGigSchema,
  realEstateSchema,
  ALL_SCHEMAS,
};
