import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Token ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: (username, password) =>
    api.post('/auth/login/', { username, password }),
  
  register: (username, password, email) =>
    api.post('/auth/register/', { username, password, email }),
  
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
  },
};

// Dataset API
export const datasetAPI = {
  list: () => api.get('/datasets/'),
  
  get: (id) => api.get(`/datasets/${id}/`),
  
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/datasets/upload/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  getAnalytics: (id) => api.get(`/datasets/${id}/analytics/`),
  
  downloadReport: (id) => {
    return api.get(`/datasets/${id}/report/`, {
      responseType: 'blob',
    });
  },
};

export default api;
