import { logEvent } from "../api/client";

const SESSION_KEY = "hybrid_game_demo_session_id";
const USER_ID = "demo_user";

function createSessionId() {
  return `sess_${Math.random().toString(36).slice(2, 10)}`;
}

export function getUserId() {
  return USER_ID;
}

export function getSessionId() {
  let sessionId = localStorage.getItem(SESSION_KEY);

  if (!sessionId) {
    sessionId = createSessionId();
    localStorage.setItem(SESSION_KEY, sessionId);
  }

  return sessionId;
}

export async function safeLogEvent({
  event_type,
  game_id = null,
  event_value = 1.0,
  query = null,
  source = null,
  metadata = {},
}) {
  try {
    return await logEvent({
      user_id: getUserId(),
      event_type,
      game_id,
      event_value,
      query,
      source,
      session_id: getSessionId(),
      metadata: typeof metadata === "string" ? metadata : JSON.stringify(metadata),
    });
  } catch (error) {
    console.error("Failed to log event:", error);
    return null;
  }
}