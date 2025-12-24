# 🧠💬 GitHub Codebase Assistant

A chat-based AI assistant for deeply understanding and navigating GitHub repositories.

---

### 🚀 What this Project Does

This tool allows developers to **ask questions about any codebase** and get reliable, context-aware answers, grounded only in the repository's source files. It’s built on a **Retrieval-Augmented Generation (RAG)** architecture to eliminate hallucinations and provide high-fidelity technical insights.

### ✨ Core Features

* **Clone & Index:** Clones any public GitHub repository for processing.
* **Deep Understanding:** Parses and chunks source code files for deep, granular comprehension.
* **Vectorized Knowledge:** Generates embeddings for code snippets and stores them in a vector database.
* **Precision Retrieval:** Retrieves the most relevant code snippets for every question asked.
* **Context-Aware Chat:** Interact with the codebase as a conversation.
* **Grounded Responses:** Responses are guaranteed to be based *only* on the provided source code.
* **Exact References:** Get file references (`src/path/to/file.js`) alongside every answer.

---

## 🧩 Tech Stack

This project is built using a modern, efficient, and fully self-hosted stack to deliver fast, reliable code insights.

| Category | Key Technologies | Description |
| :--- | :--- | :--- |
| **Frontend** | `React`, `CSS/Tailwind` | Minimalist, chat-style UI with real-time typing indicators for a responsive feel. |
| **Backend** | `FastAPI` | High-performance Python REST API handling repo loading, indexing, and Q/A requests. |
| **Caching** | In-Memory Stores | Used for caching loaded repositories and vector stores to minimize re-indexing time. |

### 🤖 AI / RAG Components

* **Orchestration:** **LangChain**
    * Used for managing the RAG pipeline, chaining components, and structured prompting.
* **Vector Database:** **Chroma**
    * The persistent, in-memory store for vectorized code embeddings.
* **Local LLM Host:** **Ollama**
    * Enables local, private execution of the Language Model.
    * **LLM:** **Llama 3** (The large language model used for generating answers.)
    * **Embeddings:** **mxbai-embed-large** (The embedding model used to create vector representations of the code.)

---

### ❓ Example Questions You Can Ask

* `Which function handles login?`
* `Where is authentication implemented?`
* `How does this service work internally?`
* `Explain this class like I’m new to the project.`
* `What is the purpose of the 'utility.py' file?`

---

### 🛠️ Architecture Overview

This project uses a **RAG (Retrieval-Augmented Generation)** architecture to deeply understand real codebases instead of hallucinating.
