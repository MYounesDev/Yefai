/**
 * Yefai Database Seeder
 * ---------------------
 * Seeds all tables with realistic data using upsert/insert to avoid conflicts.
 * Run: npm run seed (from project root)
 */

import { createClient } from '@supabase/supabase-js';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '..', '..', '.env') });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in server/.env');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// ── Color helpers ───────────────────────────────────────────────
const c = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', yellow: '\x1b[33m', red: '\x1b[31m',
  cyan: '\x1b[36m', blue: '\x1b[34m', magenta: '\x1b[35m',
};

function logStep(icon, msg) { console.log(`  ${icon}  ${c.cyan}${msg}${c.reset}`); }
function logOk(msg) { console.log(`  ${c.green}✓${c.reset} ${msg}`); }
function logWarn(msg) { console.log(`  ${c.yellow}⚠${c.reset} ${msg}`); }

// ── Fixed IDs for deterministic seeds ───────────────────────────
const ORG_1 = '11111111-1111-1111-1111-111111111111';
const ORG_2 = '22222222-2222-2222-2222-222222222222';

const CHAT_SESSION_1 = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa';
const CHAT_SESSION_2 = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab';

const NOTIF_CHANNEL_1 = 'cccccccc-cccc-cccc-cccc-cccccccccc01';
const NOTIF_CHANNEL_2 = 'cccccccc-cccc-cccc-cccc-cccccccccc02';

const SUPPORT_TICKET_1 = 'dddddddd-dddd-dddd-dddd-dddddddddd01';

// A placeholder user ID for seeded data (not a real auth user)
const SEED_USER_ID = 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeee01';

// ── Seed Functions ──────────────────────────────────────────────

async function seedOrganizations() {
  logStep('🏢', 'Organizations');
  const { error } = await supabase.from('organizations').upsert([
    {
      id: ORG_1, name: 'Acme Factory', slug: 'acme', plan: 'pro',
      settings: {
        notification_channels: { telegram: false, email: true, sms: false },
        critical_threshold_hours: 24, crisis_score_threshold: 70,
        refresh_interval_seconds: 30,
      },
    },
    {
      id: ORG_2, name: 'Global Manufacturing', slug: 'global-mfg', plan: 'enterprise',
      settings: {
        notification_channels: { telegram: true, email: true, sms: true },
        critical_threshold_hours: 12, crisis_score_threshold: 60,
        refresh_interval_seconds: 15,
      },
    },
  ], { onConflict: 'id' });
  if (error) throw error;
  logOk('2 organizations upserted');
}

async function seedProfiles() {
  logStep('👤', 'Profiles (seed placeholder)');
  const { error } = await supabase.from('profiles').upsert([
    { id: SEED_USER_ID, full_name: 'Seed User', is_platform_admin: true },
  ], { onConflict: 'id' });
  if (error) throw error;
  logOk('1 seed profile upserted');
}

async function seedOrgMembers() {
  logStep('👥', 'Org Members');
  const { error } = await supabase.from('org_members').upsert([
    { org_id: ORG_1, user_id: SEED_USER_ID, role: 'manager', status: 'active' },
  ], { onConflict: 'org_id,user_id' });
  if (error) logWarn(`org_members: ${error.message}`);
  else logOk('1 org member upserted');
}

async function seedSuppliers() {
  logStep('🚚', 'Suppliers');
  const { error } = await supabase.from('suppliers').upsert([
    { supplier_id: 'sup_001', supplier_name: 'GlobalTool GmbH', reliability_score: 0.85, lead_time_p50: 14, lead_time_p90: 21, is_primary: true },
    { supplier_id: 'sup_002', supplier_name: 'HızlıParça A.Ş.', reliability_score: 0.72, lead_time_p50: 3, lead_time_p90: 5, is_primary: false },
    { supplier_id: 'sup_003', supplier_name: 'PrecisionParts Ltd', reliability_score: 0.91, lead_time_p50: 21, lead_time_p90: 30, is_primary: true },
    { supplier_id: 'sup_004', supplier_name: 'KES-Tedarik A.Ş.', reliability_score: 0.78, lead_time_p50: 28, lead_time_p90: 45, is_primary: true },
    { supplier_id: 'sup_005', supplier_name: 'MakiTech Sanayi', reliability_score: 0.68, lead_time_p50: 12, lead_time_p90: 20, is_primary: false },
    { supplier_id: 'sup_006', supplier_name: 'CutRight Tools', reliability_score: 0.88, lead_time_p50: 5, lead_time_p90: 8, is_primary: true },
    { supplier_id: 'sup_007', supplier_name: 'Asya Makina Ltd.', reliability_score: 0.65, lead_time_p50: 5, lead_time_p90: 9, is_primary: false },
    { supplier_id: 'sup_008', supplier_name: 'Tecnologia Italiana S.r.l.', reliability_score: 0.93, lead_time_p50: 18, lead_time_p90: 25, is_primary: true },
    { supplier_id: 'sup_009', supplier_name: 'Nippon Precision KK', reliability_score: 0.97, lead_time_p50: 25, lead_time_p90: 35, is_primary: false },
    { supplier_id: 'sup_010', supplier_name: 'Balkan Endüstri A.Ş.', reliability_score: 0.70, lead_time_p50: 8, lead_time_p90: 14, is_primary: false },
  ], { onConflict: 'supplier_id' });
  if (error) throw error;
  logOk('10 suppliers upserted');
}

async function seedSparePartsCatalog() {
  logStep('🔧', 'Spare Parts Catalog');
  const { error } = await supabase.from('spare_parts_catalog').upsert([
    { part_id: 'p001', part_name: 'Insert Tip A-12', criticality: 'A', demand_pattern: 'high', unit_cost: 45.0, lead_time_p50: 14, lead_time_p90: 21, min_stock: 5, max_stock: 50, org_id: ORG_1 },
    { part_id: 'p002', part_name: 'Spindle Bearing XR-9', criticality: 'A', demand_pattern: 'low', unit_cost: 320.0, lead_time_p50: 21, lead_time_p90: 35, min_stock: 2, max_stock: 10, org_id: ORG_1 },
    { part_id: 'p003', part_name: 'Coolant Nozzle CN-4', criticality: 'B', demand_pattern: 'medium', unit_cost: 28.5, lead_time_p50: 7, lead_time_p90: 10, min_stock: 8, max_stock: 30, org_id: ORG_1 },
    { part_id: 'p004', part_name: 'Tool Holder TH-7', criticality: 'A', demand_pattern: 'medium', unit_cost: 185.0, lead_time_p50: 10, lead_time_p90: 18, min_stock: 3, max_stock: 15, org_id: ORG_1 },
    { part_id: 'p005', part_name: 'End Mill EM-16', criticality: 'B', demand_pattern: 'high', unit_cost: 62.0, lead_time_p50: 5, lead_time_p90: 8, min_stock: 10, max_stock: 40, org_id: ORG_1 },
    { part_id: 'p006', part_name: 'Collet Chuck CC-20', criticality: 'B', demand_pattern: 'medium', unit_cost: 95.0, lead_time_p50: 12, lead_time_p90: 20, min_stock: 5, max_stock: 20, org_id: ORG_1 },
    { part_id: 'p007', part_name: 'Drive Belt DB-3', criticality: 'C', demand_pattern: 'high', unit_cost: 18.0, lead_time_p50: 3, lead_time_p90: 5, min_stock: 15, max_stock: 50, org_id: ORG_1 },
    { part_id: 'p008', part_name: 'Linear Guide LG-15', criticality: 'A', demand_pattern: 'low', unit_cost: 540.0, lead_time_p50: 28, lead_time_p90: 45, min_stock: 1, max_stock: 5, org_id: ORG_1 },
    { part_id: 'p009', part_name: 'Servo Motor SM-4', criticality: 'A', demand_pattern: 'low', unit_cost: 1200.0, lead_time_p50: 18, lead_time_p90: 30, min_stock: 1, max_stock: 3, org_id: ORG_1 },
    { part_id: 'p010', part_name: 'Proximity Sensor PS-8', criticality: 'B', demand_pattern: 'medium', unit_cost: 42.0, lead_time_p50: 6, lead_time_p90: 10, min_stock: 6, max_stock: 25, org_id: ORG_1 },
    { part_id: 'p011', part_name: 'Rotary Encoder RE-6', criticality: 'B', demand_pattern: 'medium', unit_cost: 78.0, lead_time_p50: 9, lead_time_p90: 15, min_stock: 4, max_stock: 12, org_id: ORG_1 },
    { part_id: 'p012', part_name: 'Hydraulic Seal HS-2', criticality: 'C', demand_pattern: 'high', unit_cost: 12.0, lead_time_p50: 2, lead_time_p90: 4, min_stock: 20, max_stock: 100, org_id: ORG_1 },
    { part_id: 'p013', part_name: 'Ball Screw BS-20', criticality: 'A', demand_pattern: 'low', unit_cost: 890.0, lead_time_p50: 22, lead_time_p90: 40, min_stock: 2, max_stock: 8, org_id: ORG_1 },
    { part_id: 'p014', part_name: 'Coolant Filter CF-1', criticality: 'C', demand_pattern: 'medium', unit_cost: 15.0, lead_time_p50: 3, lead_time_p90: 5, min_stock: 10, max_stock: 50, org_id: ORG_1 },
    { part_id: 'p015', part_name: 'Tool Presetter TP-5', criticality: 'C', demand_pattern: 'low', unit_cost: 245.0, lead_time_p50: 8, lead_time_p90: 14, min_stock: 2, max_stock: 10, org_id: ORG_1 },
  ], { onConflict: 'part_id' });
  if (error) throw error;
  logOk('15 spare parts upserted');
}

async function seedSupplierParts() {
  logStep('🔗', 'Supplier ↔ Parts');
  const { error } = await supabase.from('supplier_parts').upsert([
    { supplier_id: 'sup_001', part_id: 'p001', unit_cost: 45.0, lead_time_days: 14, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_001', part_id: 'p004', unit_cost: 185.0, lead_time_days: 14, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_001', part_id: 'p006', unit_cost: 95.0, lead_time_days: 14, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_001', part_id: 'p009', unit_cost: 1200.0, lead_time_days: 14, is_preferred: false, org_id: ORG_1 },
    
    { supplier_id: 'sup_002', part_id: 'p001', unit_cost: 51.75, lead_time_days: 3, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_002', part_id: 'p003', unit_cost: 32.77, lead_time_days: 3, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_002', part_id: 'p007', unit_cost: 20.7, lead_time_days: 3, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_002', part_id: 'p012', unit_cost: 13.8, lead_time_days: 3, is_preferred: true, org_id: ORG_1 },

    { supplier_id: 'sup_003', part_id: 'p002', unit_cost: 384.0, lead_time_days: 21, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_003', part_id: 'p008', unit_cost: 648.0, lead_time_days: 21, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_003', part_id: 'p013', unit_cost: 1068.0, lead_time_days: 21, is_preferred: false, org_id: ORG_1 },

    { supplier_id: 'sup_004', part_id: 'p008', unit_cost: 513.0, lead_time_days: 28, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_004', part_id: 'p013', unit_cost: 845.5, lead_time_days: 28, is_preferred: true, org_id: ORG_1 },

    { supplier_id: 'sup_005', part_id: 'p004', unit_cost: 166.5, lead_time_days: 12, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_005', part_id: 'p006', unit_cost: 85.5, lead_time_days: 12, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_005', part_id: 'p008', unit_cost: 486.0, lead_time_days: 12, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_005', part_id: 'p015', unit_cost: 220.5, lead_time_days: 12, is_preferred: true, org_id: ORG_1 },

    { supplier_id: 'sup_006', part_id: 'p005', unit_cost: 65.1, lead_time_days: 7, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_006', part_id: 'p010', unit_cost: 44.1, lead_time_days: 7, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_006', part_id: 'p014', unit_cost: 15.75, lead_time_days: 7, is_preferred: true, org_id: ORG_1 },

    { supplier_id: 'sup_007', part_id: 'p003', unit_cost: 22.8, lead_time_days: 5, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_007', part_id: 'p005', unit_cost: 49.6, lead_time_days: 5, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_007', part_id: 'p007', unit_cost: 14.4, lead_time_days: 5, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_007', part_id: 'p010', unit_cost: 33.6, lead_time_days: 5, is_preferred: false, org_id: ORG_1 },

    { supplier_id: 'sup_008', part_id: 'p009', unit_cost: 1560.0, lead_time_days: 18, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_008', part_id: 'p011', unit_cost: 101.4, lead_time_days: 18, is_preferred: true, org_id: ORG_1 },
    { supplier_id: 'sup_008', part_id: 'p013', unit_cost: 1157.0, lead_time_days: 18, is_preferred: false, org_id: ORG_1 },

    { supplier_id: 'sup_009', part_id: 'p002', unit_cost: 464.0, lead_time_days: 25, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_009', part_id: 'p009', unit_cost: 1740.0, lead_time_days: 25, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_009', part_id: 'p011', unit_cost: 113.1, lead_time_days: 25, is_preferred: false, org_id: ORG_1 },

    { supplier_id: 'sup_010', part_id: 'p003', unit_cost: 21.37, lead_time_days: 8, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_010', part_id: 'p007', unit_cost: 13.5, lead_time_days: 8, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_010', part_id: 'p012', unit_cost: 9.0, lead_time_days: 8, is_preferred: false, org_id: ORG_1 },
    { supplier_id: 'sup_010', part_id: 'p014', unit_cost: 11.25, lead_time_days: 8, is_preferred: false, org_id: ORG_1 },
  ], { onConflict: 'supplier_id,part_id,org_id' });
  if (error) throw error;
  logOk('34 supplier-parts upserted');
}

async function seedInventorySnapshots() {
  logStep('📦', 'Inventory Snapshots');
  // No good unique constraint — check if data exists first
  const { data: existing } = await supabase.from('inventory_snapshots').select('id').limit(1);
  if (existing && existing.length > 0) {
    logWarn('Inventory snapshots already exist — skipping');
    return;
  }
  const { error } = await supabase.from('inventory_snapshots').insert([
    { part_id: 'p001', on_hand: 2, on_order: 10, min_level: 5, max_level: 50, org_id: ORG_1 },
    { part_id: 'p002', on_hand: 0, on_order: 2, min_level: 2, max_level: 10, org_id: ORG_1 },
    { part_id: 'p003', on_hand: 12, on_order: 0, min_level: 8, max_level: 30, org_id: ORG_1 },
    { part_id: 'p004', on_hand: 3, on_order: 5, min_level: 3, max_level: 15, org_id: ORG_1 },
    { part_id: 'p005', on_hand: 18, on_order: 0, min_level: 10, max_level: 40, org_id: ORG_1 },
    { part_id: 'p006', on_hand: 4, on_order: 5, min_level: 5, max_level: 20, org_id: ORG_1 },
    { part_id: 'p007', on_hand: 25, on_order: 0, min_level: 15, max_level: 50, org_id: ORG_1 },
    { part_id: 'p008', on_hand: 0, on_order: 1, min_level: 1, max_level: 5, org_id: ORG_1 },
    { part_id: 'p009', on_hand: 1, on_order: 0, min_level: 1, max_level: 3, org_id: ORG_1 },
    { part_id: 'p010', on_hand: 8, on_order: 0, min_level: 6, max_level: 25, org_id: ORG_1 },
    { part_id: 'p011', on_hand: 3, on_order: 4, min_level: 4, max_level: 12, org_id: ORG_1 },
    { part_id: 'p012', on_hand: 50, on_order: 0, min_level: 20, max_level: 100, org_id: ORG_1 },
    { part_id: 'p013', on_hand: 1, on_order: 2, min_level: 2, max_level: 8, org_id: ORG_1 },
    { part_id: 'p014', on_hand: 30, on_order: 0, min_level: 10, max_level: 50, org_id: ORG_1 },
    { part_id: 'p015', on_hand: 2, on_order: 0, min_level: 2, max_level: 10, org_id: ORG_1 },
  ]);
  if (error) logWarn(`inventory_snapshots: ${error.message}`);
  else logOk('15 inventory snapshots inserted');
}

async function seedPartTickets() {
  logStep('🎫', 'Part Tickets');
  const { data: existing } = await supabase.from('part_tickets').select('id').limit(1);
  if (existing && existing.length > 0) {
    logWarn('Part tickets already exist — skipping');
    return;
  }
  const { error } = await supabase.from('part_tickets').insert([
    { part_id: 'p001', status: 'waiting_part', quantity: 1, risk_level: 'crisis', org_id: ORG_1 },
    { part_id: 'p002', status: 'stockout', quantity: 1, risk_level: 'crisis', org_id: ORG_1 },
    { part_id: 'p008', status: 'ordered', quantity: 1, risk_level: 'crisis', org_id: ORG_1 },
    { part_id: 'p004', status: 'waiting_part', quantity: 1, risk_level: 'at_risk', org_id: ORG_1 },
    { part_id: 'p006', status: 'planned', quantity: 1, risk_level: 'at_risk', org_id: ORG_1 },
    { part_id: 'p011', status: 'planned', quantity: 1, risk_level: 'at_risk', org_id: ORG_1 },
    { part_id: 'p013', status: 'waiting_part', quantity: 1, risk_level: 'at_risk', org_id: ORG_1 },
    { part_id: 'p003', status: 'planned', quantity: 1, risk_level: 'watch', org_id: ORG_1 },
    { part_id: 'p005', status: 'planned', quantity: 1, risk_level: 'watch', org_id: ORG_1 },
    { part_id: 'p010', status: 'planned', quantity: 1, risk_level: 'watch', org_id: ORG_1 },
    { part_id: 'p009', status: 'ordered', quantity: 1, risk_level: 'none', org_id: ORG_1 },
    { part_id: 'p007', status: 'closed', quantity: 1, risk_level: 'none', org_id: ORG_1 },
  ]);
  if (error) logWarn(`part_tickets: ${error.message}`);
  else logOk('12 part tickets inserted');
}

async function seedPurchaseOrders() {
  logStep('📋', 'Purchase Orders');
  const { data: existing } = await supabase.from('purchase_orders').select('id').limit(1);
  if (existing && existing.length > 0) {
    logWarn('Purchase orders already exist — skipping');
    return;
  }
  const { error } = await supabase.from('purchase_orders').insert([
    { part_id: 'p001', supplier_id: 'sup_001', quantity: 10, status: 'ready_for_review', org_id: ORG_1 },
    { part_id: 'p002', supplier_id: 'sup_003', quantity: 2, status: 'ready_for_review', org_id: ORG_1 },
    { part_id: 'p008', supplier_id: 'sup_004', quantity: 1, status: 'ready_for_review', org_id: ORG_1 },
    { part_id: 'p004', supplier_id: 'sup_001', quantity: 3, status: 'approved', org_id: ORG_1 },
    { part_id: 'p005', supplier_id: 'sup_006', quantity: 20, status: 'approved', org_id: ORG_1 },
    { part_id: 'p013', supplier_id: 'sup_003', quantity: 1, status: 'draft', org_id: ORG_1 },
  ]);
  if (error) logWarn(`purchase_orders: ${error.message}`);
  else logOk('6 purchase orders inserted');
}

async function seedSetsAndImages() {
  logStep('📸', 'Sets & Images');
  const { data: existing } = await supabase.from('sets').select('id').limit(1);
  if (existing && existing.length > 0) {
    logWarn('Sets already exist — skipping');
    return existing;
  }
  const { data: sets, error: setsErr } = await supabase.from('sets').insert([
    { name: 'Machine Line A - Inspection', image_count: 3, org_id: ORG_1, metadata: { location: 'Factory Floor 1' } },
    { name: 'Machine Line B - Monitoring', image_count: 2, org_id: ORG_1, metadata: { location: 'Factory Floor 2' } },
  ]).select();
  if (setsErr) { logWarn(`sets: ${setsErr.message}`); return []; }

  const setId = sets[0].id;
  const { error: imgErr } = await supabase.from('images').insert([
    { set_id: setId, file_path: '/data/images/inspection_001.jpg', flank_wear: 0.12, wear_type: 'flank', wear: 0.12, org_id: ORG_1 },
    { set_id: setId, file_path: '/data/images/inspection_002.jpg', adhesive_wear: 0.08, wear_type: 'adhesive', wear: 0.08, org_id: ORG_1 },
    { set_id: setId, file_path: '/data/images/inspection_003.jpg', combination_wear: 0.25, wear_type: 'combination', wear: 0.25, org_id: ORG_1 },
  ]).select();
  if (imgErr) logWarn(`images: ${imgErr.message}`);
  else logOk('2 sets + 3 images inserted');
  return sets;
}

async function seedAnomalies() {
  logStep('🚨', 'Anomalies');
  const { data: existing } = await supabase.from('anomalies').select('id').eq('org_id', ORG_1).limit(1);
  if (existing && existing.length > 0) {
    logWarn('Anomalies already exist for org — skipping');
    return;
  }

  // Get an image id if available
  const { data: imgs } = await supabase.from('images').select('id').limit(1);
  const imgId = imgs && imgs.length > 0 ? imgs[0].id : null;

  const rows = [
    { image_id: imgId, score: 0.98, wear_type: 'flank', org_id: ORG_1, machine_id: 'MCH-001', status: 'new', severity: 'critical' },
    { image_id: imgId, score: 0.72, wear_type: 'adhesive', org_id: ORG_1, machine_id: 'MCH-002', status: 'reviewed', severity: 'warning' },
    { image_id: imgId, score: 0.45, wear_type: 'combination', org_id: ORG_1, machine_id: 'MCH-001', status: 'new', severity: 'info' },
    { image_id: imgId, score: 0.89, wear_type: 'flank', org_id: ORG_1, machine_id: 'MCH-003', status: 'new', severity: 'critical' },
  ];
  const { error } = await supabase.from('anomalies').insert(rows);
  if (error) logWarn(`anomalies: ${error.message}`);
  else logOk('4 anomalies inserted');
}

async function seedChatSessions() {
  logStep('💬', 'Chat Sessions & Messages');
  const { error: sessErr } = await supabase.from('chat_sessions').upsert([
    { id: CHAT_SESSION_1, org_id: ORG_1, user_id: SEED_USER_ID, title: 'Bearing failure analysis' },
    { id: CHAT_SESSION_2, org_id: ORG_1, user_id: SEED_USER_ID, title: 'Maintenance schedule Q3' },
  ], { onConflict: 'id' });
  if (sessErr) { logWarn(`chat_sessions: ${sessErr.message}`); return; }

  // Check if messages exist
  const { data: existing } = await supabase.from('chat_messages').select('id').eq('session_id', CHAT_SESSION_1).limit(1);
  if (existing && existing.length > 0) {
    logWarn('Chat messages already exist — skipping');
    return;
  }
  const { error: msgErr } = await supabase.from('chat_messages').insert([
    { session_id: CHAT_SESSION_1, role: 'user', content: 'What is the current wear status of Machine MCH-001?' },
    { session_id: CHAT_SESSION_1, role: 'assistant', content: 'Machine MCH-001 shows elevated flank wear at 0.12mm. The current rate suggests critical threshold will be reached in approximately 48 hours.' },
    { session_id: CHAT_SESSION_2, role: 'user', content: 'Show me the maintenance schedule for next quarter.' },
    { session_id: CHAT_SESSION_2, role: 'assistant', content: 'Based on current wear patterns, I recommend scheduling preventive maintenance for MCH-001 within 2 weeks and MCH-003 within 1 month.' },
  ]);
  if (msgErr) logWarn(`chat_messages: ${msgErr.message}`);
  else logOk('2 sessions + 4 messages');
}

async function seedNotificationChannels() {
  logStep('🔔', 'Notification Channels & Logs');
  const { error: chErr } = await supabase.from('notification_channels').upsert([
    { id: NOTIF_CHANNEL_1, org_id: ORG_1, channel_type: 'email', config: { email: 'ops@acme-factory.com' }, is_enabled: true },
    { id: NOTIF_CHANNEL_2, org_id: ORG_1, channel_type: 'webhook', config: { url: 'https://hooks.example.com/yefai' }, is_enabled: false },
  ], { onConflict: 'id' });
  if (chErr) { logWarn(`notification_channels: ${chErr.message}`); return; }

  const { data: existing } = await supabase.from('notification_logs').select('id').eq('org_id', ORG_1).limit(1);
  if (existing && existing.length > 0) {
    logWarn('Notification logs already exist — skipping');
    return;
  }
  const { error: logErr } = await supabase.from('notification_logs').insert([
    { org_id: ORG_1, channel_type: 'email', event_type: 'anomaly_alert', payload: { anomaly_id: 'test', severity: 'critical' }, status: 'sent' },
    { org_id: ORG_1, channel_type: 'email', event_type: 'inventory_low', payload: { part_id: 'P-100' }, status: 'sent' },
  ]);
  if (logErr) logWarn(`notification_logs: ${logErr.message}`);
  else logOk('2 channels + 2 logs');
}

async function seedSupportTickets() {
  logStep('🎟️', 'Support Tickets');
  const { error } = await supabase.from('support_tickets').upsert([
    {
      id: SUPPORT_TICKET_1, org_id: ORG_1, user_id: SEED_USER_ID,
      subject: 'Dashboard loading slowly', description: 'The dashboard overview page takes over 10 seconds to load.',
      status: 'open',
    },
  ], { onConflict: 'id' });
  if (error) logWarn(`support_tickets: ${error.message}`);
  else logOk('1 support ticket upserted');
}

// ── Main ────────────────────────────────────────────────────────

async function seed() {
  console.log(`\n${c.bright}${c.magenta}🌱 Yefai Database Seeder${c.reset}`);
  console.log(`${c.blue}${'═'.repeat(50)}${c.reset}\n`);

  const start = Date.now();

  try {
    await seedOrganizations();
    await seedProfiles();
    await seedOrgMembers();
    await seedSuppliers();
    await seedSparePartsCatalog();
    await seedSupplierParts();
    await seedInventorySnapshots();
    await seedPartTickets();
    await seedPurchaseOrders();
    await seedSetsAndImages();
    await seedAnomalies();
    await seedChatSessions();
    await seedNotificationChannels();
    await seedSupportTickets();

    const duration = ((Date.now() - start) / 1000).toFixed(2);
    console.log(`\n${c.green}${c.bright}✅ Seeding completed in ${duration}s${c.reset}\n`);
  } catch (error) {
    console.error(`\n${c.red}${c.bright}❌ Seeding failed:${c.reset}`, error);
    process.exit(1);
  }
}

seed();
