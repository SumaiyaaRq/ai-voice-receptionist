# AI-Powered Voice Receptionist for Small Businesses

## Project Overview

An AI-powered virtual receptionist designed to handle appointment-related queries, check availability, and assist users through natural language interactions.

The project uses FastAPI for backend development and Google Gemini for natural language understanding and response generation. It is being developed with the goal of integrating appointment management and voice-based interaction into a single system.

## Project Status

Currently in development

The backend foundation and core appointment-management logic are being developed incrementally.

## Tech Stack

Language: Python 3.12

Backend Framework: FastAPI

LLM: Google Gemini

AI Integration: Google Gen AI SDK

Database: SQLite

Package Management: uv

Environment Management: python-dotenv

## Current Features

FastAPI backend with API endpoints.

Gemini integration for natural language processing.

AI receptionist instructions for handling user queries.

Appointment availability checking.

Appointment date and time validation.

Prevention of booking appointments for past dates.

SQLite-based data storage.

Environment variable management for API credentials.

API documentation through Swagger UI.

## Project Structure

```text
ai-voice-receptionist/
│
├── src/
│   └── ai_voice_receptionist/
│       ├── main.py
│       └── services/
│           ├── appointment_service.py
│           └── llm_service.py
│
├── .env
├── .gitignore
├── .python-version
├── pyproject.toml
├── uv.lock
└── README.md
```

*Note: The structure above highlights the main backend files. The frontend directory and other files may vary depending on the current repository structure.*

## Getting Started

### Prerequisites

- Python 3.12
- uv package manager
- Google Gemini API key

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ai-voice-receptionist
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

Replace the placeholder with your Gemini API key. Never commit your `.env` file or expose API credentials.

### 4. Start the Backend

```bash
uv run fastapi dev src/ai_voice_receptionist/main.py
```

### 5. Access the API

Once the server is running, open:

- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI Schema:** http://127.0.0.1:8000/openapi.json

Run the frontend using its own development command and configuration.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Checks backend health |
| POST | `/message` | Processes user messages through the receptionist workflow |

Refer to the Swagger UI for the current request and response schemas.

## Appointment Management

The appointment service is designed to support:

- Checking appointment availability
- Validating appointment dates and times
- Rejecting past-date bookings
- Managing appointment records using SQLite
- Enforcing business-hour and working-day constraints

The exact booking workflow should be verified against the current implementation before treating every capability as production-ready.

## Development Roadmap

- [x] Set up the Python project and backend structure
- [x] Configure FastAPI endpoints
- [x] Integrate Google Gemini
- [x] Implement the initial appointment service
- [x] Add appointment date validation
- [x] Establish the SQLite database foundation
- [x] Connect the frontend to the backend
- [ ] Complete and test the end-to-end appointment workflow
- [ ] Strengthen Gemini tool-calling and execution handling
- [ ] Complete appointment booking, cancellation, and rescheduling flows
- [ ] Add comprehensive automated tests
- [ ] Integrate voice input and output
- [ ] Evaluate deployment options
