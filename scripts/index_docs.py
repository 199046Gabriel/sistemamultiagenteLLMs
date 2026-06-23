#!/usr/bin/env python3
# scripts/index_docs.py — Indexa os documentos da pasta knowledge_base/

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
from rich.console import Console
from rag.indexer import build_index

console = Console()

def main():
    parser = argparse.ArgumentParser(
        description="Indexa documentos acadêmicos para busca semântica (RAG)"
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Reconstrói o índice do zero (apaga o índice existente)"
    )
    args = parser.parse_args()

    console.print("\n[bold cyan]📚 Assistente Acadêmico — Indexador de Documentos[/bold cyan]")
    console.print("[dim]Coloque seus PDFs e arquivos .txt em knowledge_base/ antes de rodar.[/dim]\n")

    if args.rebuild:
        console.print("[yellow]⚠ Modo rebuild: o índice existente será substituído.[/yellow]\n")

    try:
        build_index(force_rebuild=args.rebuild)
        console.print("\n[bold green]✅ Indexação concluída com sucesso![/bold green]")
        console.print("[dim]Agora você pode iniciar o assistente com: python main.py[/dim]\n")
    except Exception as e:
        console.print(f"\n[bold red]❌ Erro durante a indexação:[/bold red] {e}")
        console.print("[dim]Verifique se o Ollama está rodando: ollama serve[/dim]")
        sys.exit(1)

if __name__ == "__main__":
    main()
