from pathlib import Path
import pandas as pd


def pedidos_concluidos(dados: pd.DataFrame) -> pd.DataFrame:
    """Retorna as linhas de pedidos concluídos."""
    return dados.loc[dados["status"] == "concluido"].copy()


def receita_total(dados: pd.DataFrame) -> float:
    """Soma a receita das linhas de pedidos concluídos."""
    return float(pedidos_concluidos(dados)["receita"].sum())


def total_pedidos(dados: pd.DataFrame) -> int:
    """Conta pedidos concluídos distintos."""
    return int(pedidos_concluidos(dados)["pedido_id"].nunique())


def produtos_vendidos(dados: pd.DataFrame) -> int:
    """Soma unidades vendidas em pedidos concluídos."""
    return int(pedidos_concluidos(dados)["quantidade"].sum())


def clientes_unicos(dados: pd.DataFrame) -> int:
    """Conta clientes distintos com pedidos concluídos."""
    return int(pedidos_concluidos(dados)["cliente_id"].nunique())


def ticket_medio(dados: pd.DataFrame) -> float:
    """Receita concluída dividida pela quantidade de pedidos concluídos."""
    pedidos = total_pedidos(dados)
    return receita_total(dados) / pedidos if pedidos else 0.0


def taxa_cancelamento(dados: pd.DataFrame) -> float:
    """Percentual de pedidos cancelados entre todos os pedidos distintos."""
    total = dados["pedido_id"].nunique()
    cancelados = dados.loc[dados["status"] == "cancelado", "pedido_id"].nunique()
    return (cancelados / total * 100) if total else 0.0


def receita_por_mes(dados: pd.DataFrame) -> pd.DataFrame:
    """Agrega receita concluída por mês, em ordem cronológica."""
    return (pedidos_concluidos(dados).groupby("mes", as_index=False)["receita"]
            .sum().sort_values("mes"))