# AI Backend API Architecture

```text
                Client
                   │
                   ▼
          FastAPI REST API
                   │
      ┌────────────┼────────────┐
      ▼            ▼            ▼
 Authentication   Chat API    Health API
      │            │
      ▼            ▼
 JWT Validation  Redis Memory
      │            │
      └──────┬─────┘
             ▼
      OpenAI Service
             │
             ▼
      Streaming Response
```

```text
Client
   │
   ▼
Route
   │
   ▼
Conversation Service
   │
   ├────────► PostgreSQL
   │
   └────────► Redis
                  │
                  ▼
              OpenAI
```

## Request Flow

1. User logs in and receives a JWT.
2. Client sends the JWT with each protected request.
3. FastAPI validates the JWT.
4. Chat history is loaded from Redis using the authenticated user and session ID.
5. The request is sent to OpenAI.
6. The response is streamed back to the client.
7. Updated conversation history is saved back to Redis.
