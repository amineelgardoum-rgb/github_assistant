import os
import stat
import hashlib
from git import Repo
from langchain_core.documents import Document

# ---------- Utils ----------


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def repo_id_from_url(url: str) -> str:
    return hashlib.md5(url.encode()).hexdigest()


# ---------- Repo cloning ----------


def clone_repo(repo_url: str, base_dir="data"):
    repo_id = repo_id_from_url(repo_url)
    repo_path = os.path.join(base_dir, repo_id)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} → {repo_path}")
        Repo.clone_from(repo_url, repo_path)

    return repo_path, repo_id


# ---------- Load files ----------


def load_repo_files(repo_dir):
    docs = []

    ALLOWED_EXTENSIONS = {
        ".java",
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".json",
        ".yml",
        ".yaml",
        ".xml",
        ".properties",
        ".md",
        ".txt",
    }

    EXCLUDED_DIRS = {
        ".git",
        "node_modules",
        "target",
        "build",
        "dist",
        "__pycache__",
        ".idea",
        ".vscode",
    }

    for root, dirs, files in os.walk(repo_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for file in files:
            ext = os.path.splitext(file)[1]

            if ext in ALLOWED_EXTENSIONS:
                path = os.path.join(root, file)
                try:
                    with open(path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                        docs.append(
                            Document(
                                page_content=content,
                                metadata={
                                    "source": path,
                                    "file_name": os.path.basename(path),
                                    "language": ext,
                                    "repo_path": os.path.relpath(path, repo_dir),
                                },
                            )
                        )
                except Exception as e:
                    print(f"Failed to read {path}: {e}")

    print(f"Loaded {len(docs)} files")
    return docs


# ---------- Split ----------


def split_code_docs(docs, chunk_size=2500, min_chars=300):
    all_splits = []

    for doc in docs:
        lines = doc.page_content.splitlines()
        chunk = []

        for line in lines:
            chunk.append(line)

            if len("\n".join(chunk)) >= chunk_size:
                content = "\n".join(chunk)
                if len(content) >= min_chars:
                    all_splits.append(
                        Document(page_content=content, metadata=doc.metadata)
                    )
                chunk = []

        if chunk:
            content = "\n".join(chunk)
            if len(content) >= min_chars:
                all_splits.append(
                    Document(page_content=content, metadata=doc.metadata)
                )

    print(f"Created {len(all_splits)} chunks")
    return all_splits
