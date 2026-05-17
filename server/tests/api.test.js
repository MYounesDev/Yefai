/**
 * Yefai API Test Suite
 * --------------------
 * Tests all endpoints against a running server.
 * Creates test users on-the-fly via /api/auth/register.
 * Run: npm test (from project root)
 */

import axios from 'axios';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import { createClient } from '@supabase/supabase-js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;
const supabase = createClient(supabaseUrl, supabaseKey);

const PORT = process.env.PORT || 8000;
const BASE = `http://localhost:${PORT}`;
const API = `${BASE}/api`;
const TIMEOUT = 30000;

// ── Colors ──────────────────────────────────────────────────────
const c = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  red: '\x1b[31m', green: '\x1b[32m', yellow: '\x1b[33m',
  blue: '\x1b[34m', magenta: '\x1b[35m', cyan: '\x1b[36m', white: '\x1b[37m',
  bgRed: '\x1b[41m', bgGreen: '\x1b[42m', bgYellow: '\x1b[43m', bgBlue: '\x1b[44m',
};

// ── Stats ───────────────────────────────────────────────────────
let stats = { total: 0, passed: 0, failed: 0, num: 0, start: Date.now() };
const failures = [];

const logHeader = t => { console.log(`\n${c.bgBlue}${c.white}${c.bright} ${t} ${c.reset}`); console.log(`${c.blue}${'═'.repeat(60)}${c.reset}\n`); };
const logSub = t => { console.log(`\n${c.cyan}${c.bright}📋 ${t}${c.reset}`); console.log(`${c.cyan}${'─'.repeat(40)}${c.reset}`); };
const logInfo = m => console.log(`${c.blue}ℹ️  ${m}${c.reset}`);
const logWarn = m => console.log(`${c.yellow}⚠️  ${m}${c.reset}`);

function logTest(title, status, details = '') {
  const icon = status === 'PASS' ? '✅' : '❌';
  const color = status === 'PASS' ? c.green : c.red;
  const n = `${c.bright}[${String(stats.num).padStart(3, '0')}]${c.reset}`;
  console.log(`${n} ${icon} ${color}${status}${c.reset} - ${title}`);
  if (details) console.log(`     ${c.dim}${details}${c.reset}`);
}

// ── Helpers ─────────────────────────────────────────────────────
function has(obj, dotPath) {
  return dotPath.split('.').reduce((o, k) => (o != null && k in o ? o[k] : undefined), obj) !== undefined;
}

async function test(title, method, endpoint, { body, headers = {}, token, orgId, expected = 200, props = [], retries = 3, isRetry = false } = {}) {
  if (!isRetry) { stats.num++; stats.total++; }
  try {
    const h = { 'Content-Type': 'application/json', ...headers };
    if (token) h['Authorization'] = `Bearer ${token}`;
    if (orgId) h['X-Organization-Id'] = orgId;

    const res = await axios({
      method: method.toLowerCase(),
      url: `${API}${endpoint}`,
      headers: h,
      data: body || undefined,
      timeout: TIMEOUT,
      validateStatus: () => true,
    });

    const statusOk = res.status === expected;
    const missing = props.filter(p => !has(res.data, p));
    const ok = statusOk && missing.length === 0;

    let detail = `${method} ${endpoint} → ${res.status}`;
    if (!ok) detail += `\n     Response: ${JSON.stringify(res.data, null, 2).substring(0, 300)}`;

    if (ok) {
      stats.passed++;
      logTest(title, 'PASS', detail);
    } else {
      stats.failed++;
      let errParts = [];
      if (!statusOk) errParts.push(`Expected ${expected}, got ${res.status}`);
      if (missing.length) errParts.push(`Missing: ${missing.join(', ')}`);
      const err = errParts.join('; ');
      logTest(title, 'FAIL', `${err}\n     ${detail}`);
      failures.push({ num: stats.num, title, method, endpoint, error: err });
    }
    return { ok, res, data: res.data };
  } catch (err) {
    const isRetryable = err.code === 'ECONNREFUSED' || err.code === 'ECONNRESET';
    if (retries > 0 && isRetryable) {
      const delay = err.code === 'ECONNRESET' ? 3000 : 2000;
      logWarn(`${err.code} — Retrying "${title}"... (${retries} left, waiting ${delay / 1000}s)`);
      await new Promise(r => setTimeout(r, delay));
      return test(title, method, endpoint, { body, headers, token, orgId, expected, props, retries: retries - 1, isRetry: true });
    } 
    stats.failed++;
    const msg = err.code === 'ECONNREFUSED' ? 'Server not running'
              : err.code === 'ECONNRESET'   ? 'Connection reset by server (after retries)'
              : err.message;
    logTest(title, 'FAIL', msg);
    failures.push({ num: stats.num, title, method, endpoint, error: msg });
    return { ok: false };
  }
}

// ═══════════════════════════════════════════════════════════════
async function runAllTests() {
  logHeader('🚀 Yefai API Test Suite');

  // ── Shared state ────────────────────────────────────────────
  const ts = Date.now();
  const testEmail = `test_${ts}@gmail.com`;
  const testPass = 'TestPass123!';
  const testName = 'API Test User';
  let authToken = null;
  let refreshToken = null;
  let userId = null;
  const orgId = '11111111-1111-1111-1111-111111111111'; // seeded org

  try {
    // ── 1. HEALTH ──────────────────────────────────────────────
    logSub('Health & Connectivity');
    stats.num++; stats.total++;
    try {
      const hr = await axios.get(`${BASE}/health`, { timeout: TIMEOUT });
      if (hr.status === 200) { stats.passed++; logTest('Health check', 'PASS', 'GET /health → 200'); }
      else { stats.failed++; logTest('Health check', 'FAIL', `→ ${hr.status}`); }
    } catch (e) {
      stats.failed++;
      logTest('Health check', 'FAIL', e.message);
      failures.push({ num: stats.num, title: 'Health check', method: 'GET', endpoint: '/health', error: e.message });
      console.log(`\n${c.red}${c.bright}Server not reachable — aborting.${c.reset}\n`);
      printSummary();
      return;
    }

    // ── 2. AUTH — Register & Login ─────────────────────────────
    logSub('Authentication');

    const regRes = await test('Register new user', 'POST', '/auth/register', {
      body: { name: testName, email: testEmail, password: testPass },
      expected: 201,
      props: ['user.id'],
    });

    if (regRes.ok && regRes.data?.token) {
      authToken = regRes.data.token;
      userId = regRes.data.user.id;
      logInfo(`Registered user ${userId}`);
    }

    // Track which credentials to use for re-login
    let loginEmail = testEmail;
    let loginPass = testPass;

    // If register didn't return a token (e.g. email confirmation required), login
    if (!authToken) {
      // Confirm the user via admin API so login works
      if (regRes.ok && regRes.data?.user?.id) {
        userId = regRes.data.user.id;
        await supabase.auth.admin.updateUserById(userId, { email_confirm: true });
      }
      // Fall back to existing test user when registration fails (e.g. rate limit)
      loginEmail = "testuser@gmail.com";
      loginPass = "123123";
      const loginRes = await test('Login test user', 'POST', '/auth/login', {
        body: { email: loginEmail, password: loginPass },
        expected: 200,
        props: ['user.id', 'token'],
      });
      if (loginRes.ok) {
        authToken = loginRes.data.token;
        refreshToken = loginRes.data.refresh_token;
        userId = loginRes.data.user.id;
      }
    } else {
      // Still test the login endpoint
      const loginRes = await test('Login test user', 'POST', '/auth/login', {
        body: { email: testEmail, password: testPass },
        expected: 200,
        props: ['user.id', 'token'],
      });
      if (loginRes.ok) refreshToken = loginRes.data.refresh_token;
    }

    if (!authToken) {
      console.log(`\n${c.red}${c.bright}No auth token — cannot continue.${c.reset}\n`);
      printSummary();
      return;
    }

    // Setup: make the test user a platform admin + member of seeded org
    logInfo('Setting up org membership & admin flag via service key...');
    await supabase.from('profiles').upsert({ id: userId, full_name: testName, is_platform_admin: true }, { onConflict: 'id' });
    await supabase.from('org_members').upsert({ org_id: orgId, user_id: userId, role: 'manager', status: 'active' }, { onConflict: 'org_id,user_id' });

    // Re-login to pick up admin status in the JWT context
    const freshLogin = await test('Re-login (admin)', 'POST', '/auth/login', {
      body: { email: loginEmail, password: loginPass },
      expected: 200,
      props: ['token'],
    });
    if (freshLogin.ok) {
      authToken = freshLogin.data.token;
      refreshToken = freshLogin.data.refresh_token;
    }

    await test('Get current user (GET /auth/me)', 'GET', '/auth/me', {
      token: authToken, expected: 200, props: ['user.id'],
    });

    await test('Forgot password', 'POST', '/auth/forgot-password', {
      body: { email: testEmail }, expected: 200,
    });

    if (refreshToken) {
      await test('Refresh token', 'POST', '/auth/refresh', {
        body: { refresh_token: refreshToken }, expected: 200, props: ['token'],
      });
    }

    // ── 3. ORGANIZATIONS ───────────────────────────────────────
    logSub('Organizations');

    await test('List my organizations', 'GET', '/organizations', {
      token: authToken, expected: 200,
    });

    await test('Get organization by ID', 'GET', `/organizations/${orgId}`, {
      token: authToken, orgId, expected: 200, props: ['id', 'name'],
    });

    await test('Switch organization', 'POST', '/organizations/switch', {
      token: authToken, body: { org_id: orgId }, expected: 200,
    });

    await test('Update organization', 'PATCH', `/organizations/${orgId}`, {
      token: authToken, orgId, body: { name: 'Acme Factory' }, expected: 200,
    });

    // ── 4. MEMBERS ─────────────────────────────────────────────
    logSub('Members');

    await test('List org members', 'GET', `/organizations/${orgId}/members`, {
      token: authToken, orgId, expected: 200,
    });

    const inviteEmail = `invite_${ts}@gmail.com`;
    await test('Invite member', 'POST', `/organizations/${orgId}/members/invite`, {
      token: authToken, orgId, body: { email: inviteEmail, role: 'viewer' }, expected: 201,
    });

    // ── 5. ADMIN ───────────────────────────────────────────────
    logSub('Admin (Platform)');

    await test('Admin — platform stats', 'GET', '/admin/stats', {
      token: authToken, expected: 200,
    });

    await test('Admin — list organizations', 'GET', '/admin/organizations', {
      token: authToken, expected: 200,
    });

    const newOrgEmail = `neworg_${ts}@gmail.com`;
    const createOrgRes = await test('Admin — create organization', 'POST', '/admin/organizations', {
      token: authToken, body: { name: `Test Org ${ts}`, plan: 'free', manager_email: newOrgEmail },
      expected: 201, props: ['organization.id'],
    });

    if (createOrgRes.ok && createOrgRes.data?.organization?.id) {
      await test('Admin — get organization detail', 'GET', `/admin/organizations/${createOrgRes.data.organization.id}`, {
        token: authToken, expected: 200,
      });
    }

    await test('Admin — list users', 'GET', '/admin/users', {
      token: authToken, expected: 200,
    });

    await test('Admin — list support tickets', 'GET', '/admin/support-tickets', {
      token: authToken, expected: 200,
    });

    // ── 6. SPARE PARTS ─────────────────────────────────────────
    logSub('Spare Parts');

    await test('Get catalog', 'GET', '/spare-parts/catalog', {
      token: authToken, orgId, expected: 200, props: ['items'],
    });

    await test('Get catalog part detail', 'GET', '/spare-parts/catalog/P-100', {
      token: authToken, orgId, expected: 200, props: ['part_id'],
    });

    await test('Get inventory history', 'GET', '/spare-parts/inventory/P-100', {
      token: authToken, orgId, expected: 200, props: ['history'],
    });

    await test('Get tickets', 'GET', '/spare-parts/tickets', {
      token: authToken, orgId, expected: 200, props: ['tickets'],
    });

    await test('Get purchase orders', 'GET', '/spare-parts/purchase-orders', {
      token: authToken, orgId, expected: 200, props: ['orders'],
    });

    await test('Get suppliers', 'GET', '/spare-parts/suppliers', {
      token: authToken, orgId, expected: 200, props: ['suppliers'],
    });

    await test('Get alternative suppliers', 'GET', '/spare-parts/alternative-suppliers/P-100', {
      token: authToken, orgId, expected: 200, props: ['alternatives'],
    });

    await test('Get crisis dashboard', 'GET', '/spare-parts/crisis', {
      token: authToken, orgId, expected: 200,
    });

    await test('Get part crisis score', 'GET', '/spare-parts/crisis/P-100', {
      token: authToken, orgId, expected: 200,
    });

    // ── 7. ANOMALIES ───────────────────────────────────────────
    logSub('Anomalies');

    const anomListRes = await test('List anomalies', 'GET', '/anomalies', {
      token: authToken, orgId, expected: 200, props: ['anomalies'],
    });

    let anomalyId = null;
    if (anomListRes.ok && anomListRes.data?.anomalies?.length > 0) {
      anomalyId = anomListRes.data.anomalies[0].anomaly_id || anomListRes.data.anomalies[0].id;

      if (anomalyId) {
        await test('Get anomaly detail', 'GET', `/anomalies/${anomalyId}`, {
          token: authToken, orgId, expected: 200,
        });

        await test('Update anomaly status', 'PATCH', `/anomalies/${anomalyId}/status`, {
          token: authToken, orgId, body: { status: 'reviewed', notes: 'Reviewed by test' }, expected: 200,
        });
      }
    } else {
      logWarn('No anomalies found — skipping detail/update tests');
    }

    // ── 8. DASHBOARD ───────────────────────────────────────────
    logSub('Dashboard');

    await test('Dashboard overview', 'GET', '/dashboard/overview', {
      token: authToken, orgId, expected: 200,
    });

    await test('Dashboard health', 'GET', '/dashboard/health', {
      token: authToken, orgId, expected: 200,
    });

    // ── 9. CHAT ────────────────────────────────────────────────
    logSub('Chat');

    await test('List chat sessions', 'GET', '/chat/sessions', {
      token: authToken, orgId, expected: 200,
    });

    const chatRes = await test('Create chat session', 'POST', '/chat/sessions', {
      token: authToken, orgId, body: { title: 'Test Session' }, expected: 201,
    });

    let sessionId = chatRes.ok ? (chatRes.data?.id || chatRes.data?.session_id) : null;
    if (sessionId) {
      await test('Get session messages', 'GET', `/chat/sessions/${sessionId}`, {
        token: authToken, orgId, expected: 200,
      });

      await test('Archive chat session', 'DELETE', `/chat/sessions/${sessionId}`, {
        token: authToken, orgId, expected: 200,
      });
    }

    // ── 10. NOTIFICATIONS ──────────────────────────────────────
    logSub('Notifications');

    await test('Get notification logs', 'GET', '/notifications/logs', {
      token: authToken, orgId, expected: 200,
    });

    await test('List notification channels', 'GET', '/notifications/channels', {
      token: authToken, orgId, expected: 200,
    });

    const chRes = await test('Create notification channel', 'POST', '/notifications/channels', {
      token: authToken, orgId,
      body: { channel_type: 'email', config: { email: `test_${ts}@example.com` }, is_enabled: true },
      expected: 201, props: ['channel'],
    });

    let channelId = chRes.ok ? chRes.data?.channel?.id : null;
    if (channelId) {
      await test('Update notification channel', 'PATCH', `/notifications/channels/${channelId}`, {
        token: authToken, orgId, body: { is_enabled: false }, expected: 200,
      });

      await test('Delete notification channel', 'DELETE', `/notifications/channels/${channelId}`, {
        token: authToken, orgId, expected: 200,
      });
    }

    // ── 11. FILES ──────────────────────────────────────────────
    logSub('Files');

    await test('List org files', 'GET', '/files', {
      token: authToken, orgId, expected: 200,
    });

    // ── 12. UNAUTH TESTS ───────────────────────────────────────
    logSub('Unauthorized Access');

    await test('No token → 401 (auth/me)', 'GET', '/auth/me', {
      expected: 401,
    });

    await test('No token → 401 (organizations)', 'GET', '/organizations', {
      expected: 401,
    });

    await test('Bad token → 401', 'GET', '/auth/me', {
      token: 'invalid.jwt.token', expected: 401,
    });

    // ── 13. LOGOUT ─────────────────────────────────────────────
    logSub('Logout');
    await test('Logout', 'POST', '/auth/logout', {
      token: authToken, expected: 200,
    });

  } catch (err) {
    console.error(`\n${c.red}${c.bright}Unexpected error: ${err.message}${c.reset}`);
    console.error(err.stack);
  }
/*
  // ── CLEANUP ────────────────────────────────────────────────
  logSub('Cleanup');
  if (userId) {
    try {
      await supabase.from('org_members').delete().eq('user_id', userId);
      await supabase.from('profiles').delete().eq('id', userId);
      await supabase.auth.admin.deleteUser(userId);
      logInfo(`Cleaned up test user ${userId}`);
    } catch (e) {
      logWarn(`Cleanup warning: ${e.message}`);
    }
  }
*/
  printSummary();
}

// ── Summary ─────────────────────────────────────────────────────
function printSummary() {
  const dur = ((Date.now() - stats.start) / 1000).toFixed(2);
  const rate = stats.total > 0 ? ((stats.passed / stats.total) * 100).toFixed(1) : 0;

  logHeader('📊 Test Results Summary');
  console.log(`${c.bright}⏱️  Duration: ${c.cyan}${dur}s${c.reset}`);
  console.log(`${c.bright}📈 Total:    ${c.blue}${stats.total}${c.reset}`);
  console.log(`${c.bright}✅ Passed:   ${c.green}${stats.passed}${c.reset}`);
  console.log(`${c.bright}❌ Failed:   ${c.red}${stats.failed}${c.reset}`);
  console.log(`${c.bright}📊 Rate:     ${c.cyan}${rate}%${c.reset}`);

  if (rate >= 80) console.log(`\n${c.bgGreen}${c.white}${c.bright} 🎉 EXCELLENT! ${c.reset}`);
  else if (rate >= 60) console.log(`\n${c.bgYellow}${c.white}${c.bright} ⚠️  NEEDS IMPROVEMENT ${c.reset}`);
  else console.log(`\n${c.bgRed}${c.white}${c.bright} 🚨 MANY FAILURES — CHECK SETUP ${c.reset}`);

  if (failures.length) {
    logHeader('❌ Failed Tests');
    failures.forEach((t, i) => {
      console.log(`${c.bright}${i + 1}. [${t.num}] ${t.title}${c.reset}`);
      console.log(`   ${c.dim}${t.method} ${t.endpoint}${c.reset}`);
      console.log(`   ${c.red}${t.error}${c.reset}`);
      console.log(`   ${c.white}${'─'.repeat(55)}${c.reset}`);
    });
  }
}

runAllTests();
