# agents/orchestrator.py — Agente Orquestrador
#
# Responsabilidade: analisar a intenção do usuário e decidir qual agente
# deve tratar a requisição (Recuperador ou Executor), além de montar
# a resposta final consolidada.

from __future__ import annotations
import json
import re
from langchain_ollama import OllamaLLM
from rich.console import Console
from config import LLM_MODEL, OLLAMA_BASE_URL

console = Console()

# Prompt de roteamento: o orquestrador decide o tipo de tarefa
ROUTING_PROMPT = """\
Você é o orquestrador de um assistente acadêmico inteligente.
Sua única tarefa agora é classificar a intenção do usuário.

Mensagem do usuário: "{query}"

Classifique em EXATAMENTE UMA das categorias abaixo e responda APENAS com o JSON:

- "rag"        → pergunta sobre conteúdo de matérias, conceitos, teorias, explicações
- "schedule"   → criação de cronograma, planejamento de estudos, organização de tempo
- "tool"       → outras ferramentas: listar documentos, dicas de estudo, data atual
- "general"    → conversa geral, saudações, dúvidas que não se encaixam acima

Responda SOMENTE com este JSON (sem texto adicional):
{{"intent": "<categoria>", "reason": "<motivo em uma frase>"}}
"""

# Prompt final: sintetiza a resposta para o usuário
SYNTHESIS_PROMPT = """\
Você é um assistente acadêmico amigável, claro e objetivo.
Responda ao aluno em português, de forma didática e encorajadora.

Pergunta do aluno: {query}

Contexto disponível:
{context}

Instruções:
- Se o contexto contiver fontes de documentos, cite-as naturalmente.
- Se houver um cronograma ou dicas, apresente-os formatados e claros.
- Se não houver contexto suficiente, seja honesto e oriente o aluno.
- Mantenha tom motivador e acadêmico.
- Responda em português do Brasil.
"""


class OrchestratorAgent:
    """
    Agente Orquestrador — analisa a intenção e coordena os demais agentes.
    """

    def __init__(self):
        self.llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,   # baixo para roteamento preciso
        )
        self.synthesis_llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,   # mais criativo para resposta final
        )

    def route(self, query: str) -> dict:
        """Determina a intenção da mensagem do usuário."""
        prompt = ROUTING_PROMPT.format(query=query)
        raw = self.llm.invoke(prompt).strip()

        # Extrai o JSON da resposta (mesmo se houver texto ao redor)
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        if match:
            try:
                result = json.loads(match.group())
                intent = result.get("intent", "general")
                reason = result.get("reason", "")
                return {"intent": intent, "reason": reason}
            except json.JSONDecodeError:
                pass

        # Fallback por palavras-chave se o LLM não retornar JSON válido
        q = query.lower()
        if any(w in q for w in ["cronograma", "prova", "estudar", "planejar", "semana", "dias"]):
            return {"intent": "schedule", "reason": "palavras-chave de cronograma"}
        if any(w in q for w in ["explica", "o que é", "como funciona", "conceito", "teoria", "defin"]):
            return {"intent": "rag", "reason": "palavras-chave de explicação"}
        if any(w in q for w in ["documento", "arquivo", "dica", "data", "listar"]):
            return {"intent": "tool", "reason": "palavras-chave de ferramenta"}
        return {"intent": "general", "reason": "intenção não identificada"}

    def synthesize(self, query: str, context: str) -> str:
        """Gera a resposta final consolidando o contexto dos agentes."""
        prompt = SYNTHESIS_PROMPT.format(query=query, context=context or "Nenhum contexto adicional disponível.")
        return self.synthesis_llm.invoke(prompt).strip()
