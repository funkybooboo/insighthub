# Developer Guide: Chat

This document provides a technical guide to the Chat feature.

## Core Components

The Chat feature is composed of two primary sub-domains: `session` and `message`. The main `ChatService` acts as a facade, coordinating the services of these two sub-domains.

- **Main Service Facade:** `src/domains/workspace/chat/service.py`
- **Session Management:** `src/domains/workspace/chat/session/`
  - Service: `service.py`
  - DTOs: `dtos.py`
- **Message Management:** `src/domains/workspace/chat/message/`
  - Service: `service.py`
  - DTOs: `dtos.py`

## Service Logic

The chat functionality is split across three services:

1.  **`ChatService`:** This is the high-level service that the rest of the application interacts with. It delegates session creation to `ChatSessionService` and message handling to `ChatMessageService`.

2.  **`ChatSessionService`:** This service is responsible for the lifecycle of a chat session. It handles creating, retrieving, and deleting sessions.

3.  **`ChatMessageService`:** This is where the core RAG logic is triggered.

### Message Handling Workflow (`ChatMessageService`)

The `add_message` method (or similar) in `ChatMessageService` is the most critical part of the feature.

1.  **Receive Message:** It receives a DTO containing the `session_id` and the user's message content.
2.  **Save Human Message:** It first creates and saves the `HUMAN` message to the database to persist the user's query.
3.  **Build RAG Config:** It retrieves the workspace associated with the session to get the configured RAG pipeline settings.
4.  **Execute RAG Query:** It constructs a query object and executes the appropriate RAG workflow (e.g., `QueryVectorWorkflow`). This workflow is responsible for:
    a. Retrieving relevant document chunks from the index.
    b. Calling the configured LLM with the context and query.
    c. Returning the generated response.
5.  **Save AI Message:** It saves the response from the RAG workflow as a new `AI` message in the database, associated with the same session.
6.  **Return Response:** It returns the newly created AI message.

## Data Structures (DTOs)

Each sub-domain has its own set of DTOs for clear data contracts.

- **`session/dtos.py`**:
  - `CreateChatSessionDTO`: Data to create a new session (e.g., `workspace_id`).
  - `ChatSessionResponse`: The standard representation of a session.

- **`message/dtos.py`**:
  - `CreateChatMessageDTO`: Data to add a new message to a session (e.g., `session_id`, `message` content).
  - `ChatMessageResponse`: The standard representation of a message, including its type (`HUMAN` or `AI`).

## Design Rationale

The separation into `session` and `message` services follows the Single Responsibility Principle.
- `ChatSessionService` only cares about managing the container for the conversation.
- `ChatMessageService` only cares about the logic of handling a single turn in the conversation, which includes the complex RAG interaction.
- `ChatService` provides a simplified, high-level API to the rest of the application, hiding the underlying complexity.
