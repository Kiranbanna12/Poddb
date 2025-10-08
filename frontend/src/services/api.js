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
  const token = localStorage.getItem('auth_token');
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

// YouTube API Integration
export const fetchYouTubePlaylist = async (playlistUrl) => {
  const response = await api.post('/youtube/fetch-playlist', { playlist_url: playlistUrl });
  return response.data;
};

export const fetchYouTubeVideo = async (videoUrl) => {
  const response = await api.post('/youtube/fetch-video', { video_url: videoUrl });
  return response.data;
};

// Smart Search APIs
export const searchCategories = async (query = '', limit = 10) => {
  const response = await api.get(`/search/categories?q=${query}&limit=${limit}`);
  return response.data;
};

export const addNewCategory = async (name, description = null, icon = null) => {
  const params = new URLSearchParams();
  params.append('name', name);
  if (description) params.append('description', description);
  if (icon) params.append('icon', icon);
  
  const response = await api.post(`/search/categories/add?${params.toString()}`);
  return response.data;
};

export const searchLanguages = async (query = '', limit = 10) => {
  const response = await api.get(`/search/languages?q=${query}&limit=${limit}`);
  return response.data;
};

export const addNewLanguage = async (code, name, nativeName = null) => {
  const params = new URLSearchParams();
  params.append('code', code);
  params.append('name', name);
  if (nativeName) params.append('native_name', nativeName);
  
  const response = await api.post(`/search/languages/add?${params.toString()}`);
  return response.data;
};

export const searchLocations = async (query = '', limit = 10) => {
  const response = await api.get(`/search/locations?q=${query}&limit=${limit}`);
  return response.data;
};

export const addNewLocation = async (location, state = '', country = '') => {
  const params = new URLSearchParams();
  params.append('location', location);
  if (state) params.append('state', state);
  if (country) params.append('country', country);
  
  const response = await api.post(`/search/locations/add?${params.toString()}`);
  return response.data;
};

export const searchPeople = async (query = '', limit = 10) => {
  const response = await api.get(`/search/people?q=${query}&limit=${limit}`);
  return response.data;
};

// People (Team Members) APIs
export const createPerson = async (personData) => {
  const response = await api.post('/people', personData);
  return response.data;
};

export const getPerson = async (personId) => {
  const response = await api.get(`/people/${personId}`);
  return response.data;
};

export const getPersonEpisodes = async (personId) => {
  const response = await api.get(`/people/${personId}/episodes`);
  return response.data;
};

export const assignPersonToEpisodes = async (personId, episodeIds) => {
  const response = await api.post('/people/assign-episodes', {
    person_id: personId,
    episode_ids: episodeIds
  });
  return response.data;
};

export const removePersonFromEpisodes = async (personId, episodeIds) => {
  const response = await api.post(`/people/${personId}/remove-episodes`, episodeIds);
  return response.data;
};

// Episode Management APIs
export const getPodcastEpisodes = async (podcastId) => {
  const response = await api.get(`/podcasts/${podcastId}/episodes`);
  return response.data;
};

export const importEpisodes = async (importData) => {
  const response = await api.post('/episodes/import', importData);
  return response.data;
};

export const createEpisode = async (episodeData) => {
  const response = await api.post('/episodes', episodeData);
  return response.data;
};

export const deleteEpisode = async (episodeId) => {
  const response = await api.delete(`/episodes/${episodeId}`);
  return response.data;
};

export const getEpisodePeople = async (episodeId) => {
  const response = await api.get(`/episodes/${episodeId}/people`);
  return response.data;
};

export default api;