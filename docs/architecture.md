# AI Backend API Architecture

```text
                Client
                   │
                   ▼
              FastAPI API
                   │
        JWT Authentication
                   │
                   ▼
        Conversation Service
         │        │        │
         ▼        ▼        ▼
   User Service  Cache   Title Service
                   │
            Conversation Repository
                   │
                   ▼
             PostgreSQL
                   │
                   ▼
                Redis
                   │
                   ▼
             OpenAI GPT-4o
```

```text
Client
   │
   ▼
FastAPI Routes
   │
   ▼
JWT Authentication
   │
   ▼
Conversation Service
   │
   ├──────────────┐
   ▼              ▼
User Service   Title Service
   │              │
   ▼              ▼
Conversation Repository
   │
   ├──────────────┐
   ▼              ▼
Message Service  Cache Service
   │              │
   ▼              ▼
 PostgreSQL      Redis
        \        /
         \      /
          ▼    ▼
        OpenAI GPT
```

## Request Flow

1. User logs in and receives a JWT.
2. Client sends the JWT with each protected request.
3. FastAPI validates the JWT.
4. Chat history is loaded from Redis using the authenticated user and session ID.
5. The request is sent to OpenAI.
6. The response is streamed back to the client.
7. Updated conversation history is saved back to Redis.
