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