# Todo list

## Workspaces

I am building a system where you can configure your own rag system, 
upload documents and have intelligent converstaions about the topic. 
On the UI you can create new chat sessions but all chat sessions are tied to the same uploaded documents. 
uploaded documents are global for chats. 
I want to create a higher level grouping of documents and chats where the user can upload documents 
and this section of chat sessions will have access to those documents but they can make 
new document groupings and those new groupings will have there own chat sessions.

### **1. Data Modeling (with separate RAG config table)**

**Entities:**

1. **Workspace**

   * `id`
   * `name`
   * `created_at`, `updated_at`

2. **Document**

   * `id`
   * `workspace_id` (foreign key)
   * `filename`
   * `content` or `storage_path`
   * `uploaded_at`

3. **RAG Config**

   * `id`
   * `workspace_id` (foreign key, unique) → ensures one config per workspace
   * `embedding_model`
   * `retriever_type`
   * `chunk_size`
   * Other relevant parameters
   * `created_at`, `updated_at`

4. **Chat Session**

   * `id`
   * `workspace_id` (foreign key)
   * `history` (DB or in-memory cache)
   * `created_at`, `updated_at`

**Relationships:**

* Workspace 1:N Documents
* Workspace 1:1 RAG Config
* Workspace 1:N Chat Sessions

### **2. API / Backend Updates**

1. **Workspace Management**

   * Create / update / delete workspace
   * List all workspaces for a user

2. **Document Management**

   * Upload / delete / list documents per workspace

3. **RAG Config Management**

   * Create / update / retrieve RAG config per workspace
   * Validate parameters
   * Ensure one config per workspace

4. **Chat Session Management**

   * Create / delete / list chat sessions per workspace
   * Retrieve session history

5. **RAG Operations**

   * On chat request:

     * Load workspace’s RAG config
     * Load workspace documents / embeddings
     * Query relevant documents
     * Generate response

### **3. Database Schema Example (PostgreSQL)**

```sql
CREATE TABLE workspace (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE rag_config (
    id SERIAL PRIMARY KEY,
    workspace_id INT UNIQUE REFERENCES workspace(id) ON DELETE CASCADE,
    embedding_model TEXT NOT NULL,
    retriever_type TEXT NOT NULL,
    chunk_size INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document (
    id SERIAL PRIMARY KEY,
    workspace_id INT REFERENCES workspace(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_session (
    id SERIAL PRIMARY KEY,
    workspace_id INT REFERENCES workspace(id) ON DELETE CASCADE,
    history JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### **4. Advantages of Separate RAG Config Table**

* Config can evolve independently of the workspace
* Easier to store history or multiple versions in the future
* Cleaner API endpoints: `GET /workspace/{id}/rag_config`

## Storybook stories

- there should be a story for all main components

## Cypress tests

- rip out playwright
- test main workflows
  - sign up
  - sign in
  - change the background color
  - make a new workspace
  - make a new chat
  - upload a document
  - delete workspace
  - delete chat
  - delete document
  - chat with chatbot

## Clean up types and code

- simplify where possible without loosing functionality
- ensure security
- ensure we validate user inputs
- ensure there are global and local types

## fix bruno tests

- pass security middleware

## mock out more interfaces for rag system

- what are the parts of a graph rag system, name all the algorithms and technologies used
- same for a vector rag system

## restructure and organize files and folders

## update docs

- document features
- document tests
- UML
- user manual
- changelog 
  - https://common-changelog.org/

## more tests

- make sure there is a high test coverage

## ensure stateless processes

- make sure that new server processes or client processes can be launched and destroyed at will without effecting users

## worker processes

- more packages next to client and server? or same folder as server?
- process documents
- pull information from the internet
- run rag system
- prepare for user queries
- rabbitmq
- observer pattern. no pulling

## cache

- redis
- cache where possible
- hit db as little as possible

## preferences page

- change password, email, name, etc... 
- set what the default rag should be

## shared library between server and workers

- processes should be able to rely on the same global shared library
- no duplicate code even between the server and the workers

## figure out env files on client and server

- be able to handle local and production configs

## figure out how to secure secrets in docker

- dont bake secrets into the images

## audit code in ci

- add onto existing ci
- add a task
- test locally

## SLSA

- https://slsa.dev/

## ELK stack

- ELK in docker
- grab streams from all other containers to get logs
- be able to monitor entire system

## make a plain text workflow for project management

- find out a good way to manage the project in plain text documents
- I want something like a kandam board but simple and easy

## be able to run in docker swarm

- if we can run in docker swarm then we can run in k8s
- this will make it easy to deploy the app to a cloud provider of choice later
