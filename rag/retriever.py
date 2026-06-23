# rag/retriever.py — Busca semântica no índice vetorial

from __future__ import annotations
from langchain_community.vectorstores import Chroma
from config import RAG_TOP_K


class Retriever:
    """Realiza busca semântica na base de conhecimento indexada."""

    def __init__(self, vectorstore: Chroma):
        self._store = vectorstore
        self._retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": RAG_TOP_K},
        )

    def search(self, query: str, k: int = RAG_TOP_K) -> list[dict]:
        """
        Busca os k chunks mais relevantes para a query.
        Retorna lista de dicts com 'content' e 'source'.
        """
        docs = self._store.similarity_search(query, k=k)
        results = []
        for doc in docs:
            results.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source_file", "desconhecido"),
                "page": doc.metadata.get("page", ""),
            })
        return results

    def format_context(self, query: str, k: int = RAG_TOP_K) -> str:
        """
        Retorna o contexto formatado como string para inserir no prompt.
        """
        results = self.search(query, k=k)
        if not results:
            return ""

        parts = []
        for i, r in enumerate(results, 1):
            source_label = f"{r['source']}"
            if r["page"] != "":
                source_label += f", pág. {r['page']}"
            parts.append(f"[Fonte {i} — {source_label}]\n{r['content']}")

        return "\n\n---\n\n".join(parts)

    def has_documents(self) -> bool:
        """Verifica se há documentos indexados."""
        try:
            count = self._store._collection.count()
            return count > 0
        except Exception:
            return False
