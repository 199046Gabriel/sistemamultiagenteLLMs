# mcp_server/server.py — Servidor MCP com FastMCP
#
# Expõe as ferramentas do assistente acadêmico via Model Context Protocol,
# permitindo que qualquer cliente MCP acesse as tools de forma padronizada.

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastmcp import FastMCP
from tools.academic_tools import (
    get_current_date,
    create_schedule,
    list_available_docs,
    get_study_tips,
)
from config import MCP_HOST, MCP_PORT

# Instancia o servidor MCP
mcp = FastMCP(
    name="academic-assistant-mcp",
    instructions=(
        "Servidor MCP do Assistente Acadêmico. "
        "Fornece ferramentas para criação de cronogramas de estudo, "
        "dicas de aprendizado e gestão de documentos acadêmicos."
    ),
)


# ── Registra cada tool no servidor MCP ────────────────────────

@mcp.tool()
def tool_get_current_date() -> str:
    """Retorna a data e hora atual em português."""
    return get_current_date()


@mcp.tool()
def tool_create_schedule(
    topics: list[str],
    exam_date: str,
    hours_per_day: int = 2,
) -> str:
    """
    Cria um cronograma de estudos personalizado.

    Args:
        topics: Lista de tópicos a estudar (ex: ["Recursão", "Árvores", "Grafos"]).
        exam_date: Data da prova no formato DD/MM/AAAA (ex: "20/06/2025").
        hours_per_day: Horas de estudo disponíveis por dia (padrão: 2).

    Returns:
        Cronograma formatado com a distribuição dos tópicos por dia.
    """
    return create_schedule(topics=topics, exam_date=exam_date, hours_per_day=hours_per_day)


@mcp.tool()
def tool_list_documents() -> str:
    """
    Lista todos os documentos disponíveis na base de conhecimento.

    Returns:
        Lista de arquivos indexados com nome e tamanho.
    """
    return list_available_docs()


@mcp.tool()
def tool_get_study_tips(topic: str = "") -> str:
    """
    Retorna dicas e técnicas de estudo.

    Args:
        topic: Tópico ou disciplina (ex: "programação", "matemática").
               Deixe vazio para dicas gerais.

    Returns:
        Lista de dicas de estudo adequadas ao tópico.
    """
    return get_study_tips(topic=topic)


# ── Ponto de entrada ───────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Servidor MCP do Assistente Acadêmico")
    parser.add_argument("--host", default=MCP_HOST, help="Host do servidor")
    parser.add_argument("--port", type=int, default=MCP_PORT, help="Porta do servidor")
    parser.add_argument("--transport", default="stdio",
                        choices=["stdio", "sse"],
                        help="Transporte MCP (stdio para integração local, sse para HTTP)")
    args = parser.parse_args()

    if args.transport == "sse":
        print(f"🚀 Servidor MCP rodando em http://{args.host}:{args.port}")
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        print("🚀 Servidor MCP rodando via stdio (pronto para integração com agentes)")
        mcp.run(transport="stdio")
