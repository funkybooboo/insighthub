# Tutorial 1: Quick Start - Personal Knowledge Base

Project: Build a searchable knowledge base from personal documents
Time: 15 minutes

## What You'll Build

- Create a workspace for your documents
- Upload 3 sample documents
- Ask questions and get answers
- Test searching your data

## Setup

Verify services are running:

```bash
task health-check
```

All services should report healthy.

## Step 1: Create Workspace

A workspace is a project container. Create one for your knowledge base.

```bash
task cli -- workspace create
```

When prompted, enter:

```
Workspace name: My Knowledge Base
Workspace description: Personal learning materials
```

Output:

```
Workspace created successfully
ID: 1
Name: My Knowledge Base
Description: Personal learning materials
Created: 2025-12-07T10:00:00
```

Workspace created and ready to use.

## Step 2: Create Sample Documents

Create three sample text files inline.

Document 1 - Save as knowledge1.txt:

```
Python is a high-level programming language. It emphasizes code readability
and uses significant whitespace. Python supports multiple programming paradigms
including procedural, object-oriented, and functional programming. The Python
interpreter is available for many platforms including Windows, Mac, and Linux.
```

Document 2 - Save as knowledge2.txt:

```
Docker is a containerization platform that packages applications and dependencies
into isolated containers. Containers are lightweight, portable, and can run on any
system with Docker installed. Docker uses images as templates and containers as
running instances. Common Docker commands include docker build, docker run, and
docker push.
```

Document 3 - Save as knowledge3.txt:

```
Machine learning is a subset of artificial intelligence that enables systems to
learn from data. Supervised learning requires labeled training data. Unsupervised
learning finds patterns in unlabeled data. Reinforcement learning uses rewards and
penalties to guide learning. Neural networks with multiple layers are called deep
learning.
```

## Step 3: Select Workspace

Set this workspace as active:

```bash
task cli -- workspace select
```

When prompted, choose "My Knowledge Base".

Output:

```
Workspace selected: My Knowledge Base
```

Workspace is now active for uploads and chats.

## Step 4: Upload Documents

Upload each document to your workspace for searching.

Upload document 1:

```bash
task cli -- document add knowledge1.txt vector
```

Output:

```
Document added successfully
ID: doc_001
Name: knowledge1.txt
Type: vector
Processed tokens: 45
```

Upload document 2:

```bash
task cli -- document add knowledge2.txt vector
```

Output:

```
Document added successfully
ID: doc_002
Name: knowledge2.txt
Type: vector
Processed tokens: 42
```

Upload document 3:

```bash
task cli -- document add knowledge3.txt vector
```

Output:

```
Document added successfully
ID: doc_003
Name: knowledge3.txt
Type: vector
Processed tokens: 48
```

All three documents now uploaded and ready to search.

## Step 5: Create Chat Session

Create a chat session to ask questions about your documents.

```bash
task cli -- chat create
```

When prompted:

```
Session name: General Questions
Session description: Ask questions about uploaded materials
```

Output:

```
Chat session created successfully
ID: session_001
Name: General Questions
Workspace: My Knowledge Base
```

Chat session ready for queries.

## Step 6: Ask Questions

Query your documents using natural language.

Question 1:

```bash
task cli -- chat message "What programming languages are used for AI?"
```

Output:

```
Session: General Questions
User: What programming languages are used for AI?

Response:
Based on your documents, Python is highlighted as a programming language that
supports multiple paradigms and is widely available. The materials mention Python
in the context of general programming capabilities. Machine learning and AI systems
are also discussed, which often use languages like Python alongside frameworks.

Sources:
- knowledge1.txt (match: 0.82)
- knowledge3.txt (match: 0.71)
```

The system found related documents that matched your question.

Question 2:

```bash
task cli -- chat message "How do I deploy applications?"
```

Output:

```
Session: General Questions
User: How do I deploy applications?

Response:
Your documents mention Docker, which is a containerization platform used for
deployment. Docker packages applications with their dependencies into portable
containers that run on any system. Key Docker commands for deployment include
docker build, docker run, and docker push.

Sources:
- knowledge2.txt (match: 0.88)
```

The search found the Docker document even though you used different words.

## Step 7: Verify Documents

List all documents in your workspace:

```bash
task cli -- document list
```

Output:

```
Documents in workspace: My Knowledge Base

ID        Name           Type   Tokens Status
--------- -------------- ------ ------ --------
doc_001   knowledge1.txt vector 45     indexed
doc_002   knowledge2.txt vector 42     indexed
doc_003   knowledge3.txt vector 48     indexed

Total documents: 3
Total tokens processed: 135
```

All documents indexed and ready to search.

## Testing

Test the system works by running another query:

```bash
task cli -- chat message "Explain machine learning in simple terms"
```

Expected output includes knowledge3.txt with high similarity score. The response
should explain machine learning based on your document content.

## What You Learned

- Creating workspaces to organize projects
- Uploading documents for searching
- Finding related content when asking questions
- Creating chat sessions to ask multiple questions
- How the system matches questions to your documents
