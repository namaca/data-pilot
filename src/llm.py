import json
import os
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from openrouter import OpenRouter

from src.metrics import (
    clientes_unicos,
    pedidos_concluidos,
    receita_por_mes,
    receita_total,
    taxa_cancelamento,
    ticket_medio,
    total_pedidos,
    produtos_vendidos,
)

DEFAULT_MODEL = "~openai/gpt-mini-latest"
MAX_TOOL_ROUNDS = 3

# Any permite encaminhar os objetos de mensagem/tool do SDK sem depender de
# aliases de tipos que não são exportados pelo pacote OpenRouter instalado.
TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "sales_summary",
            "description": "Retorna os principais indicadores consolidados das vendas.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "monthly_revenue",
            "description": "Retorna a receita de pedidos concluídos agrupada por mês.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancellation_rate",
            "description": "Retorna a taxa de cancelamento dos pedidos, em percentual.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(name: str, df: pd.DataFrame) -> dict[str, object]:
    """Executa uma ferramenta e devolve métricas com nomes em português."""
    tools: dict[str, Callable[[], dict[str, object]]] = {
        "sales_summary": lambda: {
            "pedidos_concluidos": len(pedidos_concluidos(df)),
            "receita_total": receita_total(df),
            "total_pedidos": total_pedidos(df),
            "produtos_vendidos": produtos_vendidos(df),
            "clientes_unicos": clientes_unicos(df),
            "ticket_medio": ticket_medio(df),
        },
        "monthly_revenue": lambda: {
            "receita_mensal": receita_por_mes(df).to_dict(orient="records")
        },
        "cancellation_rate": lambda: {
            "taxa_cancelamento": taxa_cancelamento(df)
        },
    }

    tool = tools.get(name)
    return tool() if tool else {"erro": f"Ferramenta desconhecida: {name}"}


def run_agent(client: OpenRouter, question: str, df: pd.DataFrame) -> str:
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "Você é um agente de análise de vendas. Responda em português do Brasil, "
                "sem inventar dados. Use as ferramentas quando precisar de dados; elas são "
                "a única fonte permitida."
            ),
        },
        {"role": "user", "content": question},
    ]

    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.send(
            model=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            return (
                message.content
                if isinstance(message.content, str)
                else "O modelo não retornou uma resposta válida."
            )

        # Preserva a mensagem do assistente (inclusive tool_calls) no histórico.
        messages.append(message.model_dump(exclude_none=True))
        for tool_call in tool_calls:
            try:
                json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                result = {"erro": "Argumentos inválidos para a ferramenta."}
            else:
                result = execute_tool(tool_call.function.name, df)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        result,
                        ensure_ascii=False,
                        default=_json_default,
                    ),
                }
            )

    return "Não foi possível concluir a análise no número permitido de consultas."


def build_data_context(df: pd.DataFrame):
    receita_mes = receita_por_mes(df).to_dict(orient="records")
    return {
        "pedidos_concluidos": len(pedidos_concluidos(df)),
        "receita_total": receita_total(df),
        "total_pedidos": total_pedidos(df),
        "produtos_vendidos": produtos_vendidos(df),
        "clientes_unicos": clientes_unicos(df),
        "ticket_medio": ticket_medio(df),
        "taxa_cancelamento": taxa_cancelamento(df),
        "receita_mensal": receita_mes,
    }
def build_prompt(question: str, data_context: dict[str, object]) -> str:
    data = json.dumps(data_context, ensure_ascii=False, default=_json_default)
    return f"""Você é um assistente de análise de vendas. Responda em português do Brasil, com clareza e sem inventar dados. Use somente as métricas calculadas abaixo. Se os dados não forem suficientes para responder, informe isso.

Pergunta: {question}
Métricas calculadas: {data}"""
def ask_openrouter(question: str, df: pd.DataFrame):
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return "Defina OPENROUTER_API_KEY para conversar com os dados."

    try:
        with OpenRouter(api_key=api_key) as client:
            response = client.chat.send(
                model=os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL),
                messages=[
                    {
                        "role": "user",
                        "content": build_prompt(
                            question,
                            build_data_context(df),
                        ),
                    }
                ],
            )

        content = response.choices[0].message.content
        if isinstance(content, str):
            return content

        return "O modelo não retornou uma resposta válida. Tente novamente."

    except Exception as exc:
        print(exc)
        return "Não foi possível conectar ao OpenRouter. Tente novamente."
def _json_default(value: object):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Unsupported value: {type(value).__name__}")