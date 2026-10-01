import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns an initialized LLM client based on available API keys."""
    if os.getenv("GROQ_API_KEY"):
        from langchain_groq import ChatGroq
        # We use a Groq model suitable for coding
        return ChatGroq(model="openai/gpt-oss-20b", temperature=0.1)
    elif os.getenv("GEMINI_API_KEY"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
    else:
        raise ValueError("No API key found for Groq or Gemini. Please set it in .env")
