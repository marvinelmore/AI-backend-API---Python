# AI-backend-API---Python

<p align="center">
  <img src="app/assets/dev-tools.png" alt="AI Backend API Banner" width="100%">
</p>

<h1 align="center">AI Backend API</h1>

<p align="center">
Production-ready AI Backend built with FastAPI, OpenAI, Redis, Docker, and JWT Authentication.
</p>

<p align="center">
  <img src="app/assets/AI-backend-API---Python.gif" alt="AI Backend API Gif" width="100%">
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-API-412991?logo=openai)
![Redis](https://img.shields.io/badge/Redis-Database-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker)
![JWT](https://img.shields.io/badge/JWT-Authentication-black?logo=jsonwebtokens)

</p>
A production-style AI backend built with **FastAPI**, **OpenAI**, **Redis**, and **JWT Authentication**.

This project demonstrates modern backend engineering practices, including secure authentication, streaming AI responses, centralized configuration, structured logging, Redis-backed conversation memory, and production-ready API architecture.

---

## Features

* FastAPI REST API
* OpenAI Chat Integration
* Streaming AI Responses
* JWT Authentication
* Redis Conversation Memory
* User-based Chat Sessions
* Centralized Configuration
* Shared Redis Client
* Structured Application Logging
* Global Exception Handling
* Health Check Endpoint
* Swagger/OpenAPI Documentation

---

## Tech Stack

* Python 3.13
* FastAPI
* OpenAI API
* Redis
* JWT
* Pydantic
* Uvicorn
* python-dotenv

---

## Project Structure

```text
app/
├── auth/
├── core/
│   ├── config.py
│   ├── logger.py
│   └── redis_client.py
├── middleware/
├── models/
├── routes/
├── services/
└── main.py
```

---

## API Endpoints

| Method | Endpoint     | Description               |
| ------ | ------------ | ------------------------- |
| POST   | /auth/login  | Generate JWT access token |
| POST   | /chat/stream | Stream AI response        |
| GET    | /health      | Service health check      |

---

## Running the Project

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Redis:

```bash
redis-server
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```
http://127.0.0.1:8000/docs
```

---

## Current Features

* AI chat powered by OpenAI
* Redis-backed memory
* JWT-secured endpoints
* Streaming responses
* Centralized configuration
* Production logging
* Global exception middleware

---

## Planned Improvements

* Docker & Docker Compose
* PostgreSQL integration
* Alembic migrations
* Conversation management
* Retrieval-Augmented Generation (RAG)
* File upload & document chat
* Deployment to the cloud

---

## Author

**Marvin Elmore**

Senior Full Stack Software Engineer

GitHub: https://github.com/marvinelmore
