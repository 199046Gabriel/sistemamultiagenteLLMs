# mcp_server/client.py — Cliente MCP para os agentes
#
# Permite que os agentes chamem as tools via MCP de forma padronizada,
# seja localmente (chamada direta) ou via protocolo MCP completo.

from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.academic_tools import call_tool, TOOLS_REGISTRY


class MCPClient:
    """
    Cliente MCP simples para integração local.
    Em produção, pode ser substituído por um cliente HTTP/SSE para
    comunicação com o servidor MCP remoto.
    """

    def __init__(self, mode: str = "local"):
        """
        Args:
            mode: "local" para chamada direta às tools,
                  "remote" para comunicação via servidor MCP (futuro).
        """
        self.mode = mode

    def list_tools(self) -> list[dict]:
        """Lista as tools disponíveis no servidor MCP."""
        return [
            {
                "name": name,
                "description": entry["description"],
                "params": entry["params"],
            }
            for name, entry in TOOLS_REGISTRY.items()
        ]

    def call(self, tool_name: str, params: dict) -> str:
        """
        Chama uma tool pelo nome com os parâmetros fornecidos.

        Args:
            tool_name: nome da ferramenta registrada
            params: dicionário de parâmetros

        Returns:
            Resultado da execução como string.
        """
        if self.mode == "local":
            return call_tool(tool_name, params)
        else:
            raise NotImplementedError(
                "Modo remoto não implementado nesta versão. Use mode='local'."
            )

    def describe(self) -> str:
        """Retorna descrição formatada das tools disponíveis."""
        tools = self.list_tools()
        lines = [f"🔧 Tools MCP disponíveis ({len(tools)}):"]
        for t in tools:
            params_str = ", ".join(t["params"]) if t["params"] else "nenhum"
            lines.append(f"  • {t['name']}: {t['description']}")
            lines.append(f"    Parâmetros: {params_str}")
        return "\n".join(lines)
