import axios from 'axios';

const API_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Create axios instance with auth interceptor
const api = axios.create({
  baseURL: API_URL,
});

// Add token to all requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================
// CONTRIBUTION REVIEW API
// ============================================

export const getContributionStats = async () => {
  const response = await api.get('/api/admin/contributions/stats');
  return response.data;
};

export const getContributions = async (filters = {}) => {
  const response = await api.get('/api/admin/contributions', { params: filters });
  return response.data;
};

export const getContributionDetails = async (contributionId) => {
  const response = await api.get(`/api/admin/contributions/${contributionId}`);
  return response.data;
};

export const approveContribution = async (contributionId) => {
  const response = await api.post(`/api/admin/contributions/${contributionId}/approve`);
  return response.data;
};

export const rejectContribution = async (contributionId, data) => {
  const response = await api.post(`/api/admin/contributions/${contributionId}/reject`, data);
  return response.data;
};

export const updateContributionStatus = async (contributionId, data) => {
  const response = await api.put(`/api/admin/contributions/${contributionId}/status`, data);
  return response.data;
};

// ============================================
// CONTENT MANAGEMENT - PODCASTS API
// ============================================

export const getAllPodcasts = async (filters = {}) => {
  const response = await api.get('/api/admin/podcasts', { params: filters });
  return response.data;
};

export const getPodcastDetails = async (podcastId) => {
  const response = await api.get(`/api/admin/podcasts/${podcastId}`);
  return response.data;
};

export const updatePodcast = async (podcastId, data) => {
  const response = await api.put(`/api/admin/podcasts/${podcastId}`, data);
  return response.data;
};

export const deletePodcast = async (podcastId, permanent = false) => {
  const response = await api.delete(`/api/admin/podcasts/${podcastId}`, {
    params: { permanent }
  });
  return response.data;
};

// ============================================
// CONTENT MANAGEMENT - EPISODES API
// ============================================

export const getAllEpisodes = async (filters = {}) => {
  const response = await api.get('/api/admin/episodes', { params: filters });
  return response.data;
};

export const updateEpisode = async (episodeId, data) => {
  const response = await api.put(`/api/admin/episodes/${episodeId}`, data);
  return response.data;
};

export const deleteEpisode = async (episodeId) => {
  const response = await api.delete(`/api/admin/episodes/${episodeId}`);
  return response.data;
};

// ============================================
// CONTENT MANAGEMENT - PEOPLE API
// ============================================

export const getAllPeople = async (filters = {}) => {
  const response = await api.get('/api/admin/people', { params: filters });
  return response.data;
};

export const updatePerson = async (personId, data) => {
  const response = await api.put(`/api/admin/people/${personId}`, data);
  return response.data;
};

export const deletePerson = async (personId) => {
  const response = await api.delete(`/api/admin/people/${personId}`);
  return response.data;
};

export const mergePeople = async (personId1, personId2) => {
  const response = await api.post('/api/admin/people/merge', null, {
    params: { person_id1: personId1, person_id2: personId2 }
  });
  return response.data;
};

// ============================================
// SYNC MANAGEMENT API (OLD)
// ============================================

export const getSyncStats = async () => {
  const response = await api.get('/api/admin/sync/stats');
  return response.data;
};

export const getSyncedPlaylists = async (filters = {}) => {
  const response = await api.get('/api/admin/sync/playlists', { params: filters });
  return response.data;
};

export const getSyncHistory = async (filters = {}) => {
  const response = await api.get('/api/admin/sync/history', { params: filters });
  return response.data;
};

export const updateSyncSettings = async (playlistId, settings) => {
  const response = await api.put(`/api/admin/sync/playlists/${playlistId}/settings`, settings);
  return response.data;
};

export const deletePlaylistSync = async (playlistId) => {
  const response = await api.delete(`/api/admin/sync/playlists/${playlistId}`);
  return response.data;
};

// ============================================
// NEW SYNC SYSTEM API
// ============================================

export const getSyncStatus = async () => {
  const response = await api.get('/api/sync/status');
  return response.data;
};

export const getSyncDashboard = async () => {
  const response = await api.get('/api/sync/dashboard');
  return response.data;
};

export const runFullSync = async () => {
  const response = await api.post('/api/sync/run-full-sync');
  return response.data;
};

export const checkNewEpisodes = async () => {
  const response = await api.post('/api/sync/check-new-episodes');
  return response.data;
};

export const syncSinglePodcast = async (podcastId) => {
  const response = await api.post(`/api/sync/sync-podcast/${podcastId}`);
  return response.data;
};

export const recalculateAnalytics = async () => {
  const response = await api.post('/api/sync/recalculate-analytics');
  return response.data;
};

export const getSyncJobs = async (params = {}) => {
  const response = await api.get('/api/sync/jobs', { params });
  return response.data;
};

export const getSyncErrors = async (params = {}) => {
  const response = await api.get('/api/sync/errors', { params });
  return response.data;
};

export const resolveError = async (errorId) => {
  const response = await api.post(`/api/sync/errors/${errorId}/resolve`);
  return response.data;
};

export const getSyncConfig = async () => {
  const response = await api.get('/api/sync/config');
  return response.data;
};

export const updateSyncConfig = async (configKey, configValue) => {
  const response = await api.post('/api/sync/config', {
    config_key: configKey,
    config_value: configValue
  });
  return response.data;
};

export const getApiUsage = async (days = 30) => {
  const response = await api.get('/api/sync/api-usage', { params: { days } });
  return response.data;
};

export const testEmail = async (testEmail = null) => {
  const response = await api.post('/api/sync/test-email', { test_email: testEmail });
  return response.data;
};

export const enableSync = async () => {
  const response = await api.post('/api/sync/enable');
  return response.data;
};

export const disableSync = async () => {
  const response = await api.post('/api/sync/disable');
  return response.data;
};

// ============================================
// ADMIN ACTIVITY LOGS API
// ============================================

export const getActivityLogs = async (filters = {}) => {
  const response = await api.get('/api/admin/activity-logs', { params: filters });
  return response.data;
};

// ============================================
// NOTIFICATIONS API
// ============================================

export const getNotifications = async (unreadOnly = false) => {
  const response = await api.get('/api/admin/notifications', { params: { unread_only: unreadOnly } });
  return response.data;
};

export const markNotificationRead = async (notificationId) => {
  const response = await api.put(`/api/admin/notifications/${notificationId}/read`);
  return response.data;
};

export const markAllNotificationsRead = async () => {
  const response = await api.put('/api/admin/notifications/read-all');
  return response.data;
};

export default {
  // Contribution Review
  getContributionStats,
  getContributions,
  getContributionDetails,
  approveContribution,
  rejectContribution,
  updateContributionStatus,
  
  // Podcasts Management
  getAllPodcasts,
  getPodcastDetails,
  updatePodcast,
  deletePodcast,
  
  // Episodes Management
  getAllEpisodes,
  updateEpisode,
  deleteEpisode,
  
  // People Management
  getAllPeople,
  updatePerson,
  deletePerson,
  mergePeople,
  
  // Sync Management
  getSyncStats,
  getSyncedPlaylists,
  getSyncHistory,
  updateSyncSettings,
  deletePlaylistSync,
  
  // Activity Logs
  getActivityLogs,
  
  // Notifications
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
};
