// ===== AUTH & ORG TYPES =====

export type Role = 'admin' | 'manager' | 'operator' | 'technician' | 'procurement' | 'viewer';

export interface User {
  id: string;
  name: string;
  email: string;
  avatar_url?: string;
  created_at: string;
}

export interface OrgMembership {
  org_id: string;
  org_name: string;
  org_logo_url?: string;
  role: Role;
  joined_at: string;
}

export interface UserWithOrgs extends User {
  organizations: OrgMembership[];
}

export interface OrgSettings {
  notification_channels: { telegram: boolean; email: boolean; sms: boolean };
  critical_threshold_hours: number;
  crisis_score_threshold: number;
  refresh_interval_seconds: number;
}

export interface Organization {
  id: string;
  name: string;
  logo_url?: string;
  plan: 'free' | 'pro' | 'enterprise';
  member_count: number;
  created_at: string;
  settings?: OrgSettings;
}

export interface OrgMember {
  user_id: string;
  name: string;
  email: string;
  avatar_url?: string;
  role: Role;
  joined_at: string;
  status: 'active' | 'invited' | 'disabled';
  last_active?: string;
}

export interface SupportTicket {
  id: string;
  org_id: string;
  org_name: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  created_at: string;
  resolved_at?: string;
  resolution?: string;
}

// ===== DOMAIN TYPES =====

export interface HealthStatus {
  database: 'healthy' | 'degraded' | 'down';
  ai_model: 'healthy' | 'degraded' | 'down';
  novavision: 'healthy' | 'degraded' | 'down';
  puq_ai: 'healthy' | 'degraded' | 'down';
  last_check: string;
}

export interface DashboardOverview {
  total_anomalies: number;
  active_anomalies: number;
  avg_wear_um: number;
  crisis_count: number;
  uptime: number;
  trend_anomalies: number;
  trend_wear: number;
}

export type WearType = 'flank_wear' | 'adhesion' | 'combination';
export type Severity = 'low' | 'medium' | 'high' | 'critical';
export type AnomalyStatus = 'new' | 'reviewed' | 'resolved';
export type MachineStatusLevel = 'safe' | 'watch' | 'warning' | 'critical';

export interface SensorDataPoint {
  t: number;
  value: number;
}

export interface Anomaly {
  id: string;
  machine_id: string;
  tool_id: string;
  timestamp: string;
  anomaly_score: number;
  wear_type: WearType;
  estimated_wear_um: number;
  severity: Severity;
  status: AnomalyStatus;
  image_id?: string;
  set_id?: string;
}

export interface AnomalyDetail extends Anomaly {
  image_url?: string;
  heatmap_url?: string;
  wear_probabilities: { type: WearType; probability: number }[];
  sensor_data: {
    accelerometer: SensorDataPoint[];
    acoustic: SensorDataPoint[];
    force_x: SensorDataPoint[];
    force_y: SensorDataPoint[];
    force_z: SensorDataPoint[];
  };
  anomaly_region?: { x: number; y: number; w: number; h: number };
}

export interface WearScenario {
  label: 'pessimistic' | 'baseline' | 'optimistic';
  wear_rate_um_per_hour: number;
  hours_to_critical: number;
  projected_date: string;
  color: string;
}

export interface WearDataPoint {
  hour: number;
  wear_um: number;
  is_historical: boolean;
}

export interface Prediction {
  machine_id: string;
  machine_name: string;
  current_wear_um: number;
  critical_threshold_um: number;
  wear_rate_um_per_hour: number;
  hours_to_critical: number;
  confidence: 'low' | 'medium' | 'high';
  status: MachineStatusLevel;
  trend: 'accelerating' | 'stable' | 'decelerating';
  last_updated: string;
  scenarios: WearScenario[];
  historical_data: WearDataPoint[];
  wear_probabilities: { type: WearType; probability: number }[];
  last_inspections: { inspection_num: number; wear_um: number; rate: number }[];
}

export interface MachineStatus {
  machine_id: string;
  machine_name: string;
  status: MachineStatusLevel;
  current_wear_um: number;
  hours_to_critical: number;
  wear_rate: number;
  trend: 'accelerating' | 'stable' | 'decelerating';
  sparkline: number[];
}

export interface FactoryOverview {
  machines: MachineStatus[];
  total_machines: number;
  critical_count: number;
  avg_hours_to_critical: number;
  next_maintenance: string;
}

// ===== SPARE PARTS TYPES =====

export type CriticalityClass = 'A_vital' | 'B_essential' | 'C_desirable';
export type RiskLevel = 'none' | 'watch' | 'at_risk' | 'crisis';
export type TicketStatus = 'planned' | 'waiting_part' | 'ordered' | 'stockout' | 'closed';
export type POStatus = 'draft' | 'ready_for_review' | 'approved' | 'rejected';
export type POUrgency = 'normal' | 'rush' | 'critical';

export interface SparePart {
  id: string;
  name: string;
  part_number: string;
  criticality_class: CriticalityClass;
  compatible_wear_types: WearType[];
  supplier_count: number;
  lead_time_p50_days: number;
  lead_time_p90_days: number;
  unit_cost_usd: number;
}

export interface InventorySnapshot {
  part_id: string;
  on_hand: number;
  reorder_point: number;
  on_order: number;
  last_updated: string;
}

export interface PartTicket {
  id: string;
  machine_id: string;
  tool_id: string;
  part_id: string;
  part_name: string;
  status: TicketStatus;
  risk_level: RiskLevel;
  stockout_risk_score: number;
  needed_by: string;
  expected_replenishment: string;
  auto_po_id?: string;
  score_breakdown: {
    shortage_probability: number;
    lead_time_gap: number;
    criticality: number;
    supplier_risk: number;
    anomaly_severity: number;
  };
}

export interface Supplier {
  id: string;
  name: string;
  country: string;
  reliability_score: number;
  avg_lead_time_days: number;
  lead_time_p50_days: number;
  lead_time_p90_days: number;
  parts_supplied: string[];
  is_primary: boolean;
  cost_index: number;
  in_stock_probability: number;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  part_id: string;
  part_name: string;
  supplier_id: string;
  supplier_name: string;
  status: POStatus;
  urgency: POUrgency;
  quantity: number;
  unit_cost_usd: number;
  total_cost_usd: number;
  needed_by: string;
  expected_delivery: string;
  alternative_supplier_id?: string;
  alternative_supplier_name?: string;
  alternative_lead_time_days?: number;
  alternative_cost_delta_pct?: number;
  ticket_id?: string;
  created_at: string;
}

export interface CrisisScore {
  image_id: string;
  part_id: string;
  part_name: string;
  on_hand: number;
  reorder_point: number;
  risk_level: RiskLevel;
  score: number;
  auto_po_id?: string;
}

// ===== CHAT TYPES =====

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  images?: { url: string; metadata: { set: string; wear_level: number; machine_id: string; anomaly_score: number } }[];
  sources?: { label: string; similarity: number; anomaly_id?: string }[];
}

export interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface SearchResult {
  image_id: string;
  set: string;
  wear_level: number;
  machine_id: string;
  anomaly_score: number;
  similarity: number;
  url?: string;
}

// ===== NOTIFICATION TYPES =====

export type NotificationType = 'anomaly_alert' | 'critical_warning' | 'report' | 'crisis_alert' | 'po_notification';
export type NotificationChannel = 'telegram' | 'email' | 'sms';
export type NotificationStatus = 'delivered' | 'failed' | 'pending';

export interface NotificationLog {
  id: string;
  type: NotificationType;
  channel: NotificationChannel;
  target: string;
  status: NotificationStatus;
  timestamp: string;
  payload: Record<string, unknown>;
  error_message?: string;
}

// ===== ADMIN TYPES =====

export interface PlatformStats {
  total_orgs: number;
  total_users: number;
  active_orgs: number;
  tickets_open: number;
}
