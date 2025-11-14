import axios from 'axios';

// Create an 'instance' of axios
const api = axios.create({
  baseURL: 'http://127.0.0.1:5000/api', // Your backend's base URL
});

export default api;
