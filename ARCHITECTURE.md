# System Architecture — RAG Codebase Assistant

This document details the system architecture and data flow of the RAG-based GitHub Codebase Assistant.

---

## Minimal Architecture (Quick Overview)

```mermaid
graph LR
    User["👤 User"]
    Frontend["⚛️ React<br/>Frontend"]
    Backend["🔌 FastAPI<br/>Backend"]
    Chroma["🗄️ Chroma<br/>Vector DB"]
    Gemini["🌐 Gemini<br/>LLM"]
  
    User -->|Chat| Frontend
    Frontend -->|Query| Backend
    Backend -->|Embed| Chroma
    Backend -->|Prompt| Gemini
    Gemini -->|Answer| Backend
    Backend -->|Response| Frontend
    Frontend -->|Display| User
```

---

## High-Level Architecture Diagram

```mermaid
graph TB
    User["👤 User<br/>(Browser)"]
    Frontend["⚛️ Frontend<br/>(React + Vite)<br/>localhost:5173"]
    API["🔌 Backend API<br/>(FastAPI)<br/>localhost:8000"]
    Loader["📂 Repo Loader<br/>(repo_loader.py)"]
    Chunker["✂️ Chunker<br/>(Split Code)"]
    EmbeddingModel["🧠 Embedding Model<br/>(sentence-transformers)"]
    VectorDB["🗄️ Vector Database<br/>(Chroma)"]
    Retriever["🔍 Retriever<br/>(Similarity Search)"]
    LLMChain["🔗 LLM Chain<br/>(LangChain)"]
    LLMProvider["🌐 LLM Provider<br/>(Google Gemini)"]
    Response["✅ Grounded Response<br/>(with file refs)"]

    User -->|Ask Question| Frontend
    Frontend -->|HTTP Request| API
  
    API -->|Index Repo| Loader
    Loader -->|Raw Code Files| Chunker
    Chunker -->|Code Chunks| EmbeddingModel
    EmbeddingModel -->|Dense Vectors| VectorDB
  
    API -->|User Query| EmbeddingModel
    EmbeddingModel -->|Query Vector| Retriever
    Retriever -->|Top-K Chunks| VectorDB
    Retriever -->|Retrieved Context| LLMChain
    LLMChain -->|Prompt| LLMProvider
    LLMProvider -->|Generated Text| LLMChain
    LLMChain -->|Answer| Response
    Response -->|HTTP Response| Frontend
    Frontend -->|Display Answer| User
```

---

## Detailed Component Diagram

```mermaid
graph LR

APIClient["API Client<br/>(Frontend)"]

subgraph Backend["Backend Layer (FastAPI)"]
    Routes["Routes<br/>(main.py)"]
    IndexEndpoint["POST /load_repo"]
    ChatEndpoint["POST /ask"]
    Routes --> IndexEndpoint
    Routes --> ChatEndpoint
end

subgraph Indexing["Indexing Pipeline"]
    RepoLoader["Repo Loader<br/>(loaders/repo_loader.py)"]
    CodeChunker["Code Chunker<br/>(semantic split)"]
    EmbedGen["Embedding Generator<br/>(embeddings/vector_store.py)"]
    RepoLoader --> CodeChunker
    CodeChunker --> EmbedGen
end

subgraph Retrieval["Retrieval Pipeline"]
    QueryEmbed["Query Embedder<br/>(same model)"]
    ChromaRetriever["Chroma Retriever<br/>(similarity search)"]
    QueryEmbed --> ChromaRetriever
end

subgraph Generation["Generation Pipeline"]
    PromptBuilder["Prompt Builder<br/>(utils/retriever_utils.py)"]
    RAGChain["RAG Chain<br/>(llm/llm_chain.py)"]
    LLMCall["LLM API Call<br/>(Google Gemini)"]
    PromptBuilder --> RAGChain
    RAGChain --> LLMCall
end

subgraph Persistence["Persistence Layer"]
    ChromaDB["Chroma Vector DB<br/>(chroma_langchain_db/)"]
end

APIClient -->|"POST index-repo"| IndexEndpoint
IndexEndpoint --> RepoLoader
EmbedGen -->|"Store vectors"| ChromaDB

APIClient -->|"POST chat"| ChatEndpoint
ChatEndpoint --> QueryEmbed
ChromaRetriever -.->|"Fetch"| ChromaDB
ChromaRetriever --> PromptBuilder
LLMCall -->|"Response"| RAGChain

```

---

## Data Flow: Indexing a Repository

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Frontend<br/>(React)
    participant API as Backend API<br/>(FastAPI)
    participant Loader as Repo Loader
    participant Chunker as Code Chunker
    participant EmbedModel as Embedding Model
    participant Chroma as Vector DB<br/>(Chroma)

    User->>Frontend: Enter GitHub URL
    Frontend->>API: POST /load_repo {url}
    API->>Loader: Load and clone repo
    Loader->>Loader: Extract .py, .js, .md, etc.
    Loader->>Chunker: Split into chunks
    Chunker->>Chunker: Apply semantic chunking
    Chunker->>EmbedModel: Embed each chunk
    EmbedModel->>EmbedModel: Generate vectors (384-dim)
    EmbedModel->>Chroma: Store vectors + metadata
    Chroma->>Chroma: Index vectors (HNSW)
    API->>Frontend: {status: success}
    Frontend->>User: ✓ Repo indexed!
```

---

## Data Flow: Chat (Query & Answer)

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Frontend<br/>(React)
    participant API as Backend API<br/>(FastAPI)
    participant EmbedModel as Embedding Model
    participant Chroma as Vector DB<br/>(Chroma)
    participant Retriever as Retriever
    participant PromptBuilder as Prompt Builder
    participant LLMChain as LLM Chain<br/>(LangChain)
    participant Gemini as Google Gemini

    User->>Frontend: Ask question
    Frontend->>API: POST /ask {question}
    API->>EmbedModel: Embed question
    EmbedModel->>EmbedModel: Generate query vector
    API->>Chroma: Search top-k chunks
    Chroma->>Retriever: Return ranked results
    Retriever->>PromptBuilder: Build prompt with context
    PromptBuilder->>LLMChain: {context, question}
    LLMChain->>Gemini: Send prompt
    Gemini->>Gemini: Generate response
    Gemini->>LLMChain: Response text
    LLMChain->>API: {answer, sources}
    API->>Frontend: Return response
    Frontend->>User: Display answer + file refs
```

---

## File Structure & Module Map

```mermaid
graph TD
    Root["rag/"]
  
    Backend["backend/"]
    Main["main.py<br/>(API routes)"]
    Reqs["requirements.txt<br/>(deps)"]
  
    Embeddings["embeddings/"]
    VectorStore["vector_store.py<br/>(embeddings)"]
  
    LLM["llm/"]
    LLMChain["llm_chain.py<br/>(prompt + chain)"]
  
    Loaders["loaders/"]
    RepoLoader["repo_loader.py<br/>(cloning + chunking)"]
  
    Utils["utils/"]
    RetrieverUtils["retriever_utils.py<br/>(retrieval helpers)"]
  
    ChromaDB["chroma_langchain_db/<br/>(persisted vectors)"]
  
    Frontend["frontend/"]
    Src["src/"]
    API["api.js<br/>(HTTP client)"]
    Components["components/<br/>(React)"]
  
    Root --> Backend
    Root --> Frontend
    Backend --> Main
    Backend --> Reqs
    Backend --> Embeddings
    Backend --> LLM
    Backend --> Loaders
    Backend --> Utils
    Backend --> ChromaDB
    Embeddings --> VectorStore
    LLM --> LLMChain
    Loaders --> RepoLoader
    Utils --> RetrieverUtils
    Frontend --> Src
    Src --> API
    Src --> Components
```

---

## Technology Stack Overview

### Frontend

- **React**: UI framework for interactive chat interface
- **Vite**: Lightning-fast build tool & dev server
- **Styling**: CSS for layout and theming

### Backend

- **FastAPI**: High-performance Python async API framework
- **Python 3.9+**: Language runtime

### AI/ML Components

- **LangChain**: Orchestrates RAG pipeline, prompts, and LLM chains
- **Sentence-Transformers** (all-MiniLM-L6-v2): Converts text to 384-dimensional embeddings
- **Google Gemini**: LLM for generating grounded answers
- **Chroma**: Vector database for persistent embedding storage and retrieval

### Containerization & Deployment

- **Docker**: Containerizes frontend and backend
- **Docker Compose**: Orchestrates multi-container local environment

---

## RAG Pipeline: Step-by-Step

1. **Repository Input**

   - User provides GitHub repository URL
   - Backend clones repo using `repo_loader.py`
2. **Code Parsing & Chunking**

   - Extract source files (`.py`, `.js`, `.ts`, `.md`, etc.)
   - Split into semantic chunks (maintains context, ~500 tokens/chunk)
   - Preserve file path, line number metadata
3. **Embedding Generation**

   - Each chunk → sentence-transformers model
   - Output: 384-dimensional dense vectors
4. **Vector Storage**

   - Vectors stored in Chroma with metadata
   - Chroma builds HNSW index for fast retrieval
5. **Query Processing**

   - User question → embed using same model
   - Query vector → similarity search in Chroma
6. **Context Retrieval**

   - Top-k chunks (default: 5-10) ranked by cosine similarity
   - Preserve file path + line numbers for sources
7. **Prompt Construction**

   - Build RAG prompt: `{question} + {context} → answer`
   - Use LangChain to orchestrate
8. **LLM Generation**

   - Send prompt to Google Gemini
   - Receive generated answer
9. **Response Assembly**

   - Return answer + source references (file, line #)
   - Frontend displays grounded response

---

## API Contract

### POST /index-repo

```json
Request:  { "repo_url": "https://github.com/user/repo" }
Response: { "status": "success", "message": "..." }
```

### POST /chat

```json
Request:  { "question": "How does authentication work?" }
Response: { 
  "answer": "...",
  "sources": [
    { "file": "backend/auth.py", "line": 42 },
    { "file": "backend/utils.py", "line": 88 }
  ]
}
```

---

## Performance & Scalability Notes

- **Embeddings**: Cached in memory and persisted in Chroma (~instant retrieval)
- **Chunking**: Semantic splitting maintains context while controlling chunk size
- **Retrieval**: HNSW index in Chroma provides O(log n) search time
- **LLM Latency**: Dominant factor; typically 2-5 seconds for answer generation
- **Scalability**: Can handle 1000s of code files; Chroma scales to millions of embeddings

---

## Development Workflow

1. **Local Setup**: Run backend + frontend locally with hot-reload
2. **Testing**: Index a test repo, ask questions, iterate
3. **Docker Build**: Use `docker-compose up` for containerized stack
4. **Production**: Deploy backend to cloud (AppEngine, Azure, etc.), frontend to CDN

---

## Future Enhancements

- Hybrid search (keyword + semantic)
- Multi-language support
- Fine-tuned embeddings for code
- Streaming responses
- User query logging & analytics
