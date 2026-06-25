#!/usr/bin/env python3
# scripts/check_setup.py — Verifica se o ambiente está configurado corretamente

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import subprocess
from rich.console import Console
from rich.table import Table

console = Console()


def check_ollama_running():
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def check_ollama_model(model_name: str):
    try:
        import urllib.request, json
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3) as r:
            data = json.loads(r.read())
            models = [m["name"].split(":")[0] for m in data.get("models", [])]
            return model_name.split(":")[0] in models
    except Exception:
        return False


def check_python_package(pkg: str):
    try:
        __import__(pkg.replace("-", "_"))
        return True
    except ImportError:
        return False


def check_knowledge_base():
    from config import KNOWLEDGE_BASE_DIR
    files = list(KNOWLEDGE_BASE_DIR.glob("**/*.pdf")) + list(KNOWLEDGE_BASE_DIR.glob("**/*.txt"))
    return len(files), files


def check_chroma_index():
    from config import CHROMA_DB_DIR
    if not CHROMA_DB_DIR.exists():
        return False
    return any(CHROMA_DB_DIR.iterdir())


def main():
    from config import LLM_MODEL, EMBED_MODEL

    console.print("\n[bold cyan]🔍 Verificação do Ambiente — Assistente Acadêmico IA[/bold cyan]\n")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Componente", style="bold")
    table.add_column("Status")
    table.add_column("Detalhe")

    all_ok = True

    # Ollama rodando
    ollama_ok = check_ollama_running()
    table.add_row(
        "Ollama (servidor)",
        "[green]✓ OK[/green]" if ollama_ok else "[red]✗ FALHOU[/red]",
        "http://localhost:11434" if ollama_ok else "Rode: ollama serve"
    )
    if not ollama_ok:
        all_ok = False

    # Modelo LLM
    llm_ok = check_ollama_model(LLM_MODEL) if ollama_ok else False
    table.add_row(
        f"Modelo LLM ({LLM_MODEL})",
        "[green]✓ OK[/green]" if llm_ok else "[yellow]⚠ Não encontrado[/yellow]",
        "Disponível" if llm_ok else f"Rode: ollama pull {LLM_MODEL}"
    )
    if not llm_ok:
        all_ok = False

    # Modelo de Embeddings
    embed_ok = check_ollama_model(EMBED_MODEL) if ollama_ok else False
    table.add_row(
        f"Embeddings ({EMBED_MODEL})",
        "[green]✓ OK[/green]" if embed_ok else "[yellow]⚠ Não encontrado[/yellow]",
        "Disponível" if embed_ok else f"Rode: ollama pull {EMBED_MODEL}"
    )
    if not embed_ok:
        all_ok = False

    # Pacotes Python
    packages = ["langchain", "chromadb", "fastmcp", "rich", "pypdf"]
    for pkg in packages:
        ok = check_python_package(pkg)
        table.add_row(
            f"Python: {pkg}",
            "[green]✓ OK[/green]" if ok else "[red]✗ Faltando[/red]",
            "Instalado" if ok else f"pip install {pkg}"
        )
        if not ok:
            all_ok = False

    # Base de conhecimento
    n_files, files = check_knowledge_base()
    table.add_row(
        "Base de conhecimento",
        "[green]✓ OK[/green]" if n_files > 0 else "[yellow]⚠ Vazia[/yellow]",
        f"{n_files} arquivo(s)" if n_files > 0 else "Adicione PDFs em knowledge_base/"
    )

    # Índice ChromaDB
    chroma_ok = check_chroma_index()
    table.add_row(
        "Índice ChromaDB",
        "[green]✓ OK[/green]" if chroma_ok else "[yellow]⚠ Não indexado[/yellow]",
        "Pronto" if chroma_ok else "Rode: python scripts/index_docs.py"
    )

    console.print(table)

    if all_ok:
        console.print("\n[bold green]✅ Tudo pronto! Inicie o assistente com: python main.py[/bold green]\n")
    else:
        console.print("\n[bold yellow]⚠ Alguns componentes precisam de atenção (veja a tabela acima).[/bold yellow]")
        console.print("[dim]Consulte o README.md para instruções de instalação.[/dim]\n")


if __name__ == "__main__":
    main()
