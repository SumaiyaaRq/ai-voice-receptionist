
const API_BASE_URL = "http://127.0.0.1:8000";


export async function sendMessage(sessionId, message, signal) {
  const timeoutController = new AbortController();

  const timeoutId = setTimeout(() => {
    timeoutController.abort(
      new DOMException("The request timed out.", "TimeoutError")
    );
  }, 30000);

  const requestSignal = signal
    ? AbortSignal.any([signal, timeoutController.signal])
    : timeoutController.signal;

  try {
    const response = await fetch(`${API_BASE_URL}/message`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        session_id: sessionId,
        message: message,
      }),
      signal: requestSignal,
    });

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (signal?.aborted) {
      throw new DOMException("The request was cancelled.", "AbortError");
    }

    if (timeoutController.signal.aborted) {
      throw new DOMException(
        "The receptionist took too long to respond. Please try again.",
        "TimeoutError"
      );
    }

    throw error;
  } finally {
    clearTimeout(timeoutId);
  }
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

export async function resetSession(sessionId) {
  const response = await fetch(
    `${API_BASE_URL}/sessions/${sessionId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to reset session: ${response.status}`);
  }

  return await response.json();
}
