
import { useState , useEffect, useRef } from "react";
import { sendMessage ,getAppointments, cancelAppointment , resetSession} from "./services/api";
import "./App.css";

  const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
function App() {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! Welcome to our reception desk. I can help you book, check, or cancel an appointment. What would you like to do today?",
    },
  ]);

  const chatAreaRef = useRef(null);
  const [isLoading, setIsLoading] = useState(false);

  const [sessionId] = useState(() => {
    return (
      sessionStorage.getItem("voxa_session_id") ||
      (() => {
        const id = crypto.randomUUID();
        sessionStorage.setItem("voxa_session_id", id);
        return id;
      })()
    );
  });

useEffect(() => {
  const chatArea = chatAreaRef.current;

  if (chatArea) {
    chatArea.scrollTop = chatArea.scrollHeight;
  }
}, [messages, isLoading]);

const [activeView, setActiveView] = useState("reception");
const [appointments, setAppointments] = useState([]);
const [appointmentsLoading, setAppointmentsLoading] = useState(false);
const [appointmentsError, setAppointmentsError] = useState("");
const [appointmentStatus, setAppointmentStatus] = useState("");
const [appointmentDate, setAppointmentDate] = useState("");

const bookedAppointments = appointments.filter(
  (appointment) => appointment.status === "booked"
).length;

const cancelledAppointments = appointments.filter(
  (appointment) => appointment.status === "cancelled"
).length;

const [allAppointments, setAllAppointments] = useState([]);
const [isListening, setIsListening] = useState(false);

const startListening = () => {
  if (!SpeechRecognition) {
    alert("Speech recognition is not supported in this browser.");
    return;
  }

  const recognition = new SpeechRecognition();

  recognition.lang = "en-IN";
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onstart = () => {
    setIsListening(true);
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setMessage(transcript);
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    setIsListening(false);
  };

  recognition.onend = () => {
    setIsListening(false);
  };

  recognition.start();
};

async function loadAllAppointments() {
  try {
    const data = await getAppointments();
    setAllAppointments(data.appointments ?? []);
  } catch (error) {
    console.error("Dashboard appointment loading error:", error);
  }
}


async function loadAppointments() {
  setAppointmentsLoading(true);
  setAppointmentsError("");

  try {
    const filters = {};

    if (appointmentStatus) {
      filters.status = appointmentStatus;
    }

    if (appointmentDate) {
      filters.appointment_date = appointmentDate;
    }

    const data = await getAppointments(filters);
    setAppointments(data.appointments ?? []);
  } catch (error) {
    console.error("Appointment loading error:", error);
    setAppointmentsError("Unable to load appointments. Please try again.");
  } finally {
    setAppointmentsLoading(false);
  }
}

useEffect(() => {
  loadAppointments();
  loadAllAppointments();
}, [activeView, appointmentStatus, appointmentDate]);

  async function handleSendMessage(text = message) {
    const userMessage = text.trim();

    if (!userMessage || isLoading) return;

    setMessages((previous) => [
      ...previous,
      { role: "user", content: userMessage },
    ]);

    setMessage("");
    setIsLoading(true);

    try {
      const data = await sendMessage(sessionId, userMessage);

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: data.response },
      ]);
    } catch (error) {
      console.error("Chat API error:", error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "I'm sorry, I couldn't connect to the receptionist service. Please check whether the backend is running and try again.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h2>Voxa</h2>
            <span>AI Receptionist</span>
          </div>
        </div>

        <div className="sidebar-section">
          <p className="section-label">WORKSPACE</p>
          {/* <button className="nav-item active">◉ &nbsp; Reception</button>
          <button className="nav-item">▣ &nbsp; Appointments</button> */}

          <button
          className={`nav-item ${activeView === "reception" ? "active" : ""}`}
          onClick={() => setActiveView("reception")}
          >
          ◉ &nbsp; Reception
        </button>

        <button
        className={`nav-item ${activeView === "appointments" ? "active" : ""}`}
        onClick={() => setActiveView("appointments")}
        >
        ▣ &nbsp; Appointments
        </button>
          <button className="nav-item">◷ &nbsp; Activity</button>

          <button
        className="new-conversation"
        onClick={async () => {
        try {
        await resetSession(sessionId);

        setMessages([
        {
          role: "assistant",
          content:
            "Hello! Welcome to our reception desk. I can help you book, check, or cancel an appointment. What would you like to do today?",
        },
        ]);

      setMessage("");
      } catch (error) {
      console.error("Session reset error:", error);
      }
      }}
        >
       + New Conversation
        </button>
        </div>

        <div className="sidebar-bottom">
          <div className="status-dot" />
          <div>
            <strong>System operational</strong>
            <span>Ready to assist</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
            Workspace / {activeView === "reception" ? "Reception" : "Appointments"}
            </p>
            <h1>{activeView === "reception" ? "Reception Desk" : "Appointments"}</h1>
          </div>

          <div className="topbar-right">
            <span className="online-indicator" />
            <span>Assistant online</span>
            <div className="avatar">V</div>
          </div>
        </header>

        <div className="dashboard">
          {activeView === "reception" && (
          <section className="conversation-panel">
            <div className="conversation-heading">
              <div>
                <span className="eyebrow">YOUR VIRTUAL ASSISTANT</span>
                <h2>How can I help today?</h2>
                <p>Manage appointments through a natural conversation.</p>
              </div>
              <div className="assistant-avatar">✦</div>
            </div>

            <div className="chat-area" ref={chatAreaRef}>
              {messages.map((item, index) => (
                <div
                  className={`message ${
                    item.role === "user" ? "user-message" : "assistant-message"
                  }`}
                  key={index}
                >
                  {item.role === "assistant" && (
                    <div className="message-avatar">✦</div>
                  )}

                  <div className="message-content">
                    <span className="message-author">
                      {item.role === "assistant" ? "Voxa" : "You"}
                      {item.role === "assistant" && (
                        <small>AI Assistant</small>
                      )}
                    </span>

                    <div className="message-bubble">{item.content}</div>
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="message assistant-message">
                  <div className="message-avatar">✦</div>
                  <div className="message-content">
                    <span className="message-author">Voxa</span>
                    <div className="message-bubble">Thinking...</div>
                  </div>
                </div>
              )}
            </div>

            <div className="suggestions">
              <span className="suggestion-label">TRY ASKING</span>
              <div className="suggestion-list">
                <button
                  onClick={() =>
                    handleSendMessage("I'd like to book an appointment.")
                  }
                >
                  Book an appointment
                </button>

                <button
                  onClick={() =>
                    handleSendMessage("What appointment slots are available?")
                  }
                >
                  Check availability
                </button>

                <button
                  onClick={() =>
                    handleSendMessage("I'd like to cancel an appointment.")
                  }
                >
                  Cancel a booking
                </button>
              </div>
            </div>

            <form
              className="composer"
              onSubmit={(event) => {
                event.preventDefault();
                handleSendMessage();
              }}
            >
         
              <button
              type="button"
              className={`voice-button ${isListening ? "listening" : ""}`}
              title="Voice input"
              onClick={startListening}> ♩
              </button>

              <input
                value={message}
                onChange={(event) => setMessage(event.target.value)}
                placeholder="Type your message here..."
                aria-label="Your message"
                disabled={isLoading}
              />

              <button
                type="submit"
                className="send-button"
                aria-label="Send message"
                disabled={isLoading || !message.trim()}
              >
                ↑
              </button>
            </form>

            <p className="privacy-note">
              AI-powered assistance · Your conversation is handled securely
            </p>
          </section> )}

          
        {activeView === "appointments" && (
        <section className="conversation-panel appointments-panel">
        <div className="conversation-heading">
        <div>
            <span className="eyebrow">APPOINTMENT MANAGEMENT</span>
            <h2>All appointments</h2>
        <p>View, filter, and manage your bookings.</p>
        </div>
        <div className="assistant-avatar">▣</div>
        </div>

      <div className="appointment-filters">
      <input
        type="date"
        value={appointmentDate}
        onChange={(event) => setAppointmentDate(event.target.value)}
        aria-label="Filter by appointment date"
      />

      <select
        value={appointmentStatus}
        onChange={(event) => setAppointmentStatus(event.target.value)}
        aria-label="Filter by appointment status"
      >
        <option value="">All statuses</option>
        <option value="booked">Booked</option>
        <option value="cancelled">Cancelled</option>
      </select>

      <button type="button" onClick={loadAppointments}>
        Refresh
      </button>
    </div>

    <div className="appointments-list">
      {appointmentsLoading ? (
        <p>Loading appointments...</p>
      ) : appointmentsError ? (
        <p role="alert">{appointmentsError}</p>
      ) : appointments.length === 0 ? (
        <p>No appointments found for these filters.</p>
      ) : (
        appointments.map((appointment) => (
          <div
            className="appointment-item"
            key={appointment.id}
          >
            <div className="appointment-info">
              <div className="appointment-id">
              Appointment #{appointment.id}
            </div>
              <strong>
                {appointment.customer_name || "Customer"}
              </strong>
              <p>
                {appointment.appointment_date} ·{" "}
                {appointment.appointment_time}
              </p>
              <span className="appointment-status">
                {appointment.status}
              </span>
            </div>

            {appointment.status === "booked" && (
              <button
                type="button"
                onClick={async () => {
                  try {
                    await cancelAppointment(appointment.id);
                    await loadAppointments();
                  } catch (error) {
                    console.error("Cancellation error:", error);
                    setAppointmentsError(
                      "Unable to cancel this appointment. Please try again."
                    );
                  }
                }}
              >
                Cancel
              </button>
            )}
          </div>
        ))
         )}
      </div>
      </section>
      )}


          <aside className="right-panel">
            <div className="panel-heading">
              <div>
                <span className="eyebrow">OVERVIEW</span>
                <h3>Reception insights</h3>
              </div>
              <span className="live-badge">LIVE</span>
            </div>

            <div className="insight-card">
              <div className="insight-icon purple">▣</div>
              <div>
                <span>Today's appointments</span>
                <h2>{bookedAppointments}</h2>
                <small>{cancelledAppointments} cancelled</small>
              </div>
            </div>

            <div className="insight-card">
              <div className="insight-icon green">✓</div>
              <div>
                <span>Assistant status</span>
                <h2 className="status-text">
                  {isLoading ? "Processing" : "Ready"}
                </h2>
                <small>
                  {isLoading
                    ? "Generating a response..."
                    : "Waiting for your message"}
                </small>
              </div>
            </div>

            <div className="hours-card">
              <span className="eyebrow">BUSINESS HOURS</span>
              <h3>We're here to help</h3>
              <div className="hours-row">
                <span>Monday – Friday</span>
                <strong>09:00 – 17:00</strong>
              </div>
              <div className="hours-row">
                <span>Saturday – Sunday</span>
                <strong className="closed">Closed</strong>
              </div>
            </div>

            <div className="tip-card">
              <div className="tip-icon">✧</div>
              <div>
                <strong>Designed for natural conversations</strong>
                <p>
                  Simply tell the assistant what you need. No complicated
                  forms required.
                </p>
              </div>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;
