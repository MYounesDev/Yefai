import { ChatSession, ChatMessage } from '@/types';

export const mockChatSessions: ChatSession[] = [
  { id: 'sess_001', title: 'Tool Wear Analysis — Set 5', created_at: '2026-05-16T08:00:00Z', updated_at: '2026-05-16T08:45:00Z', message_count: 6 },
  { id: 'sess_002', title: 'Critical Anomaly Investigation', created_at: '2026-05-15T14:00:00Z', updated_at: '2026-05-15T15:30:00Z', message_count: 10 },
  { id: 'sess_003', title: 'Spare Parts Inventory Check', created_at: '2026-05-14T09:00:00Z', updated_at: '2026-05-14T09:20:00Z', message_count: 4 },
  { id: 'sess_004', title: 'Weekly Report Summary', created_at: '2026-05-13T17:00:00Z', updated_at: '2026-05-13T17:10:00Z', message_count: 3 },
  { id: 'sess_005', title: 'Flank Wear Pattern Research', created_at: '2026-05-12T11:00:00Z', updated_at: '2026-05-12T11:45:00Z', message_count: 8 },
];

export const mockInitialMessages: ChatMessage[] = [
  {
    id: 'msg_s',
    session_id: 'sess_001',
    role: 'system',
    content: 'Session started. Context loaded for Yılmaz Makina A.Ş.',
    timestamp: '2026-05-16T08:00:00Z',
  },
];

export const mockAIResponses: Record<string, Omit<ChatMessage, 'id' | 'session_id' | 'timestamp'>> = {
  default: {
    role: 'assistant',
    content: `I analyzed your query against the available sensor data and anomaly records.\n\n**Key findings:**\n- Machine #3 and #6 are currently in **critical** wear state (178µm and 189µm respectively)\n- The dominant wear pattern across the fleet is **flank wear** (55% of anomalies)\n- 3 spare part tickets are at **crisis** level requiring immediate attention\n\nWould you like me to drill down into a specific machine or anomaly?`,
    sources: [
      { label: 'Set 5 / Image 23', similarity: 0.92, anomaly_id: 'anom_003' },
      { label: 'Set 12 / Image 7', similarity: 0.87, anomaly_id: 'anom_007' },
    ],
  },
  wear: {
    role: 'assistant',
    content: `Here are the **top tools by wear level** across the factory:\n\n| Machine | Tool | Wear (µm) | Status |\n|---------|------|-----------|--------|\n| M-06 | Tool-B | 189 | 🔴 Critical |\n| M-03 | Tool-A | 178 | 🔴 Critical |\n| M-04 | Tool-C | 162 | 🟠 Warning |\n| M-07 | Tool-A | 124 | 🟡 Watch |\n| M-02 | Tool-D | 112 | 🟡 Watch |\n\nMachine #6 is the most urgent — at **94.5%** of the 200µm critical threshold with a wear rate of **6.2 µm/hour**.`,
    sources: [
      { label: 'Set 8 / Image 15', similarity: 0.95, anomaly_id: 'anom_001' },
    ],
  },
  stock: {
    role: 'assistant',
    content: `**Current out-of-stock critical parts:**\n\n- **Spindle Bearing XR-9** (p002) — 0 on hand, lead time: 21 days ⚠️ Auto-PO created\n- **Linear Guide LG-15** (p008) — 0 on hand, lead time: 28 days ⚠️ Auto-PO created\n\n**Below reorder point:**\n- Insert Tip A-12 (p001): 2 on hand / 5 reorder point\n- Rotary Encoder RE-6 (p011): 3 on hand / 4 reorder point\n- Collet Chuck CC-20 (p006): 4 on hand / 5 reorder point\n\nI recommend prioritizing the Spindle Bearing — Machine #6 has zero stock with a 95/100 crisis score.`,
  },
};

export function getMockResponse(query: string): Omit<ChatMessage, 'id' | 'session_id' | 'timestamp'> {
  const q = query.toLowerCase();
  if (q.includes('wear') || q.includes('tool') || q.includes('highest')) return mockAIResponses.wear;
  if (q.includes('stock') || q.includes('spare') || q.includes('part')) return mockAIResponses.stock;
  return mockAIResponses.default;
}
