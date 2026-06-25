# 🎓 Assistente Acadêmico IA — Sistema Multiagente com LLMs

> Sistema multiagente baseado em LLaMA local para apoio aos estudos: responde perguntas sobre matérias, cria cronogramas de estudo e busca contexto em documentos acadêmicos.

---

## 👥 Integrantes da Equipe

Gabriel Castanho da Rosa | 199046

---

## 📋 Descrição do Problema

Estudantes universitários frequentemente têm dificuldade em:
1. Revisar conteúdos de múltiplas disciplinas de forma eficiente.
2. Organizar cronogramas de estudo realistas antes de provas.
3. Encontrar explicações claras nos materiais do curso (PDFs, slides, notas).

O problema se beneficia de uma arquitetura multiagente porque diferentes tipos de demanda exigem estratégias distintas: uma pergunta conceitual requer busca semântica em documentos; um pedido de cronograma requer raciocínio sobre datas e distribuição de tópicos; ambos requerem síntese linguística fluente. Delegar cada responsabilidade a um agente especializado torna o sistema mais preciso e manutenível do que um agente único tentando fazer tudo.

---

## 🎯 Objetivo da Solução

Construir um assistente de terminal baseado em LLaMA local que:
- Responda perguntas acadêmicas com base em documentos indexados (RAG).
- Gere cronogramas de estudos personalizados a partir de tópicos e datas informadas.
- Forneça dicas de aprendizado e gestão do tempo.
- Opere 100% offline, sem dependência de APIs pagas.

---

## 🏗️ Arquitetura Multiagente

```
┌─────────────────────────────────────────────────────┐
│                    USUÁRIO (Terminal)                 │
└──────────────────────┬──────────────────────────────┘
                       │ query
                       ▼
┌─────────────────────────────────────────────────────┐
│             🔀 AGENTE ORQUESTRADOR                   │
│  - Classifica a intenção (rag / schedule / tool /   │
│    general)                                          │
│  - Roteia para o agente especializado               │
│  - Sintetiza a resposta final                        │
└────────┬─────────────────────────┬──────────────────┘
         │ intent=rag              │ intent=schedule/tool
         ▼                         ▼
┌─────────────────┐    ┌──────────────────────────────┐
│  📚 AGENTE      │    │       🔧 AGENTE EXECUTOR      │
│  RECUPERADOR    │    │  - Interpreta parâmetros      │
│  - Expande a    │    │  - Chama tools via MCP Client │
│    query        │    │  - Ferramentas:               │
│  - Busca no     │    │    • create_schedule()        │
│    ChromaDB     │    │    • get_study_tips()         │
│  - Retorna      │    │    • list_available_docs()    │
│    trechos      │    │    • get_current_date()       │
│    relevantes   │    └──────────────┬───────────────┘
└────────┬────────┘                   │
         │ context                    │ result
         └──────────┬─────────────────┘
                    │
                    ▼
         ┌──────────────────┐
         │  SÍNTESE (LLaMA) │
         │  Resposta final  │
         └──────────────────┘
```

### Por que esta arquitetura?
- Um agente único teria que lidar com busca semântica, execução de lógica de negócio e síntese linguística ao mesmo tempo, tornando o sistema mais difícil de manter e menos preciso em cada tarefa.
- A separação permite otimizar cada agente independentemente (ex: temperatura diferente no LLM para roteamento vs síntese).

---

## 🤖 Papel de Cada Agente

### 1. Agente Orquestrador (`agents/orchestrator.py`)
**Responsabilidade:** Ponto de entrada. Analisa a intenção da mensagem e decide qual agente chamar. Ao final, sintetiza a resposta consolidando o contexto retornado pelos outros agentes.

### 2. Agente Recuperador (`agents/retriever_agent.py`)
**Responsabilidade:** Executa busca semântica na base vetorial. Antes da busca, usa o LLM para expandir a query e melhorar o recall. Retorna os trechos mais relevantes com referência à fonte.

### 3. Agente Executor (`agents/executor_agent.py`)
**Responsabilidade:** Seleciona e executa ferramentas concretas. Para cronogramas, usa o LLM para extrair tópicos e datas da mensagem do usuário e chama a ferramenta adequada via MCP Client.

---

## 🔧 Tools Disponíveis

| Tool | Descrição | Parâmetros |
|------|-----------|------------|
| `get_current_date` | Retorna data e hora atual em PT-BR | — |
| `create_schedule` | Gera cronograma de estudos personalizado | `topics[]`, `exam_date`, `hours_per_day` |
| `list_available_docs` | Lista documentos na base de conhecimento | — |
| `get_study_tips` | Dicas de estudo adaptadas ao tópico | `topic` (opcional) |

---

## 🔌 Como o MCP foi utilizado

O **Model Context Protocol (MCP)** é implementado via `fastmcp` em dois componentes:

1. **Servidor MCP** (`mcp_server/server.py`): expõe todas as tools acadêmicas como endpoints MCP padronizados. Pode rodar em modo `stdio` (para integração local entre agentes) ou `sse` (para acesso HTTP remoto).

2. **Cliente MCP** (`mcp_server/client.py`): abstrai o acesso às tools, permitindo que os agentes chamem ferramentas via interface padronizada sem conhecer a implementação interna. Isso desacopla os agentes das tools.

```python
# Exemplo de uso do cliente MCP pelos agentes
client = MCPClient(mode="local")
result = client.call("create_schedule", {
    "topics": ["Recursão", "Grafos"],
    "exam_date": "30/06/2025",
    "hours_per_day": 2
})
```

### Executar o servidor MCP isolado (modo HTTP/SSE):
```bash
python mcp_server/server.py --transport sse --port 8765
```

---

## 📖 Estratégia de RAG

O sistema usa RAG em três etapas:

1. **Expansão da query**: o LLM reescreve a pergunta do usuário de forma mais técnica e completa para melhorar o recall na busca vetorial.

2. **Busca semântica**: os documentos são convertidos em embeddings e armazenados no ChromaDB. A query expandida é convertida no mesmo espaço vetorial e os `k=4` chunks mais próximos são recuperados.

3. **Geração aumentada**: os chunks recuperados são inseridos no prompt do Agente Orquestrador como contexto antes da geração da resposta final.

```
query do usuário
      ↓
[LLM expande a query]
      ↓
[Embedding da query expandida]
      ↓
[Busca por similaridade no ChromaDB]  ←── [Documentos indexados]
      ↓
[Top-4 chunks mais relevantes]
      ↓
[LLM gera resposta com contexto]
```

---

## 🗂️ Base de Conhecimento

**Origem:** Documentos acadêmicos em formato Markdown e PDF colocados na pasta `knowledge_base/`.

**Documentos de exemplo incluídos:**
- `estruturas_de_dados.md` — Recursão, árvores, grafos, ordenação, complexidade, DP, hashing.
- `inteligencia_artificial.md` — Machine Learning, Redes Neurais, LLMs, RAG, Agentes, Embeddings.

**Como adicionar seus documentos:**
1. Copie seus PDFs ou arquivos `.txt`/`.md` para `knowledge_base/`.
2. Rode `python scripts/index_docs.py --rebuild`.

---

## 🔢 Tecnologia de Embeddings e Armazenamento Vetorial

| Componente | Tecnologia | Justificativa |
|------------|-----------|---------------|
| Modelo de embeddings | `nomic-embed-text` via Ollama | Local, gratuito, bom desempenho em PT-BR |
| Banco vetorial | **ChromaDB** | Local, sem servidor externo, persistência em disco |
| Chunking | RecursiveCharacterTextSplitter (800 chars, overlap 100) | Preserva contexto entre chunks |
| Similarity | Cosine similarity (padrão Chroma) | Padrão eficiente para embeddings de texto |

---

## 🦙 Modelo Local Utilizado

**Modelo:** `llama3` (Meta LLaMA 3 8B)  
**Executor:** [Ollama](https://ollama.com)  
**Justificativa:** O LLaMA 3 8B é o melhor balanço entre qualidade de resposta e requisitos de hardware (roda em 8GB de VRAM ou CPU com 16GB de RAM). O Ollama facilita o download, gerenciamento e API local dos modelos.

Configuração no `config.py`:
```python
LLM_MODEL = "llama3"          # pode trocar por "llama3:70b", "mistral", "phi3"...
EMBED_MODEL = "nomic-embed-text"
```

---

## 📦 Dependências do Projeto

```
ollama>=0.3.0          # client Python para Ollama
langchain>=0.2.0        # framework de orquestração de LLMs
langchain-community>=0.2.0
langchain-ollama>=0.1.0 # integração LangChain + Ollama
chromadb>=0.5.0         # banco vetorial local
pypdf>=4.0.0            # leitura de PDFs
fastmcp>=0.4.0          # servidor e cliente MCP
rich>=13.0.0            # interface de terminal colorida
python-dateutil>=2.9.0  # parsing de datas
pydantic>=2.0.0         # validação de dados
```

---

## ⚙️ Instalação e Execução

### Pré-requisitos
- Python 3.10+
- [Ollama](https://ollama.com) instalado

### Instalação rápida (recomendado)
```bash
git clone https://github.com/SEU_USUARIO/academic-assistant.git
cd academic-assistant
bash setup.sh
```

### Instalação manual

#### 1. Clonar o repositório
```bash
git clone https://github.com/SEU_USUARIO/academic-assistant.git
cd academic-assistant
```

#### 2. Criar ambiente virtual e instalar dependências
```bash
python3 -m venv .venv
source .venv/bin/activate      # Linux/Mac
# ou: .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

#### 3. Instalar e iniciar o Ollama
```bash
# Instalar Ollama (Linux/Mac):
curl -fsSL https://ollama.com/install.sh | sh

# Baixar os modelos:
ollama pull llama3
ollama pull nomic-embed-text

# Iniciar o servidor Ollama (deixe rodando em outro terminal):
ollama serve
```

#### 4. Indexar os documentos
```bash
python scripts/index_docs.py
```
> Para re-indexar do zero: `python scripts/index_docs.py --rebuild`

#### 5. Verificar o ambiente
```bash
python scripts/check_setup.py
```

#### 6. Iniciar o assistente
```bash
python main.py
```

---

## 💻 Exemplos de Uso pelo Terminal

```
🎓  Assistente Acadêmico IA

Você: O que é recursão?

  🔀 Orquestrador → intenção: rag
  📚 Recuperador → buscando na base de conhecimento...
  📚 Recuperador → 4 trechos relevantes encontrados
  🤖 Síntese → gerando resposta final...

╭─ 🤖 Assistente ────────────────────────────────────────────╮
│ Recursão é uma técnica em que uma função chama a si mesma  │
│ para resolver subproblemas menores. Todo algoritmo         │
│ recursivo precisa de dois componentes principais:          │
│ o caso base (condição de parada) e o caso recursivo...     │
╰────────────────────────────────────────────────────────────╯
```

```
Você: Tenho prova de Estruturas de Dados na sexta-feira 27/06/2025.
      Tópicos: Recursão, Árvores Binárias, Grafos, Ordenação

  🔀 Orquestrador → intenção: schedule
  🔧 Executor → executando ferramenta create_schedule...

╭─ 🤖 Assistente ────────────────────────────────────────────╮
│ 📅 CRONOGRAMA DE ESTUDOS                                   │
│ ========================================                   │
│ 🎯 Prova: 27/06/2025                                       │
│ 📆 Dias disponíveis: 6                                     │
│ ⏱ Carga diária: 2h/dia                                    │
│                                                            │
│   Dia 01 | Seg 23/06 | Recursão                           │
│   Dia 02 | Ter 24/06 | Árvores Binárias                   │
│   Dia 03 | Qua 25/06 | Grafos                             │
│   Dia 04 | Qui 26/06 | Ordenação                          │
│   Revisão | Sex 26/06 | 🔁 Revisão geral                  │
│   📝 PROVA | 27/06                                        │
╰────────────────────────────────────────────────────────────╯
```

```
Você: dicas de estudo para programação

  🔀 Orquestrador → intenção: tool
  🔧 Executor → executando ferramenta get_study_tips...

╭─ 🤖 Assistente ────────────────────────────────────────────╮
│ 💡 Dicas de estudo para Programação:                       │
│   💻 Pratique código todo dia, mesmo 20 minutos.           │
│   🐛 Não tenha medo de erros — debugar é aprender.        │
│   📖 Leia código de outras pessoas para aprender padrões.  │
│   🏗 Construa projetos pequenos para fixar conceitos.      │
╰────────────────────────────────────────────────────────────╯
```

### Servidor MCP (modo HTTP)
```bash
# Em um terminal separado:
python mcp_server/server.py --transport sse --port 8765

# Em outro terminal (exemplo de chamada curl):
curl -X POST http://localhost:8765 \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_current_date", "params": {}}'
```

---

## 📁 Estrutura do Projeto

```
academic-assistant/
├── main.py                    # Ponto de entrada — interface de terminal
├── config.py                  # Configurações centrais (modelos, caminhos, etc.)
├── requirements.txt           # Dependências Python
├── setup.sh                   # Script de instalação automatizada
│
├── agents/                    # Agentes do sistema
│   ├── orchestrator.py        # Agente Orquestrador (roteamento + síntese)
│   ├── retriever_agent.py     # Agente Recuperador (RAG)
│   └── executor_agent.py      # Agente Executor (tools)
│
├── rag/                       # Módulo de Retrieval-Augmented Generation
│   ├── indexer.py             # Indexação de documentos no ChromaDB
│   └── retriever.py           # Busca semântica
│
├── tools/                     # Ferramentas disponíveis para os agentes
│   └── academic_tools.py      # create_schedule, get_study_tips, etc.
│
├── mcp_server/                # Servidor e cliente MCP
│   ├── server.py              # Servidor FastMCP com as tools expostas
│   └── client.py              # Cliente MCP usado pelos agentes
│
├── scripts/                   # Scripts utilitários
│   ├── index_docs.py          # Indexa a knowledge_base no ChromaDB
│   └── check_setup.py         # Verifica se o ambiente está correto
│
├── knowledge_base/            # Documentos acadêmicos para RAG
│   ├── estruturas_de_dados.md # Exemplo: ED e Algoritmos
│   └── inteligencia_artificial.md # Exemplo: IA e ML
│
└── chroma_db/                 # Índice vetorial (gerado automaticamente)
```

---

## 🔧 Configuração Avançada

Edite `config.py` para personalizar:

```python
# Trocar o modelo LLM
LLM_MODEL = "mistral"        # alternativas: phi3, llama3:70b, codellama

# Ajustar parâmetros do RAG
RAG_TOP_K = 4                # quantos chunks recuperar
CHUNK_SIZE = 800             # tamanho dos chunks
CHUNK_OVERLAP = 100          # sobreposição entre chunks
```

---

## 📄 Licença

MIT License — veja [LICENSE](LICENSE) para detalhes.
