# Search & Answering Methods

The "Search & Answering Method" is the engine that powers your Workspace. It determines how InsightHub understands your documents and finds answers to your questions. You can choose a method when you create a Workspace.

Each method is suited for different kinds of tasks.

## Semantic Search (Vector)

This is the most common and versatile method. Think of it as a super-powered keyword search.

Instead of just matching words, Semantic Search understands the *meaning and context* behind your questions and your documents.

**When to use it:**
- You have a large collection of text documents (articles, reports, notes).
- You want to ask questions in natural language and find the most relevant passages, even if they don't use the exact same words.
- You need a general-purpose question-answering system.

**How it works conceptually:**
1.  **Learning:** When you add a document, the system reads it and breaks it down into logical pieces. It analyzes each piece to understand its underlying meaning.
2.  **Answering:** When you ask a question, the system finds the document pieces with the most similar meaning to your query and uses them to construct an answer.

## Knowledge Graph Search (Graph)

This method is more specialized. It's designed to understand the *relationships* between different pieces of information in your documents. It builds a "mind map" or a graph of your knowledge.

**When to use it:**
- Your documents contain a lot of structured information with clear connections (e.g., "Person A works for Company B," "Product C is made in Country D").
- You want to ask complex questions about relationships, like "Who works for the same company as Person A?" or "What are all the products made in Country D?".

**How it works conceptually:**
1.  **Mapping:** When you add a document, the system actively looks for specific items (like people, places, and companies) and the connections between them. It uses this to build a graph.
2.  **Answering:** When you ask a question, the system navigates the connections in its knowledge graph to find the answer, allowing it to respond to queries that a simple search couldn't handle.
