import { Supplier } from '@/types';

export const mockSuppliers: Supplier[] = [
  { id: 'sup_001', name: 'GlobalTool GmbH', country: 'Germany', reliability_score: 85, avg_lead_time_days: 14, lead_time_p50_days: 14, lead_time_p90_days: 21, parts_supplied: ['p001', 'p004', 'p006', 'p009'], is_primary: true, cost_index: 1.0, in_stock_probability: 0.60 },
  { id: 'sup_002', name: 'HızlıParça A.Ş.', country: 'Turkey', reliability_score: 72, avg_lead_time_days: 3, lead_time_p50_days: 3, lead_time_p90_days: 5, parts_supplied: ['p001', 'p003', 'p007', 'p012'], is_primary: false, cost_index: 1.15, in_stock_probability: 0.90 },
  { id: 'sup_003', name: 'PrecisionParts Ltd', country: 'UK', reliability_score: 91, avg_lead_time_days: 21, lead_time_p50_days: 21, lead_time_p90_days: 30, parts_supplied: ['p002', 'p008', 'p013'], is_primary: true, cost_index: 1.20, in_stock_probability: 0.75 },
  { id: 'sup_004', name: 'KES-Tedarik A.Ş.', country: 'Turkey', reliability_score: 78, avg_lead_time_days: 28, lead_time_p50_days: 28, lead_time_p90_days: 45, parts_supplied: ['p008', 'p013'], is_primary: true, cost_index: 0.95, in_stock_probability: 0.50 },
  { id: 'sup_005', name: 'MakiTech Sanayi', country: 'Turkey', reliability_score: 68, avg_lead_time_days: 12, lead_time_p50_days: 12, lead_time_p90_days: 20, parts_supplied: ['p004', 'p006', 'p008', 'p015'], is_primary: false, cost_index: 0.90, in_stock_probability: 0.65 },
  { id: 'sup_006', name: 'CutRight Tools', country: 'USA', reliability_score: 88, avg_lead_time_days: 7, lead_time_p50_days: 5, lead_time_p90_days: 8, parts_supplied: ['p005', 'p010', 'p014'], is_primary: true, cost_index: 1.05, in_stock_probability: 0.92 },
  { id: 'sup_007', name: 'Asya Makina Ltd.', country: 'Turkey', reliability_score: 65, avg_lead_time_days: 5, lead_time_p50_days: 5, lead_time_p90_days: 9, parts_supplied: ['p003', 'p005', 'p007', 'p010'], is_primary: false, cost_index: 0.80, in_stock_probability: 0.70 },
  { id: 'sup_008', name: 'Tecnologia Italiana S.r.l.', country: 'Italy', reliability_score: 93, avg_lead_time_days: 18, lead_time_p50_days: 18, lead_time_p90_days: 25, parts_supplied: ['p009', 'p011', 'p013'], is_primary: true, cost_index: 1.30, in_stock_probability: 0.80 },
  { id: 'sup_009', name: 'Nippon Precision KK', country: 'Japan', reliability_score: 97, avg_lead_time_days: 25, lead_time_p50_days: 25, lead_time_p90_days: 35, parts_supplied: ['p002', 'p009', 'p011'], is_primary: false, cost_index: 1.45, in_stock_probability: 0.98 },
  { id: 'sup_010', name: 'Balkan Endüstri A.Ş.', country: 'Turkey', reliability_score: 70, avg_lead_time_days: 8, lead_time_p50_days: 8, lead_time_p90_days: 14, parts_supplied: ['p003', 'p007', 'p012', 'p014'], is_primary: false, cost_index: 0.75, in_stock_probability: 0.60 },
];

export function getAlternativeSuppliers(partId: string): Supplier[] {
  return mockSuppliers.filter((s) => s.parts_supplied.includes(partId));
}
