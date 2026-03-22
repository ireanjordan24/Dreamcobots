/**
 * DreamCobots API — Unit Tests
 *
 * Basic tests for the Express API layer.
 */

'use strict';

const app = require('../index');
const http = require('http');

let server;
let port;

beforeAll((done) => {
  server = http.createServer(app);
  server.listen(0, () => {
    port = server.address().port;
    done();
  });
});

afterAll((done) => {
  server.close(done);
});

function get(path) {
  return new Promise((resolve, reject) => {
    http.get(`http://localhost:${port}${path}`, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: JSON.parse(data) });
        } catch (e) {
          resolve({ status: res.statusCode, body: data });
        }
      });
    }).on('error', reject);
  });
}

describe('DreamCobots API', () => {
  test('GET /health returns status ok', async () => {
    const { status, body } = await get('/health');
    expect(status).toBe(200);
    expect(body.status).toBe('ok');
    expect(body.service).toBe('dreamcobots');
  });

  test('GET /bots returns bot catalog', async () => {
    const { status, body } = await get('/bots');
    expect(status).toBe(200);
    expect(Array.isArray(body.bots)).toBe(true);
    expect(body.total).toBeGreaterThan(0);
  });

  test('Bot catalog includes revenue bots', async () => {
    const { body } = await get('/bots');
    const revenueBot = body.bots.find(b => b.id === 'multi_source_lead_scraper');
    expect(revenueBot).toBeDefined();
    expect(revenueBot.category).toBe('revenue');
    expect(revenueBot.status).toBe('active');
  });

  test('Bot catalog includes all key categories', async () => {
    const { body } = await get('/bots');
    const categories = [...new Set(body.bots.map(b => b.category))];
    expect(categories).toContain('revenue');
    expect(categories).toContain('automation');
    expect(categories).toContain('ai');
  });
});
