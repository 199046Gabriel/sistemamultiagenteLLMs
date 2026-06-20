# config.py — Configurações centrais do projeto

import os
from pathlib import Path

# ── Caminhos ───────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
CHROMA_DB_DIR = BASE_DIR / "chroma_db"

# ── Ollama / LLM ───────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3")          # modelo de linguagem
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")  # modelo de embeddings

# ── RAG ────────────────────────────────────────────────────────
CHROMA_COLLECTION = "academic_docs"
RAG_TOP_K = 4          # quantos chunks recuperar por consulta
CHUNK_SIZE = 800        # tamanho de cada chunk em caracteres
CHUNK_OVERLAP = 100     # sobreposição entre chunks

# ── MCP ────────────────────────────────────────────────────────
MCP_HOST = "127.0.0.1"
MCP_PORT = 8765

# ── Interface ──────────────────────────────────────────────────
APP_NAME = "Assistente Acadêmico IA"
APP_VERSION = "1.0.0"
