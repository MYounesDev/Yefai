import { Role } from '@/types';

export type Permission =
  | 'view:dashboard'
  | 'view:anomalies'
  | 'action:mark_anomaly_reviewed'
  | 'view:predictions'
  | 'action:recalculate_prediction'
  | 'view:spare_parts'
  | 'action:approve_po'
  | 'action:manage_suppliers'
  | 'view:chat'
  | 'view:notifications'
  | 'action:trigger_notification'
  | 'manage:members'
  | 'manage:org_settings'
  | 'admin:manage_orgs'
  | 'admin:manage_users'
  | 'admin:view_tickets'
  | 'admin:platform_settings';

const ROLE_PERMISSIONS: Record<Role, Permission[]> = {
  admin: [
    'admin:manage_orgs',
    'admin:manage_users',
    'admin:view_tickets',
    'admin:platform_settings',
  ],
  manager: [
    'view:dashboard',
    'view:anomalies',
    'action:mark_anomaly_reviewed',
    'view:predictions',
    'action:recalculate_prediction',
    'view:spare_parts',
    'action:approve_po',
    'action:manage_suppliers',
    'view:chat',
    'view:notifications',
    'action:trigger_notification',
    'manage:members',
    'manage:org_settings',
  ],
  operator: [
    'view:dashboard',
    'view:anomalies',
    'view:predictions',
    'view:chat',
    'view:notifications',
  ],
  technician: [
    'view:dashboard',
    'view:anomalies',
    'action:mark_anomaly_reviewed',
    'view:predictions',
    'action:recalculate_prediction',
    'view:spare_parts',
    'view:chat',
    'view:notifications',
  ],
  procurement: [
    'view:spare_parts',
    'action:approve_po',
    'action:manage_suppliers',
    'view:notifications',
    'view:anomalies',
  ],
  viewer: [
    'view:dashboard',
    'view:anomalies',
    'view:predictions',
    'view:spare_parts',
    'view:notifications',
  ],
};

export function hasPermission(role: Role | null | undefined, permission: Permission): boolean {
  if (!role) return false;
  return ROLE_PERMISSIONS[role]?.includes(permission) ?? false;
}

export function canAccessRoute(role: Role | null | undefined, pathname: string): boolean {
  if (!role) return false;

  const routePermissions: { pattern: RegExp; permission: Permission }[] = [
    { pattern: /^\/dashboard/, permission: 'view:dashboard' },
    { pattern: /^\/anomalies/, permission: 'view:anomalies' },
    { pattern: /^\/predictions/, permission: 'view:predictions' },
    { pattern: /^\/spare-parts/, permission: 'view:spare_parts' },
    { pattern: /^\/chat/, permission: 'view:chat' },
    { pattern: /^\/notifications/, permission: 'view:notifications' },
    { pattern: /^\/members/, permission: 'manage:members' },
    { pattern: /^\/settings/, permission: 'manage:org_settings' },
  ];

  const match = routePermissions.find((r) => r.pattern.test(pathname));
  if (!match) return true;
  return hasPermission(role, match.permission);
}

export interface NavItem {
  label: string;
  href: string;
  icon: string;
  permission: Permission;
}

export const ALL_NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: 'LayoutDashboard', permission: 'view:dashboard' },
  { label: 'Anomalies', href: '/anomalies', icon: 'AlertTriangle', permission: 'view:anomalies' },
  { label: 'Predictions', href: '/predictions', icon: 'TrendingUp', permission: 'view:predictions' },
  { label: 'Spare Parts', href: '/spare-parts', icon: 'Package', permission: 'view:spare_parts' },
  { label: 'AI Chat', href: '/chat', icon: 'MessageSquare', permission: 'view:chat' },
  { label: 'Notifications', href: '/notifications', icon: 'Bell', permission: 'view:notifications' },
  { label: 'Members', href: '/members', icon: 'Users', permission: 'manage:members' },
  { label: 'Settings', href: '/settings', icon: 'Settings', permission: 'manage:org_settings' },
];

export function getNavItems(role: Role | null | undefined): NavItem[] {
  if (!role) return [];
  return ALL_NAV_ITEMS.filter((item) => hasPermission(role, item.permission));
}
