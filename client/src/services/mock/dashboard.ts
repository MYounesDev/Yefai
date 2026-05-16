import { DashboardOverview, HealthStatus, FactoryOverview, MachineStatus } from '@/types';

export const mockDashboardOverview: DashboardOverview = {
  total_anomalies: 247,
  active_anomalies: 12,
  avg_wear_um: 98.5,
  crisis_count: 3,
  uptime: 99.2,
  trend_anomalies: 2,
  trend_wear: -1.3,
};

export const mockHealthStatus: HealthStatus = {
  database: 'healthy',
  ai_model: 'healthy',
  novavision: 'healthy',
  puq_ai: 'healthy',
  last_check: new Date().toISOString(),
};

const machines: MachineStatus[] = [
  { machine_id: 'M-01', machine_name: 'Machine #1', status: 'safe', current_wear_um: 42, hours_to_critical: 78, wear_rate: 2.0, trend: 'stable', sparkline: [35, 36, 38, 40, 42] },
  { machine_id: 'M-02', machine_name: 'Machine #2', status: 'watch', current_wear_um: 112, hours_to_critical: 44, wear_rate: 2.5, trend: 'stable', sparkline: [95, 100, 105, 109, 112] },
  { machine_id: 'M-03', machine_name: 'Machine #3', status: 'critical', current_wear_um: 178, hours_to_critical: 9, wear_rate: 5.1, trend: 'accelerating', sparkline: [140, 152, 160, 170, 178] },
  { machine_id: 'M-04', machine_name: 'Machine #4', status: 'warning', current_wear_um: 162, hours_to_critical: 20, wear_rate: 2.8, trend: 'stable', sparkline: [140, 148, 154, 158, 162] },
  { machine_id: 'M-05', machine_name: 'Machine #5', status: 'safe', current_wear_um: 67, hours_to_critical: 64, wear_rate: 2.1, trend: 'decelerating', sparkline: [72, 71, 70, 69, 67] },
  { machine_id: 'M-06', machine_name: 'Machine #6', status: 'critical', current_wear_um: 189, hours_to_critical: 5, wear_rate: 6.2, trend: 'accelerating', sparkline: [155, 165, 175, 183, 189] },
  { machine_id: 'M-07', machine_name: 'Machine #7', status: 'watch', current_wear_um: 124, hours_to_critical: 36, wear_rate: 3.3, trend: 'accelerating', sparkline: [100, 108, 114, 120, 124] },
  { machine_id: 'M-08', machine_name: 'Machine #8', status: 'safe', current_wear_um: 55, hours_to_critical: 92, wear_rate: 1.6, trend: 'stable', sparkline: [48, 50, 52, 53, 55] },
];

export const mockFactoryOverview: FactoryOverview = {
  machines,
  total_machines: 8,
  critical_count: 2,
  avg_hours_to_critical: 43.5,
  next_maintenance: '2026-05-17T06:00:00Z',
};
