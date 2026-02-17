// Use same hostname as the page so session cookies work (localhost vs 127.0.0.1 must match)
function getApiBase() {
  if (import.meta.env.VITE_API_BASE) return import.meta.env.VITE_API_BASE;
  if (typeof window !== "undefined" && window.location?.hostname) {
    return `http://${window.location.hostname}:5000/api`;
  }
  return "http://localhost:5000/api";
}
const API_BASE = getApiBase();

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = data?.error || `Request failed (${res.status})`;
    throw new Error(msg);
  }
  return data;
}

export const api = {
  me: () => request("/auth/me"),
  signup: (username, password) =>
    request("/auth/signup", {
      method: "POST",
      body: JSON.stringify({ username, password })
    }),
  login: (username, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    }),
  logout: () => request("/auth/logout", { method: "POST" }),
  getTrending: () => request("/trending"),
  fetchNews: (keyword) =>
    request("/fetch-news", {
      method: "POST",
      body: JSON.stringify({ keyword })
    }),
  analyze: (newsText, topic) =>
    request("/analyze", {
      method: "POST",
      body: JSON.stringify({ news_text: newsText, topic })
    }),
  getHistory: () => request("/history"),
  admin: {
    login: (username, password) =>
      request("/admin/login", {
        method: "POST",
        body: JSON.stringify({ username, password })
      }),
    logout: () => request("/admin/logout", { method: "POST" }),
    me: () => request("/admin/me"),
    getUsers: () => request("/admin/users"),
    getSearches: () => request("/admin/searches"),
    getStatistics: () => request("/admin/statistics"),
    getActivity: (limit = 100, offset = 0) =>
      request(`/admin/activity?limit=${limit}&offset=${offset}`),
    exportAll: () => request("/admin/export")
  }
};

