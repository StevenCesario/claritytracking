// This file acts as our "Ambassador" to the backend API.
// All functions for making API calls will live here.

import authFetch from '../utils/authFetch';

// The base URL for our backend, pulled from an environment variable.
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

/**
 * A helper function to handle common error parsing from our FastAPI backend.
 * It checks if the response was successful and, if not, tries to parse the
 * error detail from the JSON body.
 */
async function handleErrors(response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
    // FastAPI often returns errors in a "detail" key.
    throw new Error(errorData.detail || 'An API error occurred.');
  }
  return response.json();
}

// --- NON-AUTHENTICATED FUNCTIONS ---

/**
 * The recipe for registering a new user.
 * This is a public endpoint, so we use the standard `fetch`.
 */
export async function registerUser(userData) {
  const response = await fetch(`${API_BASE_URL}/api/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userData),
  });
  return handleErrors(response);
}

/**
 * The recipe for logging in a user.
 * This uses the special 'application/x-www-form-urlencoded' content type
 * that OAuth2PasswordRequestForm expects.
 */
export async function loginUser(credentials) {
  const formData = new URLSearchParams();
  formData.append('grant_type', 'password');
  formData.append('username', credentials.email);
  formData.append('password', credentials.password);

  const response = await fetch(`${API_BASE_URL}/api/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  const data = await handleErrors(response);
  // On successful login, we store the token in localStorage. This is a key
  // step for session persistence.
  if (data.access_token) {
    localStorage.setItem('authToken', data.access_token);
  }
  return data;
}

// --- AUTHENTICATED FUNCTIONS ---

/**
 * Fetches all websites for the current logged-in user.
 * Uses our secure authFetch courier.
 */
export async function getWebsites() {
  const response = await authFetch('/api/websites');
  return handleErrors(response);
}

/**
 * Creates a new website for the current logged-in user.
 * Uses our secure authFetch courier.
 */
export async function createWebsite(websiteData) {
  const response = await authFetch('/api/websites', {
    method: 'POST',
    body: JSON.stringify(websiteData),
  });
  return handleErrors(response);
}

/**
 * Creates a new platform connection for a specific website.
 */
export async function createConnection(websiteId, connectionData) {
  const response = await authFetch(`/api/websites/${websiteId}/connections`, {
    method: 'POST',
    body: JSON.stringify(connectionData),
  });
  return handleErrors(response);
}

/**
 * Fetches the event health monitor data for a specific website.
 */
export async function getWebsiteHealth(websiteId) {
  const response = await authFetch(`/api/websites/${websiteId}/health`);
  return handleErrors(response);
}

/**
 * NEW: Fetches the health alerts for a specific website.
 */
export async function getWebsiteAlerts(websiteId) {
  const response = await authFetch(`/api/websites/${websiteId}/alerts`);
  return handleErrors(response);
}