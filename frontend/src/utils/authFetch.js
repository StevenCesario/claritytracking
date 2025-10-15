// This is our "Secure Courier". It's a wrapper around the native `fetch`
// that automatically includes the user's JWT token in the Authorization header.

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const authFetch = async (url, options = {}) => {
  // On every request, it reads the token from localStorage.
  const token = localStorage.getItem('authToken');

  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // If a token exists, it's added to the headers as a Bearer token.
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // It then makes the actual fetch call with the combined options and headers.
  const response = await fetch(`${API_BASE_URL}${url}`, { ...options, headers });

  // This is our global "bouncer". If an API call ever returns a 401 Unauthorized,
  // it means the token is invalid or expired. We'll handle this globally later.
  if (response.status === 401) {
    // For now, we just log it. We'll build a global logout handler later.
    console.error("Authentication error: Token is invalid or expired.");
    // In a real app, you'd trigger a logout here.
  }

  return response;
};

export default authFetch;
