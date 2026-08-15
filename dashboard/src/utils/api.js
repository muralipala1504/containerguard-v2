export const getAPIURL = () => {
  const apiUrl = import.meta.env.VITE_API_URL;
  if (apiUrl) return apiUrl;
  
  // Default to localhost for dev, or derive from current host for prod
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'http://localhost:3001';
  }
  return window.location.origin.replace(/:\d+$/, ':3001');
};
