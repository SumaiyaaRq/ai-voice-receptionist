
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


export async function getAppointments(filters = {}) {
  const params = new URLSearchParams();

  if (filters.appointment_date) {
    params.set("appointment_date", filters.appointment_date);
  }

  if (filters.status) {
    params.set("status", filters.status);
  }

  const query = params.toString();
  const url = `${API_BASE_URL}/appointments${query ? `?${query}` : ""}`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch appointments: ${response.status}`);
  }

  return await response.json();
}

export async function cancelAppointment(appointmentId) {
  const response = await fetch(
    `${API_BASE_URL}/appointments/${appointmentId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to cancel appointment: ${response.status}`);
  }

  return await response.json();
}
