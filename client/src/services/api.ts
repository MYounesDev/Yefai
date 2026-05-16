import axios from 'axios';
import { config } from '@/config';

// ===== MOCK IMPORTS =====
import { mockLogin, mockCurrentUser, mockOrganizations, mockOrgMembers, mockSupportTickets } from './mock/auth';
import { mockDashboardOverview, mockHealthStatus, mockFactoryOverview } from './mock/dashboard';
import { mockAnomalies, getAnomalyDetailById } from './mock/anomalies';
import { getMockPrediction } from './mock/predictions';
import { mockSparePartsCatalog, mockInventorySnapshots, mockPartTickets, mockPurchaseOrders, mockCrisisScore } from './mock/spareParts';
import { mockSuppliers, getAlternativeSuppliers } from './mock/suppliers';
import { mockChatSessions, getMockResponse } from './mock/chat';
import { mockNotificationLogs } from './mock/notifications';

// ===== AXIOS INSTANCE =====

const apiClient = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((cfg) => {
  if (typeof window !== 'undefined') {
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const { state } = JSON.parse(authStorage);
        if (state?.token) cfg.headers.Authorization = `Bearer ${state.token}`;
      }
      const orgStorage = localStorage.getItem('org-storage');
      if (orgStorage) {
        const { state } = JSON.parse(orgStorage);
        if (state?.activeOrgId) cfg.headers['X-Organization-Id'] = state.activeOrgId;
      }
    } catch {
      // ignore
    }
  }
  return cfg;
});

// ===== GENERIC API CALL WRAPPER =====

async function apiCall<T>(
  requestFn: () => Promise<{ data: T }>,
  mockFn: () => T | Promise<T>,
  endpoint: string
): Promise<T> {
  try {
    const res = await requestFn();
    return res.data;
  } catch {
    if (config.IS_DEV) {
      console.warn(`[DEV MOCK] ${endpoint} — using mock data`);
      return await mockFn();
    }
    throw new Error(`API call failed: ${endpoint}`);
  }
}

// ===== AUTH =====

export async function login(email: string, _password: string) {
  return apiCall(
    () => apiClient.post('/api/auth/login', { email, password: _password }),
    () => ({ user: mockLogin(email), token: 'mock_token_dev_12345' }),
    'POST /api/auth/login'
  );
}

export async function logout() {
  return apiCall(
    () => apiClient.post('/api/auth/logout'),
    () => ({ success: true }),
    'POST /api/auth/logout'
  );
}

export async function getCurrentUser() {
  return apiCall(
    () => apiClient.get('/api/auth/me'),
    () => mockCurrentUser,
    'GET /api/auth/me'
  );
}

export async function register(data: { name: string; email: string; password: string }) {
  return apiCall(
    () => apiClient.post('/api/auth/register', data),
    () => ({ user: mockCurrentUser, token: 'mock_token_dev_12345' }),
    'POST /api/auth/register'
  );
}

export async function forgotPassword(email: string) {
  return apiCall(
    () => apiClient.post('/api/auth/forgot-password', { email }),
    () => ({ success: true }),
    'POST /api/auth/forgot-password'
  );
}

export async function resetPassword(token: string, newPassword: string) {
  return apiCall(
    () => apiClient.post('/api/auth/reset-password', { token, newPassword }),
    () => ({ success: true }),
    'POST /api/auth/reset-password'
  );
}

export async function acceptInvitation(inviteToken: string) {
  return apiCall(
    () => apiClient.post('/api/auth/accept-invite', { inviteToken }),
    () => ({ user: mockCurrentUser, org: mockOrganizations[0], role: 'operator' }),
    'POST /api/auth/accept-invite'
  );
}

// ===== ORGANIZATIONS =====

export async function getMyOrganizations() {
  return apiCall(
    () => apiClient.get('/api/organizations'),
    () => mockOrganizations,
    'GET /api/organizations'
  );
}

export async function getOrganizationDetails(orgId: string) {
  return apiCall(
    () => apiClient.get(`/api/organizations/${orgId}`),
    () => mockOrganizations.find((o) => o.id === orgId) || mockOrganizations[0],
    `GET /api/organizations/${orgId}`
  );
}

export async function updateOrganization(orgId: string, data: Record<string, unknown>) {
  return apiCall(
    () => apiClient.patch(`/api/organizations/${orgId}`, data),
    () => mockOrganizations[0],
    `PATCH /api/organizations/${orgId}`
  );
}

// ===== MEMBERS =====

export async function getOrgMembers(_orgId: string) {
  return apiCall(
    () => apiClient.get(`/api/organizations/${_orgId}/members`),
    () => mockOrgMembers,
    `GET /api/organizations/${_orgId}/members`
  );
}

export async function inviteMember(orgId: string, data: { email: string; role: string }) {
  return apiCall(
    () => apiClient.post(`/api/organizations/${orgId}/members/invite`, data),
    () => ({ success: true }),
    `POST /api/organizations/${orgId}/members/invite`
  );
}

export async function updateMemberRole(orgId: string, userId: string, role: string) {
  return apiCall(
    () => apiClient.patch(`/api/organizations/${orgId}/members/${userId}`, { role }),
    () => ({ role }),
    `PATCH /api/organizations/${orgId}/members/${userId}`
  );
}

export async function removeMember(orgId: string, userId: string) {
  return apiCall(
    () => apiClient.delete(`/api/organizations/${orgId}/members/${userId}`),
    () => ({ success: true }),
    `DELETE /api/organizations/${orgId}/members/${userId}`
  );
}

// ===== ADMIN =====

export async function adminListOrganizations(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/admin/organizations', { params }),
    () => mockOrganizations,
    'GET /api/admin/organizations'
  );
}

export async function adminCreateOrganization(data: Record<string, unknown>) {
  return apiCall(
    () => apiClient.post('/api/admin/organizations', data),
    () => ({ ...mockOrganizations[0], id: `org_new_${Date.now()}` }),
    'POST /api/admin/organizations'
  );
}

export async function adminGetOrganization(orgId: string) {
  return apiCall(
    () => apiClient.get(`/api/admin/organizations/${orgId}`),
    () => ({ org: mockOrganizations[0], members: mockOrgMembers }),
    `GET /api/admin/organizations/${orgId}`
  );
}

export async function adminListUsers(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/admin/users', { params }),
    () => mockOrgMembers,
    'GET /api/admin/users'
  );
}

export async function adminListSupportTickets(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/admin/support-tickets', { params }),
    () => mockSupportTickets,
    'GET /api/admin/support-tickets'
  );
}

export async function adminResolveSupportTicket(ticketId: string, resolution: string) {
  return apiCall(
    () => apiClient.post(`/api/admin/support-tickets/${ticketId}/resolve`, { resolution }),
    () => ({ success: true }),
    `POST /api/admin/support-tickets/${ticketId}/resolve`
  );
}

export async function adminGetPlatformStats() {
  return apiCall(
    () => apiClient.get('/api/admin/stats'),
    () => ({ total_orgs: mockOrganizations.length, total_users: 42, active_orgs: 5, tickets_open: 2 }),
    'GET /api/admin/stats'
  );
}

// ===== DASHBOARD =====

export async function getDashboardOverview() {
  return apiCall(
    () => apiClient.get('/api/dashboard/overview'),
    () => mockDashboardOverview,
    'GET /api/dashboard/overview'
  );
}

export async function getHealthStatus() {
  return apiCall(
    () => apiClient.get('/api/health'),
    () => mockHealthStatus,
    'GET /api/health'
  );
}

export async function getFactoryOverview() {
  return apiCall(
    () => apiClient.get('/api/factory/overview'),
    () => mockFactoryOverview,
    'GET /api/factory/overview'
  );
}

// ===== ANOMALIES =====

export async function getAnomalies(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/anomalies', { params }),
    () => {
      let results = [...mockAnomalies];
      if (params?.severity) results = results.filter((a) => a.severity === params.severity);
      if (params?.wear_type) results = results.filter((a) => a.wear_type === params.wear_type);
      if (params?.machine_id) results = results.filter((a) => a.machine_id === params.machine_id);
      const limit = (params?.limit as number) || results.length;
      return results.slice(0, limit);
    },
    'GET /api/anomalies'
  );
}

export async function getAnomalyById(id: string) {
  return apiCall(
    () => apiClient.get(`/api/anomalies/${id}`),
    () => getAnomalyDetailById(id),
    `GET /api/anomalies/${id}`
  );
}

export async function runAnomalibPredict(_formData: FormData) {
  return apiCall(
    () => apiClient.post('/api/anomalib/predict', _formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
    () => ({ anomaly_score: 0.72, wear_type: 'flank_wear', estimated_wear_um: 145 }),
    'POST /api/anomalib/predict'
  );
}

// ===== PREDICTIONS =====

export async function getFactoryOverviewPredictions() {
  return apiCall(
    () => apiClient.get('/api/predictions/factory'),
    () => mockFactoryOverview,
    'GET /api/predictions/factory'
  );
}

export async function getPrediction(machineId: string) {
  return apiCall(
    () => apiClient.get(`/api/predictions/${machineId}`),
    () => getMockPrediction(machineId),
    `GET /api/predictions/${machineId}`
  );
}

export async function recalculatePrediction(machineId: string) {
  return apiCall(
    () => apiClient.post(`/api/predictions/${machineId}/recalculate`),
    () => getMockPrediction(machineId),
    `POST /api/predictions/${machineId}/recalculate`
  );
}

// ===== SPARE PARTS =====

export async function getSparePartsCatalog() {
  return apiCall(
    () => apiClient.get('/api/spare-parts/catalog'),
    () => mockSparePartsCatalog,
    'GET /api/spare-parts/catalog'
  );
}

export async function getInventorySnapshots(partId?: string) {
  return apiCall(
    () => apiClient.get('/api/spare-parts/inventory', { params: partId ? { part_id: partId } : {} }),
    () => partId ? mockInventorySnapshots.filter((s) => s.part_id === partId) : mockInventorySnapshots,
    'GET /api/spare-parts/inventory'
  );
}

export async function getPartTickets(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/spare-parts/tickets', { params }),
    () => mockPartTickets,
    'GET /api/spare-parts/tickets'
  );
}

export async function getPurchaseOrders(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/spare-parts/purchase-orders', { params }),
    () => mockPurchaseOrders,
    'GET /api/spare-parts/purchase-orders'
  );
}

export async function approvePurchaseOrder(poId: string) {
  return apiCall(
    () => apiClient.post(`/api/spare-parts/purchase-orders/${poId}/approve`),
    () => ({ success: true, po_id: poId, status: 'approved' }),
    `POST /api/spare-parts/purchase-orders/${poId}/approve`
  );
}

export async function rejectPurchaseOrder(poId: string) {
  return apiCall(
    () => apiClient.post(`/api/spare-parts/purchase-orders/${poId}/reject`),
    () => ({ success: true, po_id: poId, status: 'rejected' }),
    `POST /api/spare-parts/purchase-orders/${poId}/reject`
  );
}

export async function getAlternativeSuppliersForPart(partId: string) {
  return apiCall(
    () => apiClient.get(`/api/spare-parts/${partId}/suppliers`),
    () => getAlternativeSuppliers(partId),
    `GET /api/spare-parts/${partId}/suppliers`
  );
}

export async function getAllSuppliers() {
  return apiCall(
    () => apiClient.get('/api/suppliers'),
    () => mockSuppliers,
    'GET /api/suppliers'
  );
}

export async function getCrisisScore(imageId: string) {
  return apiCall(
    () => apiClient.get(`/api/spare-parts/crisis-score/${imageId}`),
    () => mockCrisisScore,
    `GET /api/spare-parts/crisis-score/${imageId}`
  );
}

// ===== CHAT =====

export async function getChatSessions() {
  return apiCall(
    () => apiClient.get('/api/chat/sessions'),
    () => mockChatSessions,
    'GET /api/chat/sessions'
  );
}

export async function getChatSessionById(sessionId: string) {
  return apiCall(
    () => apiClient.get(`/api/chat/sessions/${sessionId}`),
    () => mockChatSessions.find((s) => s.id === sessionId) || mockChatSessions[0],
    `GET /api/chat/sessions/${sessionId}`
  );
}

export async function sendChatMessage(sessionId: string, message: string) {
  return apiCall(
    () => apiClient.post('/api/chat/message', { session_id: sessionId, message }),
    async () => {
      await new Promise((r) => setTimeout(r, 600));
      const response = getMockResponse(message);
      return {
        id: `msg_${Date.now()}`,
        session_id: sessionId,
        timestamp: new Date().toISOString(),
        ...response,
      };
    },
    'POST /api/chat/message'
  );
}

export async function searchHybrid(query: string, _filters?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.post('/api/search/hybrid', { query, filters: _filters }),
    () => Array.from({ length: 5 }, (_, i) => ({
      image_id: `img_${String(i + 1).padStart(4, '0')}`,
      set: `set_${i + 1}`,
      wear_level: parseFloat((Math.random() * 180 + 20).toFixed(1)),
      machine_id: `M-0${i + 1}`,
      anomaly_score: parseFloat((Math.random() * 0.5 + 0.5).toFixed(3)),
      similarity: parseFloat((0.95 - i * 0.05).toFixed(2)),
    })),
    'POST /api/search/hybrid'
  );
}

// ===== NOTIFICATIONS =====

export async function getNotificationLogs(params?: Record<string, unknown>) {
  return apiCall(
    () => apiClient.get('/api/notifications/logs', { params }),
    () => mockNotificationLogs,
    'GET /api/notifications/logs'
  );
}

export async function triggerAnomalyNotification(anomalyId: string) {
  return apiCall(
    () => apiClient.post(`/api/notifications/trigger/${anomalyId}`),
    async () => {
      await new Promise((r) => setTimeout(r, 500));
      return { success: true, channels: ['telegram', 'email'], message_id: `msg_${Date.now()}` };
    },
    `POST /api/notifications/trigger/${anomalyId}`
  );
}

// ===== NOVAVISION =====

export async function getNovaVisionHealth() {
  return apiCall(
    () => apiClient.get('/api/novavision/health'),
    () => ({ status: 'healthy', container: 'running', version: '2.1.0' }),
    'GET /api/novavision/health'
  );
}

export async function getNovaVisionModels() {
  return apiCall(
    () => apiClient.get('/api/novavision/models'),
    () => ([{ id: 'patchcore_v1', name: 'PatchCore v1', status: 'loaded', accuracy: 0.997 }]),
    'GET /api/novavision/models'
  );
}
