from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file
api_key = os.getenv("GOOGLE_API_KEY")
llm_provider = os.getenv("llm_provider", "ollama")

# this is for the llm_provider to not exceed

if llm_provider == "ollama":
    llm = ChatOllama(
        model="llama3.2:latest",  # Much smaller! 
        temperature=0.2,
        num_ctx=2048,  # Smaller context for limited RAM
    )
elif llm_provider == "llm_gemini_api":
    llm = GoogleGenerativeAI(
        model="gemini-2.5-flash"
        , api_key=api_key,
        temperature=0)


""" Define The Prompt for the llm generation"""
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
    """A helper function to answer from the docs
    Args:
        docs (str): the docs cloned from the repository
        question (str): the user question
    Returns:
        str: the answer and the sources generated from the llm retrieving
    """
    sources = sorted(set(doc.metadata.get("source", "unknown") for doc in docs))

    context = "\n\n".join(
        f"File: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )

    final_prompt = prompt.format(context=context, question=question)

    answer = llm.invoke(final_prompt)
    return answer, sources
