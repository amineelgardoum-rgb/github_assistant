
import os
import stat
import hashlib
import json
from git import Repo
from langchain_core.documents import Document

# ---------- Utils ----------


def remove_readonly(func, path, excinfo):
    """Delete read-only files
    Args:
        func: The function that raised the error (e.g., os.remove, os.rmdir)
        path: The path to the file/directory that couldn't be deleted
        excinfo: Exception information tuple (type, value, traceback)
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def repo_id_from_url(url: str) -> str:
    """Generate repo ID from URL
    Args:
        url (str): GitHub repo URL (https://github.com/user/repo.git)
    Returns:
        str: MD5 hash ID for the repo
    """
    return hashlib.md5(url.encode()).hexdigest()


# ---------- Repo cloning ----------


def clone_repo(repo_url: str, base_dir="./data"):
    """Clone repository and return its path
    Args:
        repo_url (str): GitHub repository URL
        base_dir (str, optional): Base directory for cloning. Defaults to "./backend/data"
    Returns:
        tuple: (repo_path, repo_id)
    """
    # Ensure base directory exists
    os.makedirs(base_dir, exist_ok=True)
    
    repo_id = repo_id_from_url(repo_url)
    repo_path = os.path.join(base_dir, repo_id)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} → {repo_path}")
        try:
            Repo.clone_from(repo_url, repo_path)
            print(f"✅ Successfully cloned repository")
        except Exception as e:
            print(f"❌ Failed to clone repository: {e}")
            raise
    else:
        print(f"Repository already exists at {repo_path}")

    return repo_path, repo_id


# ---------- File type handlers ----------


def extract_notebook_content(path):
    """Extract code and markdown from Jupyter notebooks
    Args:
        path (str): Path to .ipynb file
    Returns:
        str: Extracted content from notebook cells
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        cells_content = []
        for cell in notebook.get('cells', []):
            cell_type = cell.get('cell_type', '')
            source = cell.get('source', [])
            
            # Handle both list and string source formats
            if isinstance(source, list):
                content = ''.join(source)
            else:
                content = source
            
            if content.strip():
                # Add cell type marker for context
                if cell_type == 'code':
                    cells_content.append(f"# CODE CELL\n{content}")
                elif cell_type == 'markdown':
                    cells_content.append(f"# MARKDOWN\n{content}")
        
        return '\n\n'.join(cells_content)
    
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in notebook {path}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing notebook {path}: {e}")
        return None


def should_process_file(file_path, file_size_limit_mb=10):
    """Check if file should be processed based on size
    Args:
        file_path (str): Path to file
        file_size_limit_mb (int): Maximum file size in MB
    Returns:
        bool: True if file should be processed
    """
    try:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if size_mb > file_size_limit_mb:
            print(f"⚠️  Skipping large file ({size_mb:.2f}MB): {file_path}")
            return False
        return True
    except Exception:
        return True


# ---------- Load files ----------


def load_repo_files(repo_dir, file_size_limit_mb=10, custom_extensions=None, 
                   custom_excluded_dirs=None, include_binary=False):
    """Load and parse files from repository
    Args:
        repo_dir (str): Repository directory path
        file_size_limit_mb (int): Skip files larger than this (in MB)
        custom_extensions (set): Custom file extensions to include (None = use defaults)
        custom_excluded_dirs (set): Custom directories to exclude (None = use defaults)
        include_binary (bool): Whether to include binary files (images, etc.)
    Returns:
        list: List of Document objects
    """
    docs = []
    
    # Default text-based file extensions
    if custom_extensions is None:
        TEXT_EXTENSIONS = {
            # Code files
            ".py", ".java", ".js", ".ts", ".jsx", ".tsx", ".cpp", ".c", ".h",
            ".cs", ".go", ".rs", ".php", ".rb", ".swift", ".kt", ".scala",
            ".r", ".m", ".sql", ".sh", ".bash", ".ps1",
            
            # Web files
            ".html", ".css", ".scss", ".sass", ".less", ".vue",
            
            # Config files
            ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf",
            ".xml", ".properties", ".env",
            
            # Documentation
            ".md", ".txt", ".rst", ".adoc",
            
            # Data files
            ".csv", ".tsv",
            
            # Notebooks
            ".ipynb",
            
            # Other
            ".graphql", ".proto", ".thrift",
        }
    else:
        TEXT_EXTENSIONS = custom_extensions
    
    # Directories to exclude
    if custom_excluded_dirs is None:
        EXCLUDED_DIRS = {
            # Version control
            ".git", ".svn", ".hg",
            
            # Dependencies
            "node_modules", "vendor", "venv", "env", ".venv",
            "site-packages", "dist-packages",
            
            # Build outputs
            "target", "build", "dist", "out", "bin", "obj",
            
            # Cache
            "__pycache__", ".pytest_cache", ".mypy_cache",
            ".cache", "cache",
            
            # IDE
            ".idea", ".vscode", ".vs", ".eclipse",
            
            # OS
            ".DS_Store", "Thumbs.db",
            
            # Other
            "coverage", ".next", ".nuxt", ".output",
        }
    else:
        EXCLUDED_DIRS = custom_excluded_dirs
    
    # Binary extensions (if needed)
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
        ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
        ".zip", ".tar", ".gz", ".rar", ".7z",
        ".exe", ".dll", ".so", ".dylib",
    }
    
    print(f"📂 Loading files from: {repo_dir}")
    print(f"   File size limit: {file_size_limit_mb}MB")
    print(f"   Allowed extensions: {len(TEXT_EXTENSIONS)} types")
    print(f"   Excluded directories: {len(EXCLUDED_DIRS)} patterns\n")
    
    file_count = 0
    skipped_count = 0
    error_count = 0
    
    for root, dirs, files in os.walk(repo_dir):
        # Filter out excluded directories
        original_dirs = dirs.copy()
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        
        excluded = set(original_dirs) - set(dirs)
        if excluded:
            print(f"⏭️  Skipping directories in {root}: {excluded}")
        
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.basename(file_path)
            ext = os.path.splitext(file)[1].lower()
            
            # Check if extension is allowed
            if ext not in TEXT_EXTENSIONS:
                if include_binary and ext in BINARY_EXTENSIONS:
                    print(f"⚠️  Binary file found (not processed): {file_name}")
                skipped_count += 1
                continue
            
            # Check file size
            if not should_process_file(file_path, file_size_limit_mb):
                skipped_count += 1
                continue
            
            try:
                # Special handling for Jupyter notebooks
                if ext == ".ipynb":
                    content = extract_notebook_content(file_path)
                    if content is None:
                        error_count += 1
                        continue
                else:
                    # Read text files
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                
                # Skip empty files
                if not content or not content.strip():
                    print(f"⚠️  Skipping empty file: {file_name}")
                    skipped_count += 1
                    continue
                
                # Create document
                docs.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": file_path,
                            "file_name": file_name,
                            "extension": ext,
                            "repo_path": os.path.relpath(file_path, repo_dir),
                            "file_size": len(content),
                        },
                    )
                )
                
                file_count += 1
                if file_count % 10 == 0:
                    print(f"   Processed {file_count} files...")
            
            except UnicodeDecodeError:
                print(f"❌ Encoding error (skipping): {file_name}")
                error_count += 1
            except PermissionError:
                print(f"❌ Permission denied (skipping): {file_name}")
                error_count += 1
            except Exception as e:
                print(f"❌ Error reading {file_name}: {e}")
                error_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Successfully loaded: {file_count} files")
    print(f"⏭️  Skipped: {skipped_count} files")
    print(f"❌ Errors: {error_count} files")
    print(f"{'='*50}\n")
    
    return docs


# ---------- Split ----------


def split_code_docs(docs, chunk_size=1000, min_chars=100, overlap=100):
    """Split documents into chunks with overlap
    Args:
        docs (list): List of Document objects
        chunk_size (int): Maximum chunk size in characters
        min_chars (int): Minimum chunk size to keep
        overlap (int): Number of characters to overlap between chunks
    Returns:
        list: List of chunked Document objects
    """
    all_splits = []
    
    print(f"📝 Splitting {len(docs)} documents...")
    print(f"   Chunk size: {chunk_size} chars")
    print(f"   Minimum size: {min_chars} chars")
    print(f"   Overlap: {overlap} chars\n")

    for doc in docs:
        lines = doc.page_content.splitlines()
        chunk = []
        overlap_buffer = []

        for line in lines:
            chunk.append(line)
            current_size = len("\n".join(chunk))

            if current_size >= chunk_size:
                content = "\n".join(chunk)
                
                if len(content) >= min_chars:
                    all_splits.append(
                        Document(
                            page_content=content,
                            metadata={**doc.metadata, "chunk_index": len(all_splits)}
                        )
                    )
                
                # Keep overlap for next chunk
                if overlap > 0:
                    overlap_text = content[-overlap:]
                    overlap_buffer = overlap_text.split("\n")
                    chunk = overlap_buffer
                else:
                    chunk = []

        # Handle remaining content
        if chunk:
            content = "\n".join(chunk)
            if len(content) >= min_chars:
                all_splits.append(
                    Document(
                        page_content=content,
                        metadata={**doc.metadata, "chunk_index": len(all_splits)}
                    )
                )

    print(f"✅ Created {len(all_splits)} chunks from {len(docs)} documents")
    return all_splits