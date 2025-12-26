from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv
# from pydantic import SecretStr
# from torch import mode

load_dotenv()  # load .env file


llm = GoogleGenerativeAI(model="gemini-2.5-flash",temperature=0)
prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert coding assistant. Be professional, friendly, and helpful.

Your task is to **answer the user's question using ONLY the information provided in the context below**.  
Do not make assumptions or include information that is not present in the context.

Guidelines:
- Use a clear, natural, and human-like tone.
- Be concise, but provide explanations if necessary.
- Format any code snippets correctly using proper syntax highlighting.
- If someone says "thank you", reply politely and courteously.
- If the answer is not present in the context, respond with:
  "I don't know based on the provided context."

Context:
{context}

User Question:
{question}

Answer:
"""
)



def answer_from_docs(docs, question: str):
    sources = sorted(set(doc.metadata.get("source", "unknown") for doc in docs))

    context = "\n\n".join(
        f"File: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )

    final_prompt = prompt.format(context=context, question=question)

    answer = llm.invoke(final_prompt)
    return answer, sources
