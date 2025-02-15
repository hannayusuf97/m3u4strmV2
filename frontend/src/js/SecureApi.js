import axios from 'axios';
import getApiBaseUrl from './apiConfig';

// Create an axios instance with default configuration
const secureApi = axios.create({
  baseURL: getApiBaseUrl(),
});

// Add request interceptor to handle authentication
secureApi.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle authentication errors
secureApi.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('access_token');
      
      // Redirect to login page
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default secureApi;