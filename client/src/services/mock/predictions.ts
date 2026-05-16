import { Prediction, WearScenario, WearDataPoint } from '@/types';

function generateHistoricalData(currentWear: number, points = 12): WearDataPoint[] {
  const data: WearDataPoint[] = [];
  let wear = currentWear * 0.4;
  for (let i = 0; i < points; i++) {
    wear = Math.min(currentWear, wear + (currentWear * 0.6) / points + (Math.random() - 0.4) * 3);
    data.push({ hour: i * 2, wear_um: parseFloat(wear.toFixed(1)), is_historical: true });
  }
  data[data.length - 1] = { hour: (points - 1) * 2, wear_um: currentWear, is_historical: true };
  return data;
}

function generateScenarios(currentWear: number, baseRate: number, threshold = 200): WearScenario[] {
  const remaining = threshold - currentWear;
  return [
    {
      label: 'pessimistic',
      wear_rate_um_per_hour: parseFloat((baseRate * 1.25).toFixed(2)),
      hours_to_critical: parseFloat((remaining / (baseRate * 1.25)).toFixed(1)),
      projected_date: new Date(Date.now() + (remaining / (baseRate * 1.25)) * 3600000).toISOString(),
      color: '#F43F5E',
    },
    {
      label: 'baseline',
      wear_rate_um_per_hour: baseRate,
      hours_to_critical: parseFloat((remaining / baseRate).toFixed(1)),
      projected_date: new Date(Date.now() + (remaining / baseRate) * 3600000).toISOString(),
      color: '#06B6D4',
    },
    {
      label: 'optimistic',
      wear_rate_um_per_hour: parseFloat((baseRate * 0.75).toFixed(2)),
      hours_to_critical: parseFloat((remaining / (baseRate * 0.75)).toFixed(1)),
      projected_date: new Date(Date.now() + (remaining / (baseRate * 0.75)) * 3600000).toISOString(),
      color: '#10B981',
    },
  ];
}

const machineConfigs = [
  { id: 'M-01', name: 'Machine #1', wear: 42, rate: 2.0, status: 'safe' as const, confidence: 'high' as const, trend: 'stable' as const },
  { id: 'M-02', name: 'Machine #2', wear: 112, rate: 2.5, status: 'watch' as const, confidence: 'medium' as const, trend: 'stable' as const },
  { id: 'M-03', name: 'Machine #3', wear: 178, rate: 5.1, status: 'critical' as const, confidence: 'high' as const, trend: 'accelerating' as const },
  { id: 'M-04', name: 'Machine #4', wear: 162, rate: 2.8, status: 'warning' as const, confidence: 'medium' as const, trend: 'stable' as const },
  { id: 'M-05', name: 'Machine #5', wear: 67, rate: 2.1, status: 'safe' as const, confidence: 'high' as const, trend: 'decelerating' as const },
  { id: 'M-06', name: 'Machine #6', wear: 189, rate: 6.2, status: 'critical' as const, confidence: 'high' as const, trend: 'accelerating' as const },
  { id: 'M-07', name: 'Machine #7', wear: 124, rate: 3.3, status: 'watch' as const, confidence: 'low' as const, trend: 'accelerating' as const },
  { id: 'M-08', name: 'Machine #8', wear: 55, rate: 1.6, status: 'safe' as const, confidence: 'high' as const, trend: 'stable' as const },
];

export const mockPredictions: Prediction[] = machineConfigs.map((m) => ({
  machine_id: m.id,
  machine_name: m.name,
  current_wear_um: m.wear,
  critical_threshold_um: 200,
  wear_rate_um_per_hour: m.rate,
  hours_to_critical: parseFloat(((200 - m.wear) / m.rate).toFixed(1)),
  confidence: m.confidence,
  status: m.status,
  trend: m.trend,
  last_updated: new Date(Date.now() - Math.random() * 3600000).toISOString(),
  scenarios: generateScenarios(m.wear, m.rate),
  historical_data: generateHistoricalData(m.wear),
  wear_probabilities: [
    { type: 'flank_wear', probability: parseFloat((Math.random() * 0.4 + 0.5).toFixed(2)) },
    { type: 'adhesion', probability: parseFloat((Math.random() * 0.35 + 0.1).toFixed(2)) },
    { type: 'combination', probability: parseFloat((Math.random() * 0.2 + 0.05).toFixed(2)) },
  ],
  last_inspections: [
    { inspection_num: 8, wear_um: Math.round(m.wear * 0.7), rate: parseFloat((m.rate * 1.1).toFixed(1)) },
    { inspection_num: 9, wear_um: Math.round(m.wear * 0.8), rate: parseFloat((m.rate * 1.03).toFixed(1)) },
    { inspection_num: 10, wear_um: Math.round(m.wear * 0.88), rate: parseFloat((m.rate * 0.99).toFixed(1)) },
    { inspection_num: 11, wear_um: Math.round(m.wear * 0.95), rate: parseFloat((m.rate * 0.98).toFixed(1)) },
    { inspection_num: 12, wear_um: m.wear, rate: m.rate },
  ],
}));

export function getMockPrediction(machineId: string): Prediction {
  return mockPredictions.find((p) => p.machine_id === machineId) || mockPredictions[0];
}
