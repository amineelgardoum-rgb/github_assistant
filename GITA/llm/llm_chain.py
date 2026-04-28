from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
llm_provider = os.getenv("llm_provider", "ollama")

def get_llm():
    if llm_provider == "ollama":
        return ChatOllama(
            model="llama3.2:latest",
            temperature=0.2,
            num_ctx=2048,
        )
    elif llm_provider == "llm_gemini_api":
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set!")
        return GoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=api_key,
            temperature=0
        )
    else:
        raise ValueError(f"Unknown llm_provider: {llm_provider}")

# Lazy load
_llm = [None]  # 👈 mutable container, no global needed

def get_llm_instance():
    if _llm[0] is None:
        _llm[0] = get_llm()
    return _llm[0]

# Prompt stays here too
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert coding assistant analyzing a code repository. Be professional, friendly, and helpful.

Context from the repository:
{context}

User's question:
{question}

Guidelines:
- Answer using ONLY the information provided in the context above
- Use a clear, natural, and conversational tone
- Be concise but thorough - provide explanations when they add value
- Format code snippets with proper syntax highlighting using markdown code blocks
- Reference specific files or functions when relevant
- If the context doesn't contain enough information to answer, say:
  "I don't have enough information in the repository context to answer that question accurately."

Your answer:
""",
)

def answer_from_docs(docs, question: str):
    llm = get_llm_instance()  # 👈 lazy load here

    sources = sorted(set(doc.metadata.get("source", "unknown") for doc in docs))
    context = "\n\n".join(
        f"File: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )

    final_prompt = prompt.format(context=context, question=question)
    answer = llm.invoke(final_prompt)
    return answer, sources