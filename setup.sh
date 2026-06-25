#!/usr/bin/env bash
# setup.sh — Instalação automatizada do Assistente Acadêmico IA
# Uso: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║      🎓  Assistente Acadêmico IA — Setup Inicial         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Verifica Python ────────────────────────────────────────────
echo "→ Verificando Python..."
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 não encontrado. Instale em https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1)
echo "  ✓ $PYTHON_VERSION"

# ── Cria ambiente virtual ──────────────────────────────────────
echo ""
echo "→ Criando ambiente virtual (.venv)..."
python3 -m venv .venv
echo "  ✓ Ambiente virtual criado em .venv/"

# Ativa o venv
source .venv/bin/activate

# ── Atualiza pip ───────────────────────────────────────────────
echo ""
echo "→ Atualizando pip..."
pip install --upgrade pip --quiet

# ── Instala dependências ───────────────────────────────────────
echo ""
echo "→ Instalando dependências Python (pode demorar alguns minutos)..."
pip install -r requirements.txt --quiet
echo "  ✓ Dependências instaladas"

# ── Verifica Ollama ────────────────────────────────────────────
echo ""
echo "→ Verificando Ollama..."
if ! command -v ollama &>/dev/null; then
    echo "  ⚠ Ollama não encontrado. Instale em https://ollama.com"
    echo "    Após instalar, execute:"
    echo "    ollama pull llama3"
    echo "    ollama pull nomic-embed-text"
else
    echo "  ✓ Ollama instalado"
    
    # Verifica se o servidor está rodando
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "  ✓ Ollama server está rodando"
        
        echo ""
        echo "→ Baixando modelos necessários..."
        echo "  Baixando llama3 (pode demorar na primeira vez)..."
        ollama pull llama3
        echo "  Baixando nomic-embed-text..."
        ollama pull nomic-embed-text
        echo "  ✓ Modelos baixados"
    else
        echo "  ⚠ Ollama server não está rodando. Execute: ollama serve"
    fi
fi

# ── Cria pastas necessárias ────────────────────────────────────
echo ""
echo "→ Criando estrutura de diretórios..."
mkdir -p knowledge_base chroma_db
echo "  ✓ Pastas criadas"

# ── Indexa documentos de exemplo ──────────────────────────────
echo ""
echo "→ Indexando documentos de exemplo da knowledge_base/..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    python scripts/index_docs.py || echo "  ⚠ Indexação falhou (Ollama pode estar offline)"
else
    echo "  ⚠ Pulando indexação (Ollama offline). Rode depois: python scripts/index_docs.py"
fi

# ── Concluído ──────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅  Instalação concluída!                               ║"
echo "║                                                          ║"
echo "║  Para iniciar o assistente:                              ║"
echo "║    source .venv/bin/activate                             ║"
echo "║    python main.py                                        ║"
echo "║                                                          ║"
echo "║  Para verificar o ambiente:                              ║"
echo "║    python scripts/check_setup.py                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
