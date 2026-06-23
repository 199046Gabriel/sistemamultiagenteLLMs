# rag/indexer.py — Indexa documentos da base de conhecimento no ChromaDB

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from config import (
    KNOWLEDGE_BASE_DIR, CHROMA_DB_DIR, EMBED_MODEL,
    CHROMA_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP, OLLAMA_BASE_URL
)

console = Console()


def load_documents(directory: Path) -> list:
    """Carrega todos os PDFs e arquivos .txt da pasta knowledge_base."""
    docs = []

    # PDFs
    pdf_files = list(directory.glob("**/*.pdf"))
    for pdf_path in pdf_files:
        try:
            loader = PyPDFLoader(str(pdf_path))
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source_file"] = pdf_path.name
                doc.metadata["file_type"] = "pdf"
            docs.extend(loaded)
            console.print(f"  [green]✓[/green] {pdf_path.name} ({len(loaded)} páginas)")
        except Exception as e:
            console.print(f"  [red]✗[/red] Erro ao carregar {pdf_path.name}: {e}")

    # TXT / Markdown
    text_files = list(directory.glob("**/*.txt")) + list(directory.glob("**/*.md"))
    for txt_path in text_files:
        try:
            loader = TextLoader(str(txt_path), encoding="utf-8")
            loaded = loader.load()
            for doc in loaded:
                doc.metadata["source_file"] = txt_path.name
                doc.metadata["file_type"] = "text"
            docs.extend(loaded)
            console.print(f"  [green]✓[/green] {txt_path.name}")
        except Exception as e:
            console.print(f"  [red]✗[/red] Erro ao carregar {txt_path.name}: {e}")

    return docs


def split_documents(docs: list) -> list:
    """Divide os documentos em chunks para indexação."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    return chunks


def build_index(force_rebuild: bool = False) -> Chroma:
    """
    Constrói ou carrega o índice vetorial.
    Se force_rebuild=True, reconstrói do zero.
    """
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    embeddings = OllamaEmbeddings(
        model=EMBED_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

    # Se já existe e não forçamos rebuild, apenas carrega
    if CHROMA_DB_DIR.exists() and any(CHROMA_DB_DIR.iterdir()) and not force_rebuild:
        console.print("[dim]Carregando índice existente...[/dim]")
        vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DB_DIR),
        )
        count = vectorstore._collection.count()
        console.print(f"[green]✓ Índice carregado com {count} chunks.[/green]")
        return vectorstore

    # Rebuild
    console.print("\n[bold]Indexando base de conhecimento...[/bold]")

    docs = load_documents(KNOWLEDGE_BASE_DIR)
    if not docs:
        console.print(
            "[yellow]⚠ Nenhum documento encontrado em knowledge_base/. "
            "Adicione PDFs ou arquivos .txt e rode novamente.[/yellow]"
        )
        # Retorna índice vazio mas funcional
        vectorstore = Chroma(
            collection_name=CHROMA_COLLECTION,
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DB_DIR),
        )
        return vectorstore

    console.print(f"\n[dim]Dividindo {len(docs)} documentos em chunks...[/dim]")
    chunks = split_documents(docs)
    console.print(f"[dim]{len(chunks)} chunks criados.[/dim]")

    console.print("[dim]Gerando embeddings e salvando no ChromaDB...[/dim]")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=CHROMA_COLLECTION,
        persist_directory=str(CHROMA_DB_DIR),
    )
    console.print(f"[green]✓ Indexação concluída: {len(chunks)} chunks salvos.[/green]")
    return vectorstore


def get_vectorstore() -> Chroma:
    """Retorna o vectorstore (cria se não existir)."""
    return build_index(force_rebuild=False)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Indexador da base de conhecimento")
    parser.add_argument("--rebuild", action="store_true", help="Reconstrói o índice do zero")
    args = parser.parse_args()
    build_index(force_rebuild=args.rebuild)
