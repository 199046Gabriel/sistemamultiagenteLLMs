#!/usr/bin/env python3
# main.py — Interface de terminal do Assistente Acadêmico IA
#
# Sistema multiagente com LLaMA local, RAG e MCP para apoio acadêmico.
# Uso: python main.py

from __future__ import annotations
import sys
import os
from pathlib import Path

# Garante que o diretório raiz está no PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box

from config import APP_NAME, APP_VERSION, LLM_MODEL
from agents.orchestrator import OrchestratorAgent
from agents.retriever_agent import RetrieverAgent
from agents.executor_agent import ExecutorAgent
from rag.indexer import get_vectorstore
from rag.retriever import Retriever

console = Console()

BANNER = f"""
╔══════════════════════════════════════════════════════════╗
║        🎓  {APP_NAME}  🎓         ║
║                  Versão {APP_VERSION}                          ║
║                                                          ║
║  Powered by LLaMA + LangChain + ChromaDB + MCP          ║
╚══════════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
[bold cyan]Comandos disponíveis:[/bold cyan]
  [green]sair[/green] / [green]exit[/green] / [green]quit[/green]  → Encerrar o assistente
  [green]ajuda[/green]                    → Mostrar esta mensagem
  [green]docs[/green]                     → Listar documentos indexados
  [green]limpar[/green]                   → Limpar a tela

[bold cyan]Exemplos de uso:[/bold cyan]
  → "O que é recursão?"
  → "Explica como funcionam os transformers"
  → "Cria um cronograma de estudos para Estruturas de Dados. Prova dia 30/06/2025"
  → "Tenho prova de IA na sexta. Tópicos: RAG, Agentes, Embeddings, LLMs"
  → "Dicas de estudo para programação"
  → "Qual a diferença entre BFS e DFS?"
"""


def print_banner():
    console.print(f"[bold cyan]{BANNER}[/bold cyan]")
    console.print(f"[dim]Modelo: {LLM_MODEL} | Digite [bold]ajuda[/bold] para ver os comandos disponíveis[/dim]\n")


def print_agent_step(label: str, detail: str = ""):
    """Exibe o passo atual do sistema de agentes."""
    icon_map = {
        "🔀 Orquestrador": "cyan",
        "📚 Recuperador": "blue",
        "🔧 Executor": "magenta",
        "🤖 Síntese": "green",
    }
    color = next((v for k, v in icon_map.items() if k in label), "white")
    msg = f"[{color}]{label}[/{color}]"
    if detail:
        msg += f" [dim]→ {detail}[/dim]"
    console.print(f"  {msg}")


def process_query(
    query: str,
    orchestrator: OrchestratorAgent,
    retriever_agent: RetrieverAgent,
    executor_agent: ExecutorAgent,
) -> str:
    """Pipeline principal: Orquestrador → Agente especializado → Síntese."""

    console.print()
    console.rule("[dim]Processando[/dim]", style="dim")

    # ── 1. Roteamento pelo Orquestrador ────────────────────────
    print_agent_step("🔀 Orquestrador", "analisando intenção...")
    routing = orchestrator.route(query)
    intent = routing["intent"]
    reason = routing.get("reason", "")
    print_agent_step("🔀 Orquestrador", f"intenção: [bold]{intent}[/bold] — {reason}")

    context_parts = []

    # ── 2. Agente especializado conforme intenção ───────────────
    if intent == "rag":
        print_agent_step("📚 Recuperador", "buscando na base de conhecimento...")
        rag_result = retriever_agent.retrieve(query)
        if rag_result["context"]:
            context_parts.append(f"[Contexto recuperado da base de conhecimento]\n{rag_result['context']}")
            n_results = len(rag_result["results"])
            print_agent_step("📚 Recuperador", f"{n_results} trechos relevantes encontrados")
        else:
            print_agent_step("📚 Recuperador", "nenhum trecho encontrado na base")

    elif intent in ("schedule", "tool"):
        print_agent_step("🔧 Executor", f"executando ferramenta (intent={intent})...")
        exec_result = executor_agent.execute(query, intent=intent)
        context_parts.append(
            f"[Resultado da ferramenta: {exec_result['tool_used']}]\n{exec_result['result']}"
        )
        print_agent_step("🔧 Executor", f"ferramenta: {exec_result['tool_used']}")

    else:
        # General: tenta RAG e, se não achar nada, vai pra resposta geral
        print_agent_step("📚 Recuperador", "tentando busca semântica...")
        rag_result = retriever_agent.retrieve(query, expand=False)
        if rag_result["results"]:
            context_parts.append(f"[Contexto recuperado]\n{rag_result['context']}")

    # ── 3. Síntese final pelo Orquestrador ─────────────────────
    print_agent_step("🤖 Síntese", "gerando resposta final...")
    full_context = "\n\n".join(context_parts) if context_parts else ""
    response = orchestrator.synthesize(query, full_context)

    console.rule(style="dim")
    console.print()
    return response


def main():
    print_banner()

    # ── Inicialização dos componentes ──────────────────────────
    console.print("[dim]Inicializando componentes...[/dim]")

    try:
        console.print("[dim]  Carregando base vetorial (ChromaDB)...[/dim]")
        vectorstore = get_vectorstore()
        retriever = Retriever(vectorstore)

        console.print("[dim]  Carregando agentes...[/dim]")
        orchestrator = OrchestratorAgent()
        retriever_agent = RetrieverAgent(retriever)
        executor_agent = ExecutorAgent()

        console.print("[bold green]✅ Sistema pronto![/bold green]\n")

        if not retriever.has_documents():
            console.print(
                Panel(
                    "⚠ Base de conhecimento vazia.\n"
                    "Adicione PDFs ou .txt em [bold]knowledge_base/[/bold] e rode:\n"
                    "  [cyan]python scripts/index_docs.py[/cyan]",
                    title="Aviso",
                    border_style="yellow",
                )
            )
            console.print()

    except Exception as e:
        console.print(f"[bold red]❌ Erro na inicialização:[/bold red] {e}")
        console.print(
            "\n[yellow]Verifique se o Ollama está rodando:[/yellow]\n"
            "  [cyan]ollama serve[/cyan]\n"
            "  [cyan]ollama pull llama3[/cyan]\n"
            "  [cyan]ollama pull nomic-embed-text[/cyan]"
        )
        sys.exit(1)

    # ── Loop principal de interação ─────────────────────────────
    while True:
        try:
            user_input = console.input("[bold green]Você:[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Encerrando... Até logo! 👋[/dim]")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        # Comandos especiais
        if cmd in ("sair", "exit", "quit", "q"):
            console.print("[dim]Até logo! Bons estudos! 📚👋[/dim]")
            break

        if cmd == "ajuda":
            console.print(Panel(HELP_TEXT, title="Ajuda", border_style="cyan", box=box.ROUNDED))
            continue

        if cmd == "limpar":
            os.system("clear" if os.name != "nt" else "cls")
            print_banner()
            continue

        if cmd == "docs":
            from tools.academic_tools import list_available_docs
            console.print(list_available_docs())
            continue

        # Processa a pergunta através do pipeline de agentes
        try:
            response = process_query(user_input, orchestrator, retriever_agent, executor_agent)
            console.print(
                Panel(
                    response,
                    title="[bold cyan]🤖 Assistente[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
        except Exception as e:
            console.print(f"[bold red]❌ Erro ao processar:[/bold red] {e}")
            console.print("[dim]Tente novamente ou verifique se o Ollama está rodando.[/dim]")

        console.print()


if __name__ == "__main__":
    main()
