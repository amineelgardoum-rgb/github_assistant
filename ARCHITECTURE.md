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

APIClient -->|"POST /load_repo"| IndexEndpoint
IndexEndpoint --> RepoLoader
EmbedGen -->|"Store vectors"| ChromaDB

APIClient -->|"POST /ask"| ChatEndpoint
ChatEndpoint --> QueryEmbed
ChromaRetriever -.->|"Fetch"| ChromaDB
ChromaRetriever --> PromptBuilder
LLMCall -->|"Response"| RAGChain

```

---

## Activity Diagram (User Workflows)

```mermaid
graph TD
    Start([User Opens App])

    subgraph IndexRepo[Index Repository Flow]
        EnterURL[Enter GitHub URL]
        SendIndex[POST /load_repo]
        CloneRepo[Clone Repository and generate repo_id]
        CacheCheck{Vector store exists?}
        LoadFiles[Load source files]
        ChunkCode[Split into chunks]
        GenEmbeds[Generate embeddings]
        StoreVectors[Store in Chroma]
        IndexSuccess[Repository indexed]

        EnterURL --> SendIndex
        SendIndex --> CloneRepo
        CloneRepo --> CacheCheck
        CacheCheck -->|Yes| IndexSuccess
        CacheCheck -->|No| LoadFiles
        LoadFiles --> ChunkCode
        ChunkCode --> GenEmbeds
        GenEmbeds --> StoreVectors
        StoreVectors --> IndexSuccess
    end

    subgraph AskQuestion[Ask Question Flow]
        EnterQuestion[Enter question]
        SendAsk[POST /ask]
        RepoLoaded{Repo indexed?}
        Error2[Repo not indexed]
        EmbedQuery[Embed question]
        SearchVectors[Similarity search]
        RetrieveDocs[Retrieve documents]
        BuildPrompt[Build prompt]
        CallLLM[Call LLM]
        GenAnswer[Generate answer]
        ReturnAnswer[Return answer]

        EnterQuestion --> SendAsk
        SendAsk --> RepoLoaded
        RepoLoaded -->|No| Error2
        RepoLoaded -->|Yes| EmbedQuery
        EmbedQuery --> SearchVectors
        SearchVectors --> RetrieveDocs
        RetrieveDocs --> BuildPrompt
        BuildPrompt --> CallLLM
        CallLLM --> GenAnswer
        GenAnswer --> ReturnAnswer
    end

    Choice{Choose action}
    End([Exit])

    Start --> Choice
    Choice -->|Index repo| EnterURL
    Choice -->|Ask question| EnterQuestion
    IndexSuccess --> Choice
    ReturnAnswer --> Choice
    Error2 --> Choice
    Choice -->|Exit| End

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

## Class Diagram (Mermaid)

```mermaid
classDiagram
        class FrontendAPIClient {
            +indexRepo(repoUrl)
            +chat(repoId, question)
        }

        class FastAPIApp {
            +LoadRepoRequest(repo_url)
            +AskRequest(repo_id, question)
            +index_repo(req)
            +chat(req)
        }

        class RepoLoader {
            +clone_repo(url)
            +load_repo_files(path)
            +split_code_docs(docs)
        }

        class EmbeddingGenerator {
            +get_vector_store(chunks, repo_id)
        }

        class VectorStore {
            +as_retriever(search_type, search_kwargs)
            +persist(chunks)
        }

        class ChromaDB {
            +store_vectors(vectors)
            +query_vectors(query, k)
        }

        class Retriever {
            +retrieve(query, k)
        }

        class PromptBuilder {
            +build_prompt(docs, question)
        }

        class LLMChain {
            +answer_from_docs(docs, question)
        }

        FrontendAPIClient --> FastAPIApp : POST /load-repo, /ask
        FastAPIApp --> RepoLoader : uses
        RepoLoader --> EmbeddingGenerator : provides chunks
        EmbeddingGenerator --> VectorStore : creates/returns
        VectorStore --> ChromaDB : persists vectors
        VectorStore --> Retriever : exposes retriever
        Retriever --> PromptBuilder : supplies docs
        PromptBuilder --> LLMChain : builds prompt for
        LLMChain --> FastAPIApp : returns answer
```
