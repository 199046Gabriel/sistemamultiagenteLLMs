# agents/executor_agent.py — Agente Executor
#
# Responsabilidade: interpretar a intenção do usuário, selecionar a
# ferramenta correta e executá-la com os parâmetros extraídos da mensagem.

from __future__ import annotations
import json
import re
from langchain_ollama import OllamaLLM
from rich.console import Console
from tools.academic_tools import call_tool, get_current_date, TOOLS_REGISTRY
from config import LLM_MODEL, OLLAMA_BASE_URL

console = Console()

TOOL_SELECTION_PROMPT = """\
Você é um agente executor de um assistente acadêmico.
Sua tarefa é identificar qual ferramenta usar e extrair os parâmetros necessários.

Ferramentas disponíveis:
{tools_description}

Mensagem do usuário: "{query}"
Data atual: {current_date}

Responda SOMENTE com um JSON no formato:
{{
  "tool": "<nome_da_ferramenta>",
  "params": {{<parâmetros conforme a ferramenta>}}
}}

Regras:
- Para create_schedule: extraia a lista de tópicos e a data da prova da mensagem.
  Se a data não for mencionada, use 7 dias a partir de hoje.
  Se os tópicos não forem mencionados, use ["Revisão Geral"].
- Para get_study_tips: extraia o tópico da mensagem (pode ser vazio "").
- Para list_available_docs e get_current_date: params deve ser {{}}.
- Se nenhuma ferramenta se encaixar, use get_current_date com params {{}}.
"""

SCHEDULE_EXTRACT_PROMPT = """\
Extraia da mensagem abaixo:
1. Uma lista de tópicos de estudo (array de strings)
2. A data da prova (string no formato DD/MM/AAAA)
3. Horas de estudo por dia (inteiro, padrão 2)

Mensagem: "{query}"
Data atual: {current_date}

Se a data não for mencionada, calcule 7 dias a partir da data atual.
Se tópicos não forem mencionados, retorne ["Revisão Geral"].

Responda SOMENTE com JSON:
{{"topics": [...], "exam_date": "DD/MM/AAAA", "hours_per_day": N}}
"""


class ExecutorAgent:
    """
    Agente Executor — seleciona e executa ferramentas com base na intenção.
    """

    def __init__(self):
        self.llm = OllamaLLM(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )

    def _build_tools_description(self) -> str:
        lines = []
        for name, entry in TOOLS_REGISTRY.items():
            lines.append(f"  - {name}: {entry['description']}")
        return "\n".join(lines)

    def _extract_json(self, text: str) -> dict | None:
        """Extrai o primeiro JSON válido do texto."""
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None

    def _handle_schedule(self, query: str) -> str:
        """Extrai parâmetros e cria o cronograma."""
        current_date = get_current_date()
        prompt = SCHEDULE_EXTRACT_PROMPT.format(query=query, current_date=current_date)
        raw = self.llm.invoke(prompt).strip()
        data = self._extract_json(raw)

        if not data:
            # Fallback: cronograma genérico
            return call_tool("create_schedule", {
                "topics": ["Revisão Geral"],
                "exam_date": "próxima semana",
                "hours_per_day": 2,
            })

        return call_tool("create_schedule", {
            "topics": data.get("topics", ["Revisão Geral"]),
            "exam_date": data.get("exam_date", ""),
            "hours_per_day": data.get("hours_per_day", 2),
        })

    def execute(self, query: str, intent: str = "tool") -> dict:
        """
        Executa a ação adequada conforme a intenção e a mensagem.

        Returns:
            dict com 'result' (string) e 'tool_used' (string)
        """
        # Cronograma tem extração especializada
        q_lower = query.lower()
        if intent == "schedule" or any(w in q_lower for w in
                                        ["cronograma", "planejar", "organizar semana",
                                         "distribuir estudo", "plano de estudo"]):
            result = self._handle_schedule(query)
            return {"result": result, "tool_used": "create_schedule"}

        # Para outras tools, pede ao LLM para selecionar
        current_date = get_current_date()
        prompt = TOOL_SELECTION_PROMPT.format(
            tools_description=self._build_tools_description(),
            query=query,
            current_date=current_date,
        )
        raw = self.llm.invoke(prompt).strip()
        data = self._extract_json(raw)

        if not data:
            # Fallback: dicas gerais
            result = call_tool("get_study_tips", {"topic": query})
            return {"result": result, "tool_used": "get_study_tips"}

        tool_name = data.get("tool", "get_study_tips")
        params = data.get("params", {})

        result = call_tool(tool_name, params)
        return {"result": result, "tool_used": tool_name}
