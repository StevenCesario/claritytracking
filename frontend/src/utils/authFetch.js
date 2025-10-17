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
    // 1. Log the user out by clearing the token from storage.
    localStorage.removeItem('authToken');

    // 2. For a full page reload. React's state will re-initialize,
    // our App component will see that there's no token, and it will render 
    // the login screen. This is the cleanest way to reset the entire app state.
    window.location.reload();

    // We throw an error to stop the original promise chain from continuing.
    throw new Error("Sesstion expired. Please log in again.");
  }

  return response;
};

export default authFetch;
