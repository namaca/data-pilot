from pathlib import Path
import pandas as pd

ARQUIVO_ORIGEM = Path("data/sales.csv")


df = pd.read_csv(ARQUIVO_ORIGEM)
print(f"Extração concluída: {len(df)} registros e {len(df.columns)} colunas")


df = df.drop_duplicates().copy()

colunas_texto = ["pedido_id", "produto", "categoria", "cliente_id", "cidade", "canal", "status"]
for coluna in colunas_texto:
    df[coluna] = df[coluna].astype("string").str.strip()
    df[coluna] = df[coluna].replace("", pd.NA)

# Tipos apropriados antes de aplicar as regras de qualidade.
df["data"] = pd.to_datetime(df["data"], errors="coerce")
df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
df["preco_unitario"] = pd.to_numeric(df["preco_unitario"], errors="coerce")

linhas_antes = len(df)
df = df.dropna(subset=["pedido_id", "data", "quantidade", "preco_unitario"])
df = df[(df["quantidade"] > 0) & (df["preco_unitario"] > 0)].copy()
linhas_removidas = linhas_antes - len(df)

colunas_descritivas = ["produto", "categoria", "cliente_id", "cidade", "canal", "status"]
df[colunas_descritivas] = df[colunas_descritivas].fillna("Não informado")

print(f"Registros removidos por campos essenciais ausentes/inválidos ou valores não positivos: {linhas_removidas}")
print("Ausentes restantes:")


df["status"] = df["status"].str.casefold().replace({
    "concluído": "concluido",
    "concluido": "concluido",
    "cancelado": "cancelado",
})

# Mantém rótulos desconhecidos visíveis; não os classifica silenciosamente como concluídos/cancelados.
df["mes"] = df["data"].dt.to_period("M").astype("string")
df["receita"] = df["quantidade"] * df["preco_unitario"]



PASTA_SAIDA = Path("data_processed")
PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
ARQUIVO_TRATADO = PASTA_SAIDA / "sales_clean.csv"
df.to_csv(ARQUIVO_TRATADO, index=False, sep=";", decimal=",", date_format="%Y-%m-%d")
print(f"Carga concluída: {ARQUIVO_TRATADO} ({len(df)} registros)")