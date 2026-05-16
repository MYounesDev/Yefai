import { UserWithOrgs, Organization, OrgMember, SupportTicket } from '@/types';

export const mockCurrentUser: UserWithOrgs = {
  id: 'usr_001',
  name: 'Ahmet Yılmaz',
  email: 'ahmet@yefai.io',
  avatar_url: undefined,
  created_at: '2026-01-15T10:00:00Z',
  organizations: [
    { org_id: 'org_001', org_name: 'Yılmaz Makina A.Ş.', role: 'manager', joined_at: '2026-01-15' },
    { org_id: 'org_002', org_name: 'Demir Çelik Fabrikası', role: 'operator', joined_at: '2026-03-01' },
    { org_id: 'org_003', org_name: 'Anadolu CNC', role: 'viewer', joined_at: '2026-04-20' },
  ],
};

export const mockAdminUser: UserWithOrgs = {
  id: 'usr_admin',
  name: 'Platform Admin',
  email: 'admin@yefai.io',
  avatar_url: undefined,
  created_at: '2025-12-01T00:00:00Z',
  organizations: [],
};

export const mockOrganizations: Organization[] = [
  { id: 'org_001', name: 'Yılmaz Makina A.Ş.', plan: 'enterprise', member_count: 12, created_at: '2026-01-10T00:00:00Z' },
  { id: 'org_002', name: 'Demir Çelik Fabrikası', plan: 'pro', member_count: 8, created_at: '2026-02-15T00:00:00Z' },
  { id: 'org_003', name: 'Anadolu CNC', plan: 'free', member_count: 3, created_at: '2026-04-01T00:00:00Z' },
  { id: 'org_004', name: 'İstanbul Endüstri A.Ş.', plan: 'pro', member_count: 15, created_at: '2026-01-20T00:00:00Z' },
  { id: 'org_005', name: 'Bursa Otomasyon Ltd.', plan: 'enterprise', member_count: 22, created_at: '2025-11-05T00:00:00Z' },
  { id: 'org_006', name: 'Konya Makina Sanayi', plan: 'free', member_count: 4, created_at: '2026-03-18T00:00:00Z' },
];

export const mockOrgMembers: OrgMember[] = [
  { user_id: 'usr_001', name: 'Ahmet Yılmaz', email: 'ahmet@yilmazmakina.com', role: 'manager', joined_at: '2026-01-15', status: 'active', last_active: '2026-05-16T08:30:00Z' },
  { user_id: 'usr_002', name: 'Fatma Demir', email: 'fatma@yilmazmakina.com', role: 'technician', joined_at: '2026-01-20', status: 'active', last_active: '2026-05-16T07:00:00Z' },
  { user_id: 'usr_003', name: 'Mehmet Kaya', email: 'mehmet@yilmazmakina.com', role: 'operator', joined_at: '2026-02-01', status: 'active', last_active: '2026-05-15T14:00:00Z' },
  { user_id: 'usr_004', name: 'Ayşe Çelik', email: 'ayse@yilmazmakina.com', role: 'procurement', joined_at: '2026-02-10', status: 'active', last_active: '2026-05-16T06:45:00Z' },
  { user_id: 'usr_005', name: 'Ali Öztürk', email: 'ali@yilmazmakina.com', role: 'viewer', joined_at: '2026-03-05', status: 'active', last_active: '2026-05-14T09:00:00Z' },
  { user_id: 'usr_006', name: 'Elif Şahin', email: 'elif@yilmazmakina.com', role: 'technician', joined_at: '2026-03-15', status: 'active', last_active: '2026-05-16T05:30:00Z' },
  { user_id: 'usr_007', name: 'Burak Arslan', email: 'burak@yilmazmakina.com', role: 'operator', joined_at: '2026-04-01', status: 'invited', last_active: undefined },
  { user_id: 'usr_008', name: 'Zeynep Kurt', email: 'zeynep@yilmazmakina.com', role: 'viewer', joined_at: '2026-04-20', status: 'invited', last_active: undefined },
];

export const mockSupportTickets: SupportTicket[] = [
  { id: 'tkt_001', org_id: 'org_002', org_name: 'Demir Çelik Fabrikası', subject: 'AI model not predicting correctly', description: 'The wear prediction model returns 0 for all machines since yesterday.', status: 'open', created_at: '2026-05-15T09:00:00Z' },
  { id: 'tkt_002', org_id: 'org_003', org_name: 'Anadolu CNC', subject: 'Cannot access spare parts dashboard', description: 'Getting a 403 error when navigating to /spare-parts.', status: 'in_progress', created_at: '2026-05-14T14:30:00Z' },
  { id: 'tkt_003', org_id: 'org_001', org_name: 'Yılmaz Makina A.Ş.', subject: 'Telegram notifications not being sent', description: 'Critical alerts are not forwarded to our Telegram channel.', status: 'resolved', created_at: '2026-05-10T10:00:00Z', resolved_at: '2026-05-12T16:00:00Z', resolution: 'Webhook URL was incorrect. Updated and tested successfully.' },
  { id: 'tkt_004', org_id: 'org_004', org_name: 'İstanbul Endüstri A.Ş.', subject: 'Request for data export feature', description: 'We need to export anomaly logs as CSV for our internal reporting.', status: 'open', created_at: '2026-05-13T11:00:00Z' },
  { id: 'tkt_005', org_id: 'org_005', org_name: 'Bursa Otomasyon Ltd.', subject: 'Billing issue — double charged', description: 'Our invoice shows two enterprise plan charges for April.', status: 'closed', created_at: '2026-05-01T08:00:00Z', resolved_at: '2026-05-03T12:00:00Z', resolution: 'Duplicate charge confirmed and refunded.' },
];

export function mockLogin(email: string): UserWithOrgs {
  if (email.toLowerCase().includes('admin')) return mockAdminUser;
  return mockCurrentUser;
}
