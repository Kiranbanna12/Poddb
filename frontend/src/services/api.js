import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API_BASE = `${BACKEND_URL}/api`;

// Create axios instance
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API functions

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const getTopPodcasts = async (limit = 8) => {
  const response = await api.get(`/podcasts/top?limit=${limit}`);
  return response.data;
};

export const getPodcasts = async (filters = {}) => {
  const params = new URLSearchParams();
  if (filters.category) params.append('category', filters.category);
  if (filters.language) params.append('language', filters.language);
  if (filters.limit) params.append('limit', filters.limit);
  
  const response = await api.get(`/podcasts?${params.toString()}`);
  return response.data;
};

export const getPodcast = async (id) => {
  const response = await api.get(`/podcasts/${id}`);
  return response.data;
};

export const getEpisodes = async (limit = 8) => {
  const response = await api.get(`/episodes?limit=${limit}`);
  return response.data;
};

export const getCategories = async () => {
  const response = await api.get('/categories');
  return response.data;
};

export const getLanguages = async () => {
  const response = await api.get('/languages');
  return response.data;
};

export const getRankings = async (type = 'overall', filters = {}) => {
  const params = new URLSearchParams();
  if (filters.category) params.append('category', filters.category);
  if (filters.language) params.append('language', filters.language);
  if (filters.limit) params.append('limit', filters.limit);
  
  const response = await api.get(`/rankings/${type}?${params.toString()}`);
  return response.data;
};

// Auth APIs
export const register = async (userData) => {
  const response = await api.post('/auth/register', userData);
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
};

export const login = async (credentials) => {
  const response = await api.post('/auth/login', credentials);
  if (response.data.token) {
    localStorage.setItem('token', response.data.token);
    localStorage.setItem('user', JSON.stringify(response.data.user));
  }
  return response.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const getCurrentUser = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

// Contributions API
export const createContribution = async (contributionData) => {
  const response = await api.post('/contributions', contributionData);
  return response.data;
};

export const getUserContributions = async () => {
  const response = await api.get('/contributions');
  return response.data;
};

export default api;