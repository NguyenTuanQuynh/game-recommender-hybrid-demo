const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function fetchJSON(url, options = {}) {
  const response = await fetch(url, options);

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Request failed: ${response.status} - ${text}`);
  }

  return response.json();
}

export async function getGames(limit = 20, offset = 0) {
  return fetchJSON(`${API_BASE_URL}/games?limit=${limit}&offset=${offset}`);
}

export async function getGameDetail(gameId) {
  return fetchJSON(`${API_BASE_URL}/games/${gameId}`);
}

export async function searchGames(query, limit = 20, offset = 0) {
  const q = encodeURIComponent(query);
  return fetchJSON(`${API_BASE_URL}/search?q=${q}&limit=${limit}&offset=${offset}`);
}

export async function getHomeRecommendations(userId = "demo_user", limit = 12, offset = 0) {
  return fetchJSON(
    `${API_BASE_URL}/recommend/home?user_id=${encodeURIComponent(userId)}&limit=${limit}&offset=${offset}`
  );
}

export async function getRecentlyWatched(userId = "demo_user", limit = 10, offset = 0) {
  return fetchJSON(
    `${API_BASE_URL}/recommend/recent?user_id=${encodeURIComponent(userId)}&limit=${limit}&offset=${offset}`
  );
}

export async function getSimilarGames(gameId, limit = 10, offset = 0) {
  return fetchJSON(
    `${API_BASE_URL}/recommend/similar/${gameId}?limit=${limit}&offset=${offset}`
  );
}

export async function logEvent(payload) {
  return fetchJSON(`${API_BASE_URL}/events/log`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
}