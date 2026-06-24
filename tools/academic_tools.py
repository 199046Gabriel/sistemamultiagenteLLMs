# tools/academic_tools.py — Ferramentas disponíveis para os agentes

from __future__ import annotations
import json
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import KNOWLEDGE_BASE_DIR


# ── Tool: data atual ───────────────────────────────────────────

def get_current_date() -> str:
    """Retorna a data e hora atual formatada em português."""
    now = datetime.now()
    days_pt = ["segunda-feira", "terça-feira", "quarta-feira",
               "quinta-feira", "sexta-feira", "sábado", "domingo"]
    months_pt = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                 "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    day_name = days_pt[now.weekday()]
    month_name = months_pt[now.month - 1]
    return (
        f"{day_name}, {now.day} de {month_name} de {now.year} "
        f"— {now.strftime('%H:%M')}"
    )


# ── Tool: criar cronograma ─────────────────────────────────────

def create_schedule(topics: list[str], exam_date: str, hours_per_day: int = 2) -> str:
    """
    Cria um cronograma de estudos distribuindo os tópicos até a data da prova.

    Args:
        topics: lista de tópicos a estudar
        exam_date: data da prova (ex: '2025-06-20' ou '20/06/2025')
        hours_per_day: horas de estudo por dia (padrão: 2)

    Returns:
        Cronograma formatado como string.
    """
    try:
        try:
            exam_dt = date_parser.parse(exam_date, dayfirst=True)
        except Exception:
            return f"❌ Não consegui interpretar a data '{exam_date}'. Use o formato DD/MM/AAAA."

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        days_available = (exam_dt - today).days

        if days_available <= 0:
            return "❌ A data da prova já passou ou é hoje. Revise a data informada."

        if not topics:
            return "❌ Nenhum tópico informado para montar o cronograma."

        # Distribui tópicos pelos dias disponíveis
        # Reserva o último dia para revisão geral
        study_days = max(days_available - 1, 1)
        lines = []
        lines.append("📅 CRONOGRAMA DE ESTUDOS")
        lines.append("=" * 40)
        lines.append(f"🎯 Prova: {exam_dt.strftime('%d/%m/%Y')}")
        lines.append(f"📆 Dias disponíveis: {days_available} (incluindo revisão)")
        lines.append(f"⏱ Carga diária: {hours_per_day}h/dia")
        lines.append(f"📚 Tópicos: {len(topics)}")
        lines.append("")

        days_pt = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        # Distribui tópicos
        topics_per_day = max(1, len(topics) // study_days)
        topic_idx = 0
        day_num = 0

        for i in range(study_days):
            current_day = today + timedelta(days=i)
            if current_day.weekday() == 6:  # pula domingo
                continue

            day_name = days_pt[current_day.weekday()]
            date_str = current_day.strftime("%d/%m")
            day_topics = topics[topic_idx: topic_idx + topics_per_day]
            if not day_topics and topic_idx < len(topics):
                day_topics = [topics[topic_idx]]
            topic_idx += len(day_topics)
            day_num += 1

            if day_topics:
                topic_list = " / ".join(day_topics)
                lines.append(f"  Dia {day_num:02d} | {day_name} {date_str} | {topic_list}")
            if topic_idx >= len(topics):
                break

        # Revisão no penúltimo dia
        rev_day = exam_dt - timedelta(days=1)
        if rev_day > today:
            day_name = days_pt[rev_day.weekday()]
            lines.append(f"  Revisão | {day_name} {rev_day.strftime('%d/%m')} | 🔁 Revisão geral de todos os tópicos")

        # Dia da prova
        lines.append(f"  📝 PROVA  | {exam_dt.strftime('%d/%m')} | Boa sorte! 🍀")
        lines.append("")
        lines.append(f"💡 Dica: estude {hours_per_day}h por dia e faça pausas de 15min a cada 45min (técnica Pomodoro).")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Erro ao criar cronograma: {e}"


# ── Tool: listar documentos disponíveis ───────────────────────

def list_available_docs() -> str:
    """Lista todos os documentos disponíveis na base de conhecimento."""
    files = (
        list(KNOWLEDGE_BASE_DIR.glob("**/*.pdf"))
        + list(KNOWLEDGE_BASE_DIR.glob("**/*.txt"))
        + list(KNOWLEDGE_BASE_DIR.glob("**/*.md"))
    )
    if not files:
        return (
            "📂 Nenhum documento encontrado em knowledge_base/.\n"
            "Adicione PDFs ou arquivos .txt e rode: python scripts/index_docs.py"
        )
    lines = [f"📂 Documentos disponíveis ({len(files)}):"]
    for f in files:
        size_kb = f.stat().st_size // 1024
        lines.append(f"  • {f.name}  [{size_kb} KB]")
    return "\n".join(lines)


# ── Tool: dicas de estudo ─────────────────────────────────────

def get_study_tips(topic: str = "") -> str:
    """Retorna dicas de estudo e técnicas de aprendizado."""
    tips = {
        "geral": [
            "🧠 Use a técnica Pomodoro: 25min de foco + 5min de pausa.",
            "✍️ Escreva resumos com suas próprias palavras — isso fixa melhor.",
            "🔄 Revise o conteúdo em intervalos espaçados (1 dia, 1 semana, 1 mês).",
            "❓ Teste seu conhecimento com perguntas antes de reler o material.",
            "😴 Durma bem: a consolidação da memória acontece durante o sono.",
        ],
        "programação": [
            "💻 Pratique código todo dia, mesmo que seja por 20 minutos.",
            "🐛 Não tenha medo de erros — debugar é aprender.",
            "📖 Leia código de outras pessoas para aprender padrões.",
            "🏗 Construa projetos pequenos para fixar conceitos.",
        ],
        "matemática": [
            "📐 Resolva exercícios variados — não apenas releia a teoria.",
            "✏️ Mostre todos os passos na resolução, mesmo os óbvios.",
            "🔢 Verifique se o resultado faz sentido antes de finalizar.",
            "📊 Use exemplos concretos para entender conceitos abstratos.",
        ],
    }

    t = topic.lower()
    if "program" in t or "código" in t or "python" in t or "java" in t:
        selected = tips["programação"]
        header = f"💡 Dicas de estudo para Programação:"
    elif "mat" in t or "cálculo" in t or "álgebra" in t or "equação" in t:
        selected = tips["matemática"]
        header = f"💡 Dicas de estudo para Matemática:"
    else:
        selected = tips["geral"]
        header = "💡 Dicas gerais de estudo:"

    return header + "\n" + "\n".join(f"  {tip}" for tip in selected)


# ── Registro de ferramentas ────────────────────────────────────

TOOLS_REGISTRY = {
    "get_current_date": {
        "fn": get_current_date,
        "description": "Retorna a data e hora atual.",
        "params": [],
    },
    "create_schedule": {
        "fn": create_schedule,
        "description": "Cria cronograma de estudos. Params: topics (lista), exam_date (string), hours_per_day (int).",
        "params": ["topics", "exam_date", "hours_per_day"],
    },
    "list_available_docs": {
        "fn": list_available_docs,
        "description": "Lista os documentos disponíveis na base de conhecimento.",
        "params": [],
    },
    "get_study_tips": {
        "fn": get_study_tips,
        "description": "Retorna dicas de estudo. Param: topic (string, opcional).",
        "params": ["topic"],
    },
}


def call_tool(name: str, params: dict) -> str:
    """Executa uma ferramenta pelo nome com os parâmetros fornecidos."""
    if name not in TOOLS_REGISTRY:
        return f"❌ Ferramenta desconhecida: '{name}'"
    entry = TOOLS_REGISTRY[name]
    try:
        return entry["fn"](**params)
    except TypeError as e:
        return f"❌ Parâmetros inválidos para '{name}': {e}"
    except Exception as e:
        return f"❌ Erro ao executar '{name}': {e}"
