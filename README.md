# 🧠💬 GitHub Codebase Assistant

A chat-based AI assistant for deeply understanding and navigating GitHub repositories using Retrieval-Augmented Generation (RAG).

---

## 🚀 What this Project Does

This tool allows developers to **ask questions about any codebase** and get reliable, context-aware answers, grounded only in the repository's source files. Built on a **Retrieval-Augmented Generation (RAG)** architecture, it eliminates hallucinations and provides high-fidelity technical insights with exact file references.

### ✨ Core Features

- **Clone & Index:** Clones any public � GitHub repository for processing
- **Deep Understanding:** Parses and chunks source code files for granular comprehension
- **Vectorized Knowledge:** Generates embeddings for code snippets using local embedding models
- **Precision Retrieval:** Retrieves the most relevant code snippets for each question
- **Context-Aware Chat:** Interact with the codebase through natural conversation
- **Grounded Responses:** Responses are guaranteed to be based *only* on provided source code
- **Exact References:** Get file references alongside every answer

---

## 🧩 Tech Stack

| Component                   | Technology                                | Purpose                                        |
| --------------------------- | ----------------------------------------- | ---------------------------------------------- |
| **Frontend**          | ⚛️ React + ⚡️ Vite                    | Modern chat UI with real-time interactions     |
| **Backend**           | 🚀 FastAPI (🐍 Python)                    | High-performance REST API for indexing and Q/A |
| **Vector DB**         | 🗄️ Chroma                               | Persistent storage for code embeddings         |
| **LLM Orchestration** | 🔗 LangChain                              | RAG pipeline management and prompting          |
| **Language Model**    | 🌐 Google Gemini                          | Core AI model for generating answers           |
| **Embedding Model**   | 🧠 sentence-transformers/all-MiniLM-L6-v2 | Vector representations of code snippets        |
| **Containerization**  | 🐳 Docker + 🧩 Docker Compose             | Containerized deployment                       |

---

## 📋 Prerequisites

- **Python 3.9+** (for backend)
- **Node.js 16+** (for frontend)
- **Docker & Docker Compose** (for containerized setup)
- **Google Gemini API Key** (for LLM access)
- **Git** (for cloning repositories)

---

## 🔧 Installation & Setup

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/amineelgardoum-rgb/github_assistant.git
cd github_assistant

# Start all services
make up 
```

The application will be available at `http://localhost:5173` (frontend) and API at `http://localhost:8000`.

### Option 2: Manual Setup

#### Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Start backend
python main.py
```

#### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Start development server
npm run dev
```

---

## Make Commands

The project includes a `Makefile` with convenient commands for Docker operations:

```bash
# Start all services (build & run in background)
make up

# Stop all services and remove volumes
make down

# View logs from all services (follow mode)
make logs

# View backend service logs only
make backendLogs

# View frontend service logs only
make frontendLogs
```

These commands simplify Docker Compose workflows for local development and testing.

---

## 🀽Project Structure

```
rag/
├── backend/                 # Python FastAPI backend
│   └── api/                 # Api logic (routers/schemas)
│   │   ├── routers/         # Routers
│   │   │    ├── __init__.py            # int file
│   │   │    ├── ask_router.py          # ask router /ask
│   │   │    └── load_repo_router.py    # load router /load
|   |   ├── schemas/
|   |   |    ├── __init__.py     # init file
|   |   |    ├── askRequest.py   # Class validation for /ask
|   |   |    └──  loadRequest.py # Class validation for /load_repo
|   |   └── vector_cache.py      # vector cache  for the caching 
│   ├── docker/               
|   |    └── Dockerfile          # Dockerfile for the backend service
│   ├── embeddings/              # Embedding generation module
|   |     ├── __init__.py        # __init__.py file
|   |     └── vector_store.py    # vector store logic 
│   ├── llm/
|   |    ├── __init__.py         # init file                  
|   |    └── llm_chain.py        # llm chain logic and setup
│   ├── loaders/                 # Repository loader and parser
|   |    ├── __init__.py         # init file
|   |    └── repo_loader.py      # repository loader logic  
│   ├── utils/                
|   |    ├── __init__.py         # init file 
|   |    └── retriever_utils.py  # retrieving logic 
│   ├── .dockerignore            # Docker ignore build
|   └── main.py                  # main api entry
├── frontend/               # React + Vite frontend
│   ├── src/
│   │   ├── components/       # React components
|   |   |    ├── ChatPage.jsx # Chat page component
|   |   |    ├── Landing.jsx  # Landing page component
|   |   |    └── Spinner.jsx  # Spinner component
│   │   ├── job/           
|   |   |    └── api.js          # api logic for the frontend    
│   │   ├── style/               
|   |   |    ├── App.css         # app styling
|   |   |    ├── chatpage.css    # chat page styling 
|   |   |    ├── index.css       # index styling
|   |   |    └── landingpage.css # landing page styling
│   │   ├── assets/         
|   |   |    └── react.svg       # react svg
│   │   ├── main.jsx             # Entry point
│   │   └── App.jsx              # The app jsx file
│   ├── public/                  # Static assets
|   |    └── vite.svg            # static icon
│   ├── package.json             # Node dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── .dockerignore            # Docker ignore (ignore in build)
│   ├── .gitignore               # Ignore file 
│   ├── docker/  
|   |     └── Dockerfile      # Dockerfile file for frontend folder
|   ├── eslint.config.js      # Config linting for the js code
│   └── index.html            # HTML template
├──  diagram/                 # Diagram folder
|      ├──  activity_diag.png  # Activity diagram for the project
|      ├──  chat_&_answer.png  # Chat and answer sequence diagram
|      ├──  files_structure.png          # The project  structure
|      ├──  high_level_architecture.png # High level architecture
|      ├──  indexing_repo.png  # Indexing sequence diagram
|      ├──  class_diag.png     # class diagram 
|      └──  rag_pipeline_architecture.png # Rag pipeline architecture
├──  docker-compose.yml       # Multi-container orchestration
├──  Makefile                 # Build automation scripts
├──  .dockerignore            # Docker build ignore file
├──  .gitignore               # Git ignore file
├──  README.md                # This file
└──  LICENSE                  # License file
```

---

## 🎯 How It Works

### RAG Pipeline Architecture

1. **Repository Cloning:** User provides a � GitHub repository URL
2. **Code Parsing:** Source files are parsed and chunked into meaningful segments
3. **Embedding Generation:** Each chunk is converted to a dense vector using mxbai-embed-large model
4. **Vector Storage:** Embeddings are persisted in Chroma vector database for fast retrieval
5. **Query Processing:** User questions are also embedded using the same model
6. **Semantic Retrieval:** Most relevant code chunks are retrieved based on vector similarity
7. **Context Augmentation:** Retrieved chunks are combined with the original question
8. **LLM Generation:** Gemini generates an answer based on the augmented context
9. **Response Delivery:** Grounded answer with exact file references and line numbers

---

## ❓ Example Questions

- `Which function handles authentication?`
- `Where is the database connection established?`
- `How does the API route work?`
- `Explain the error handling mechanism`
- `What does the utility module do?`
- `Show me how caching is implemented`
- `What are the main components of this project?`

---

## 🚀 API Endpoints

### Backend API (FastAPI)

```
POST /load_repo
  Description: Index a  GitHub repository by cloning and embedding its files
  Request: { "repo_url": "https://github.com/user/repo" }
  Response: { "repo_id": "<id>", "num_files": 12, "num_chunks": 42, "message": "Created new embeddings" }

POST /ask
  Description: Ask a question against an indexed repository
  Request: { "repo_id": "<id>", "question": "How does authentication work?" }
  Response: { "answer": "...", "sources": ["path/to/file.py:123"] }

GET /docs
  Description: FastAPI Swagger UI (OpenAPI docs)
  Response: HTML docs automatically served by FastAPI
```

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start all containers
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down

# Clean up (remove volumes)
docker-compose down -v
```

### Manual Docker Build

```bash
# Backend
cd backend
docker build -t rag-backend:latest .
docker run -p 8000:8000 rag-backend:latest

# Frontend
cd frontend
docker build -t rag-frontend:latest .
docker run -p 5173:5173 rag-frontend:latest
```

---

## 🔌 Environment Variables

Create a `.env` file in the backend directory:

```env
# Google Gemini Configuration
GOOGLE_API_KEY=your_google_gemini_api_key_here
MODEL_NAME=gemini-pro

# Embedding Model Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Vector Database
CHROMA_DB_PATH=./chroma_langchain_db

# Frontend Configuration
VITE_API_URL=http://localhost:8000
```

---

## 📊 Performance Considerations

- **Caching:** In-memory caching of loaded repositories reduces re-indexing time
- **Chunking Strategy:** Code is split intelligently to maintain context while optimizing retrieval
- **Vector Similarity:** Retrieves top-k most relevant chunks (configurable) for each query
- **Streaming:** Frontend supports streaming responses for better real-time UX
- **Database Indexing:** Chroma provides fast vector similarity search with HNSW algorithm

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Workflow

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -r backend/requirements.txt

# Run backend with auto-reload
python backend/main.py

# In another terminal, run frontend
cd frontend
npm install
npm run dev
```

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🆘 Troubleshooting

### Issue: Gemini API key not set

```bash
# Set your Google Gemini API key in .env file
# Get your API key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_actual_api_key_here
```

### Issue: Backend connection refused

- Ensure `GOOGLE_API_KEY` environment variable is correctly configured
- Verify your API key is valid and has proper permissions
- Check network connectivity to Google Gemini API

### Issue: Vector database errors

```bash
# Clear and rebuild vector store
rm -rf backend/chroma_langchain_db/
# Restart the application to rebuild from scratch
```

### Issue: Frontend can't connect to backend

- Verify backend is running on `http://localhost:8000`
- Check `VITE_API_URL` in frontend environment
- Check browser console for CORS errors

### Issue: Out of memory when indexing large repositories

- Reduce chunk size in configuration
- Process repositories in smaller batches
- Ensure sufficient system RAM (8GB+ recommended)

---

## 📖 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [Chroma Vector Database](https://docs.trychroma.com/)
- [Google Gemini API](https://ai.google.dev/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Guide](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Configuration](https://vitejs.dev/)
- [RAG Architecture](https://arxiv.org/abs/2005.11401)

---

## 🎓 Learning Resources

Understanding RAG:

- RAG combines retrieval and generation for better accuracy
- Embeddings convert text to dense vectors for similarity search
- Vector databases enable fast semantic retrieval
- LLMs generate responses based on retrieved context

---

## 📞 Support

For issues, questions, or suggestions:

- Open an issue on � GitHub
- Check existing issues for solutions
- Review logs for error details
- Contact the maintainers

---

## 🙏 Acknowledgments

Built with:

- The LangChain community for excellent LLM orchestration
- Chroma team for fast vector database
- Google Gemini for powerful AI-powered responses
- Sentence Transformers for efficient embeddings
- FastAPI for high-performance Python APIs
- React and Vite for modern frontend development
