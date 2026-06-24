# agents/retriever_agent.py — Agente Recuperador (RAG)
#
# Responsabilidade: buscar contexto relevante na base vetorial e
# retornar os trechos mais pertinentes para a pergunta do usuário.

from __future__ import annotations
from langchain_ollama import OllamaLLM
from rich.console import Console
from config import LLM_MODEL, OLLAMA_BASE_URL

console = Console()

QUERY_EXPANSION_PROMPT = """\
Você é um especialista em busca de informações acadêmicas.
Reescreva a consulta abaixo de forma mais completa e técnica para melhorar
a busca em uma base de documentos acadêmicos. Responda APENAS com a consulta
reescrita, sem explicações adicionais.

Consulta original: {query}
Consulta expandida:"""


class RetrieverAgent:
    """
    Agente Recuperador — executa busca semântica na base de conhecimento.
    """

    def __init__(self, retriever):
        """
        Args:
            retriever: instância de rag.retriever.Retriever
        """
        self.retriever = retriever
        self.llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.0,
        )

    def expand_query(self, query: str) -> str:
        """Expande a query para melhorar a recall na busca semântica."""
        try:
            prompt = QUERY_EXPANSION_PROMPT.format(query=query)
            expanded = self.llm.invoke(prompt).strip()
            # Evita expansões muito longas
            if len(expanded) > 300:
                return query
            return expanded
        except Exception:
            return query

    def retrieve(self, query: str, expand: bool = True) -> dict:
        """
        Busca documentos relevantes para a query.

        Returns:
            dict com:
              - 'context': string formatada para inserir no prompt
              - 'results': lista de dicts com content/source/page
              - 'expanded_query': query usada na busca
        """
        if not self.retriever.has_documents():
            return {
                "context": "⚠ Base de conhecimento vazia. Adicione documentos em knowledge_base/.",
                "results": [],
                "expanded_query": query,
            }

        search_query = self.expand_query(query) if expand else query
        console.print(f"  [dim]🔍 Buscando: {search_query[:80]}...[/dim]")

        results = self.retriever.search(search_query)
        context = self.retriever.format_context(search_query)

        return {
            "context": context,
            "results": results,
            "expanded_query": search_query,
        }
