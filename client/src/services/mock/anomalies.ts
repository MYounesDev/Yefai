import { Anomaly, AnomalyDetail, WearType, Severity } from '@/types';

function getSeverity(score: number): Severity {
  if (score > 0.75) return 'critical';
  if (score > 0.5) return 'high';
  if (score > 0.3) return 'medium';
  return 'low';
}

function getWearType(i: number): WearType {
  if (i % 5 === 0) return 'combination';
  if (i % 3 === 0) return 'adhesion';
  return 'flank_wear';
}

function hoursAgo(h: number): string {
  return new Date(Date.now() - h * 3600 * 1000).toISOString();
}

function generateSensorData(points = 150, base = 0.5, variance = 0.3) {
  return Array.from({ length: points }, (_, i) => ({
    t: i,
    value: Math.max(0, base + (Math.random() - 0.5) * variance),
  }));
}

const machineIds = ['M-01', 'M-02', 'M-03', 'M-04', 'M-05', 'M-06', 'M-07', 'M-08'];
const toolIds = ['Tool-A', 'Tool-B', 'Tool-C', 'Tool-D'];

export const mockAnomalies: Anomaly[] = Array.from({ length: 60 }, (_, i) => {
  const score = parseFloat((Math.random() * 0.88 + 0.1).toFixed(3));
  return {
    id: `anom_${String(i + 1).padStart(3, '0')}`,
    machine_id: machineIds[i % machineIds.length],
    tool_id: toolIds[i % toolIds.length],
    timestamp: hoursAgo(i * 2.7 + Math.random() * 2),
    anomaly_score: score,
    wear_type: getWearType(i),
    estimated_wear_um: Math.round(20 + score * 180),
    severity: getSeverity(score),
    status: i < 12 ? 'new' : i < 35 ? 'reviewed' : 'resolved',
    image_id: `img_${String(i + 1).padStart(4, '0')}`,
    set_id: `set_${(i % 17) + 1}`,
  };
});

export const mockAnomalyDetail: AnomalyDetail = {
  ...mockAnomalies[2],
  anomaly_score: 0.847,
  severity: 'critical',
  estimated_wear_um: 172,
  wear_type: 'flank_wear',
  status: 'new',
  image_url: '/api/placeholder/800/600',
  heatmap_url: '/api/placeholder/800/600',
  anomaly_region: { x: 120, y: 80, w: 200, h: 150 },
  wear_probabilities: [
    { type: 'flank_wear', probability: 0.87 },
    { type: 'adhesion', probability: 0.34 },
    { type: 'combination', probability: 0.18 },
  ],
  sensor_data: {
    accelerometer: generateSensorData(180, 0.45, 0.4),
    acoustic: generateSensorData(180, 0.60, 0.5),
    force_x: generateSensorData(180, 0.55, 0.35),
    force_y: generateSensorData(180, 0.70, 0.45),
    force_z: generateSensorData(180, 0.40, 0.3),
  },
};

export function getAnomalyDetailById(id: string): AnomalyDetail {
  const base = mockAnomalies.find((a) => a.id === id) || mockAnomalies[0];
  return {
    ...base,
    image_url: '/api/placeholder/800/600',
    heatmap_url: '/api/placeholder/800/600',
    anomaly_region: { x: 100, y: 60, w: 180, h: 140 },
    wear_probabilities: [
      { type: 'flank_wear', probability: parseFloat((Math.random() * 0.5 + 0.4).toFixed(2)) },
      { type: 'adhesion', probability: parseFloat((Math.random() * 0.4 + 0.1).toFixed(2)) },
      { type: 'combination', probability: parseFloat((Math.random() * 0.3 + 0.05).toFixed(2)) },
    ],
    sensor_data: {
      accelerometer: generateSensorData(150, 0.45 + base.anomaly_score * 0.3, 0.4),
      acoustic: generateSensorData(150, 0.60 + base.anomaly_score * 0.25, 0.5),
      force_x: generateSensorData(150, 0.55 + base.anomaly_score * 0.2, 0.35),
      force_y: generateSensorData(150, 0.70 + base.anomaly_score * 0.3, 0.45),
      force_z: generateSensorData(150, 0.40 + base.anomaly_score * 0.15, 0.3),
    },
  };
}
