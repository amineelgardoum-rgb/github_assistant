import os
import stat
import hashlib
from git import Repo
from langchain_core.documents import Document

# ---------- Utils ----------


def remove_readonly(func, path, excinfo):
    """ to delete read only files
    Args:
        func: The function that raised the error (e.g., os.remove, os.rmdir)
        path: The path to the file/directory that couldn't be deleted
        excinfo: Exception information tuple (type, value, traceback)
    """
    os.chmod(path, stat.S_IWRITE)
    func(path)


def repo_id_from_url(url: str) -> str:
    """ get the repo is from the url of the repo
    Args:
        url (str): the url for the github repo (https://gihtub.com/user/repo.git)
    Returns:
        str: the id for the repo
    """
    return hashlib.md5(url.encode()).hexdigest()


# ---------- Repo cloning ----------


def clone_repo(repo_url: str, base_dir="data"):
    """ clone the repo and index it under its repo_id 
    Args:
        repo_url (str): the repo url from github
        base_dir (str, optional): the folder name (optional). Defaults to "data".
    Returns:
        repo_path:str,repo_id:str: the repo_path under the data_dir ,and the repo_id generated from the repo_id_from_url function
    """
    repo_id = repo_id_from_url(repo_url)
    repo_path = os.path.join(base_dir, repo_id)

    if not os.path.exists(repo_path):
        print(f"Cloning {repo_url} → {repo_path}")
        Repo.clone_from(repo_url, repo_path)

    return repo_path, repo_id


# ---------- Load files ----------


def load_repo_files(repo_dir):
    """_summary_

    Args:
        repo_dir (str)/path: the path under the repo exists
    Returns:
        docs (str)/names of files: the name of files extracted from the repo_dir
    """
    # docs is a list for the files extracted from the repo_dir under data_dir
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
