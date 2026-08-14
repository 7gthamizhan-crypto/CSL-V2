import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1';

export const api = {
  // Dashboard
  getDashboardSummary: () => axios.get(`${API_BASE}/dashboard`).then(res => res.data),
  getDashboardCharts: () => axios.get(`${API_BASE}/dashboard/charts`).then(res => res.data),

  // Containers
  getContainers: (params) => axios.get(`${API_BASE}/containers`, { params }).then(res => res.data),
  getContainerById: (id) => axios.get(`${API_BASE}/containers/${id}`).then(res => res.data),
  createContainer: (data) => axios.post(`${API_BASE}/containers`, data).then(res => res.data),
  deleteContainer: (id) => axios.delete(`${API_BASE}/containers/${id}`).then(res => res.data),

  // Risk & Readiness
  getRiskDetails: (id) => axios.get(`${API_BASE}/risk/${id}`).then(res => res.data),
  recalculateRisk: (id) => axios.post(`${API_BASE}/risk/calculate/${id}`).then(res => res.data),
  getReadiness: (id) => axios.get(`${API_BASE}/readiness/${id}`).then(res => res.data),

  // Schedule
  generateSchedule: () => axios.post(`${API_BASE}/schedule/generate`).then(res => res.data),
  resetSchedule: () => axios.post(`${API_BASE}/schedule/reset`).then(res => res.data),
  getSchedules: () => axios.get(`${API_BASE}/schedule`).then(res => res.data),

  // Resources CRUD & Toggles
  getOfficers: () => axios.get(`${API_BASE}/officers`).then(res => res.data),
  createOfficer: (data) => axios.post(`${API_BASE}/officers`, data).then(res => res.data),
  toggleOfficerAvailability: (id) => axios.patch(`${API_BASE}/officers/${id}/toggle-availability`).then(res => res.data),
  deleteOfficer: (id) => axios.delete(`${API_BASE}/officers/${id}`).then(res => res.data),

  getBays: () => axios.get(`${API_BASE}/bays`).then(res => res.data),
  createBay: (data) => axios.post(`${API_BASE}/bays`, data).then(res => res.data),
  toggleBayStatus: (id) => axios.patch(`${API_BASE}/bays/${id}/toggle-status`).then(res => res.data),
  deleteBay: (id) => axios.delete(`${API_BASE}/bays/${id}`).then(res => res.data),

  getScanners: () => axios.get(`${API_BASE}/scanners`).then(res => res.data),
  createScanner: (data) => axios.post(`${API_BASE}/scanners`, data).then(res => res.data),
  deleteScanner: (id) => axios.delete(`${API_BASE}/scanners/${id}`).then(res => res.data),

  // Reports
  getReports: () => axios.get(`${API_BASE}/reports`).then(res => res.data),

  // Simulator
  runSimulation: (data) => axios.post(`${API_BASE}/simulator/run`, data).then(res => res.data),

  // Settings & Reset
  getSettings: () => axios.get(`${API_BASE}/settings`).then(res => res.data),
  updateSetting: (id, data) => axios.put(`${API_BASE}/settings/${id}`, data).then(res => res.data),
  resetAllDemoData: () => axios.post(`${API_BASE}/reset-demo-data`).then(res => res.data)
};
