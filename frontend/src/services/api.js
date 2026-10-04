
const API_BASE_URL = "http://127.0.0.1:8000";

export async function sendMessage(sessionId, message) {
  const response = await fetch(`${API_BASE_URL}/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
    }),
  });

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`);
  }

  return await response.json();
}
