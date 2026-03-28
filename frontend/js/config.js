/**
 * Backend API base URL — must match where Flask runs (see README).
 * If you serve the UI from another host/port, ensure Flask-CORS allows it.
 */
const API_BASE = "http://127.0.0.1:5000/api/v1";

const TOKEN_KEY = "tm_jwt";

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

function authHeaders() {
  const t = getToken();
  const h = { "Content-Type": "application/json" };
  if (t) h["Authorization"] = "Bearer " + t;
  return h;
}
