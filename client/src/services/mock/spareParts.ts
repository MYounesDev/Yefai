import { SparePart, InventorySnapshot, PartTicket, PurchaseOrder, CrisisScore } from '@/types';

export const mockSparePartsCatalog: SparePart[] = [
  { id: 'p001', name: 'Insert Tip A-12', part_number: 'INS-A12-CC', criticality_class: 'A_vital', compatible_wear_types: ['flank_wear'], supplier_count: 2, lead_time_p50_days: 14, lead_time_p90_days: 21, unit_cost_usd: 45.00 },
  { id: 'p002', name: 'Spindle Bearing XR-9', part_number: 'BRG-XR9-45', criticality_class: 'A_vital', compatible_wear_types: ['adhesion', 'combination'], supplier_count: 1, lead_time_p50_days: 21, lead_time_p90_days: 35, unit_cost_usd: 320.00 },
  { id: 'p003', name: 'Coolant Nozzle CN-4', part_number: 'NOZ-CN4-M', criticality_class: 'B_essential', compatible_wear_types: ['flank_wear', 'adhesion'], supplier_count: 3, lead_time_p50_days: 7, lead_time_p90_days: 10, unit_cost_usd: 28.50 },
  { id: 'p004', name: 'Tool Holder TH-7', part_number: 'HOL-TH7-40', criticality_class: 'A_vital', compatible_wear_types: ['combination'], supplier_count: 2, lead_time_p50_days: 10, lead_time_p90_days: 18, unit_cost_usd: 185.00 },
  { id: 'p005', name: 'End Mill EM-16', part_number: 'MILL-EM16-HSS', criticality_class: 'B_essential', compatible_wear_types: ['flank_wear'], supplier_count: 4, lead_time_p50_days: 5, lead_time_p90_days: 8, unit_cost_usd: 62.00 },
  { id: 'p006', name: 'Collet Chuck CC-20', part_number: 'COL-CC20-ER', criticality_class: 'B_essential', compatible_wear_types: ['adhesion'], supplier_count: 2, lead_time_p50_days: 12, lead_time_p90_days: 20, unit_cost_usd: 95.00 },
  { id: 'p007', name: 'Drive Belt DB-3', part_number: 'BEL-DB3-V', criticality_class: 'C_desirable', compatible_wear_types: ['flank_wear', 'combination'], supplier_count: 5, lead_time_p50_days: 3, lead_time_p90_days: 5, unit_cost_usd: 18.00 },
  { id: 'p008', name: 'Linear Guide LG-15', part_number: 'GUI-LG15-SB', criticality_class: 'A_vital', compatible_wear_types: ['adhesion', 'combination'], supplier_count: 1, lead_time_p50_days: 28, lead_time_p90_days: 45, unit_cost_usd: 540.00 },
  { id: 'p009', name: 'Servo Motor SM-4', part_number: 'MOT-SM4-AC', criticality_class: 'A_vital', compatible_wear_types: ['combination'], supplier_count: 2, lead_time_p50_days: 18, lead_time_p90_days: 30, unit_cost_usd: 1200.00 },
  { id: 'p010', name: 'Proximity Sensor PS-8', part_number: 'SEN-PS8-IND', criticality_class: 'B_essential', compatible_wear_types: ['flank_wear'], supplier_count: 3, lead_time_p50_days: 6, lead_time_p90_days: 10, unit_cost_usd: 42.00 },
  { id: 'p011', name: 'Rotary Encoder RE-6', part_number: 'ENC-RE6-OPT', criticality_class: 'B_essential', compatible_wear_types: ['adhesion'], supplier_count: 2, lead_time_p50_days: 9, lead_time_p90_days: 15, unit_cost_usd: 78.00 },
  { id: 'p012', name: 'Hydraulic Seal HS-2', part_number: 'SEA-HS2-NBR', criticality_class: 'C_desirable', compatible_wear_types: ['flank_wear', 'adhesion'], supplier_count: 6, lead_time_p50_days: 2, lead_time_p90_days: 4, unit_cost_usd: 12.00 },
  { id: 'p013', name: 'Ball Screw BS-20', part_number: 'SCR-BS20-C5', criticality_class: 'A_vital', compatible_wear_types: ['combination'], supplier_count: 2, lead_time_p50_days: 22, lead_time_p90_days: 40, unit_cost_usd: 890.00 },
  { id: 'p014', name: 'Coolant Filter CF-1', part_number: 'FIL-CF1-100', criticality_class: 'C_desirable', compatible_wear_types: ['flank_wear'], supplier_count: 4, lead_time_p50_days: 3, lead_time_p90_days: 5, unit_cost_usd: 15.00 },
  { id: 'p015', name: 'Tool Presetter TP-5', part_number: 'PRE-TP5-DIG', criticality_class: 'C_desirable', compatible_wear_types: ['adhesion', 'combination'], supplier_count: 2, lead_time_p50_days: 8, lead_time_p90_days: 14, unit_cost_usd: 245.00 },
];

export const mockInventorySnapshots: InventorySnapshot[] = [
  { part_id: 'p001', on_hand: 2, reorder_point: 5, on_order: 10, last_updated: new Date().toISOString() },
  { part_id: 'p002', on_hand: 0, reorder_point: 2, on_order: 2, last_updated: new Date().toISOString() },
  { part_id: 'p003', on_hand: 12, reorder_point: 8, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p004', on_hand: 3, reorder_point: 3, on_order: 5, last_updated: new Date().toISOString() },
  { part_id: 'p005', on_hand: 18, reorder_point: 10, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p006', on_hand: 4, reorder_point: 5, on_order: 5, last_updated: new Date().toISOString() },
  { part_id: 'p007', on_hand: 25, reorder_point: 15, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p008', on_hand: 0, reorder_point: 1, on_order: 1, last_updated: new Date().toISOString() },
  { part_id: 'p009', on_hand: 1, reorder_point: 1, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p010', on_hand: 8, reorder_point: 6, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p011', on_hand: 3, reorder_point: 4, on_order: 4, last_updated: new Date().toISOString() },
  { part_id: 'p012', on_hand: 50, reorder_point: 20, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p013', on_hand: 1, reorder_point: 2, on_order: 2, last_updated: new Date().toISOString() },
  { part_id: 'p014', on_hand: 30, reorder_point: 10, on_order: 0, last_updated: new Date().toISOString() },
  { part_id: 'p015', on_hand: 2, reorder_point: 2, on_order: 0, last_updated: new Date().toISOString() },
];

export const mockPartTickets: PartTicket[] = [
  { id: 'tkt_p001', machine_id: 'M-03', tool_id: 'Tool-A', part_id: 'p001', part_name: 'Insert Tip A-12', status: 'waiting_part', risk_level: 'crisis', stockout_risk_score: 82, needed_by: new Date(Date.now() + 86400000 * 2).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 14).toISOString(), auto_po_id: 'po_001', score_breakdown: { shortage_probability: 31.5, lead_time_gap: 21.3, criticality: 20.0, supplier_risk: 7.0, anomaly_severity: 2.5 } },
  { id: 'tkt_p002', machine_id: 'M-06', tool_id: 'Tool-B', part_id: 'p002', part_name: 'Spindle Bearing XR-9', status: 'stockout', risk_level: 'crisis', stockout_risk_score: 95, needed_by: new Date(Date.now() + 86400000).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 21).toISOString(), auto_po_id: 'po_002', score_breakdown: { shortage_probability: 40.0, lead_time_gap: 25.0, criticality: 20.0, supplier_risk: 8.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p003', machine_id: 'M-04', tool_id: 'Tool-C', part_id: 'p008', part_name: 'Linear Guide LG-15', status: 'ordered', risk_level: 'crisis', stockout_risk_score: 78, needed_by: new Date(Date.now() + 86400000 * 5).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 28).toISOString(), auto_po_id: 'po_003', score_breakdown: { shortage_probability: 28.5, lead_time_gap: 20.0, criticality: 20.0, supplier_risk: 7.5, anomaly_severity: 2.0 } },
  { id: 'tkt_p004', machine_id: 'M-07', tool_id: 'Tool-A', part_id: 'p004', part_name: 'Tool Holder TH-7', status: 'waiting_part', risk_level: 'at_risk', stockout_risk_score: 62, needed_by: new Date(Date.now() + 86400000 * 8).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 10).toISOString(), score_breakdown: { shortage_probability: 22.0, lead_time_gap: 18.0, criticality: 14.0, supplier_risk: 6.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p005', machine_id: 'M-02', tool_id: 'Tool-D', part_id: 'p006', part_name: 'Collet Chuck CC-20', status: 'planned', risk_level: 'at_risk', stockout_risk_score: 58, needed_by: new Date(Date.now() + 86400000 * 12).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 12).toISOString(), score_breakdown: { shortage_probability: 20.0, lead_time_gap: 17.0, criticality: 14.0, supplier_risk: 5.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p006', machine_id: 'M-01', tool_id: 'Tool-B', part_id: 'p011', part_name: 'Rotary Encoder RE-6', status: 'planned', risk_level: 'at_risk', stockout_risk_score: 55, needed_by: new Date(Date.now() + 86400000 * 10).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 9).toISOString(), score_breakdown: { shortage_probability: 18.0, lead_time_gap: 16.0, criticality: 14.0, supplier_risk: 5.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p007', machine_id: 'M-05', tool_id: 'Tool-C', part_id: 'p013', part_name: 'Ball Screw BS-20', status: 'waiting_part', risk_level: 'at_risk', stockout_risk_score: 60, needed_by: new Date(Date.now() + 86400000 * 9).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 22).toISOString(), score_breakdown: { shortage_probability: 21.0, lead_time_gap: 17.5, criticality: 14.0, supplier_risk: 5.5, anomaly_severity: 2.0 } },
  { id: 'tkt_p008', machine_id: 'M-08', tool_id: 'Tool-A', part_id: 'p003', part_name: 'Coolant Nozzle CN-4', status: 'planned', risk_level: 'watch', stockout_risk_score: 38, needed_by: new Date(Date.now() + 86400000 * 20).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 7).toISOString(), score_breakdown: { shortage_probability: 12.0, lead_time_gap: 11.0, criticality: 10.0, supplier_risk: 3.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p009', machine_id: 'M-01', tool_id: 'Tool-D', part_id: 'p005', part_name: 'End Mill EM-16', status: 'planned', risk_level: 'watch', stockout_risk_score: 35, needed_by: new Date(Date.now() + 86400000 * 25).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 5).toISOString(), score_breakdown: { shortage_probability: 11.0, lead_time_gap: 10.0, criticality: 10.0, supplier_risk: 2.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p010', machine_id: 'M-02', tool_id: 'Tool-A', part_id: 'p010', part_name: 'Proximity Sensor PS-8', status: 'planned', risk_level: 'watch', stockout_risk_score: 32, needed_by: new Date(Date.now() + 86400000 * 28).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 6).toISOString(), score_breakdown: { shortage_probability: 10.0, lead_time_gap: 9.0, criticality: 10.0, supplier_risk: 1.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p011', machine_id: 'M-03', tool_id: 'Tool-B', part_id: 'p009', part_name: 'Servo Motor SM-4', status: 'ordered', risk_level: 'none', stockout_risk_score: 18, needed_by: new Date(Date.now() + 86400000 * 40).toISOString(), expected_replenishment: new Date(Date.now() + 86400000 * 18).toISOString(), score_breakdown: { shortage_probability: 5.0, lead_time_gap: 5.0, criticality: 5.0, supplier_risk: 1.0, anomaly_severity: 2.0 } },
  { id: 'tkt_p012', machine_id: 'M-07', tool_id: 'Tool-C', part_id: 'p007', part_name: 'Drive Belt DB-3', status: 'closed', risk_level: 'none', stockout_risk_score: 10, needed_by: new Date(Date.now() - 86400000 * 5).toISOString(), expected_replenishment: new Date(Date.now() - 86400000 * 8).toISOString(), score_breakdown: { shortage_probability: 2.0, lead_time_gap: 2.0, criticality: 3.0, supplier_risk: 1.0, anomaly_severity: 2.0 } },
];

export const mockPurchaseOrders: PurchaseOrder[] = [
  { id: 'po_001', po_number: 'PO-2026-0042', part_id: 'p001', part_name: 'Insert Tip A-12', supplier_id: 'sup_001', supplier_name: 'GlobalTool GmbH', status: 'ready_for_review', urgency: 'critical', quantity: 10, unit_cost_usd: 45.00, total_cost_usd: 450.00, needed_by: new Date(Date.now() + 86400000 * 2).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 14).toISOString(), alternative_supplier_id: 'sup_002', alternative_supplier_name: 'HızlıParça A.Ş.', alternative_lead_time_days: 3, alternative_cost_delta_pct: 15, ticket_id: 'tkt_p001', created_at: new Date(Date.now() - 3600000 * 6).toISOString() },
  { id: 'po_002', po_number: 'PO-2026-0043', part_id: 'p002', part_name: 'Spindle Bearing XR-9', supplier_id: 'sup_003', supplier_name: 'PrecisionParts Ltd', status: 'ready_for_review', urgency: 'critical', quantity: 2, unit_cost_usd: 320.00, total_cost_usd: 640.00, needed_by: new Date(Date.now() + 86400000).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 21).toISOString(), ticket_id: 'tkt_p002', created_at: new Date(Date.now() - 3600000 * 3).toISOString() },
  { id: 'po_003', po_number: 'PO-2026-0044', part_id: 'p008', part_name: 'Linear Guide LG-15', supplier_id: 'sup_004', supplier_name: 'KES-Tedarik A.Ş.', status: 'ready_for_review', urgency: 'rush', quantity: 1, unit_cost_usd: 540.00, total_cost_usd: 540.00, needed_by: new Date(Date.now() + 86400000 * 5).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 28).toISOString(), alternative_supplier_id: 'sup_005', alternative_supplier_name: 'MakiTech Sanayi', alternative_lead_time_days: 12, alternative_cost_delta_pct: -5, ticket_id: 'tkt_p003', created_at: new Date(Date.now() - 3600000 * 12).toISOString() },
  { id: 'po_004', po_number: 'PO-2026-0039', part_id: 'p004', part_name: 'Tool Holder TH-7', supplier_id: 'sup_001', supplier_name: 'GlobalTool GmbH', status: 'approved', urgency: 'normal', quantity: 3, unit_cost_usd: 185.00, total_cost_usd: 555.00, needed_by: new Date(Date.now() + 86400000 * 15).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 10).toISOString(), created_at: new Date(Date.now() - 86400000 * 2).toISOString() },
  { id: 'po_005', po_number: 'PO-2026-0038', part_id: 'p005', part_name: 'End Mill EM-16', supplier_id: 'sup_006', supplier_name: 'CutRight Tools', status: 'approved', urgency: 'normal', quantity: 20, unit_cost_usd: 62.00, total_cost_usd: 1240.00, needed_by: new Date(Date.now() + 86400000 * 20).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 5).toISOString(), created_at: new Date(Date.now() - 86400000 * 3).toISOString() },
  { id: 'po_006', po_number: 'PO-2026-0035', part_id: 'p013', part_name: 'Ball Screw BS-20', supplier_id: 'sup_003', supplier_name: 'PrecisionParts Ltd', status: 'draft', urgency: 'rush', quantity: 1, unit_cost_usd: 890.00, total_cost_usd: 890.00, needed_by: new Date(Date.now() + 86400000 * 9).toISOString(), expected_delivery: new Date(Date.now() + 86400000 * 22).toISOString(), created_at: new Date(Date.now() - 3600000).toISOString() },
];

export const mockCrisisScore: CrisisScore = {
  image_id: 'img_0003',
  part_id: 'p001',
  part_name: 'Insert Tip A-12',
  on_hand: 2,
  reorder_point: 5,
  risk_level: 'crisis',
  score: 82,
  auto_po_id: 'po_001',
};
