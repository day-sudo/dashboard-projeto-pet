import pandas as pd
from pathlib import Path

DADOS_PATH = Path("dados")

def load_dados():
    # ==============================
    # BASE HISTÓRICA (Excel principal)
    # ==============================
    base_file = DASOS_PATH / "base_historica.xlsx"

    produtos = pd.read_excel(base_file, sheet_name="produtos")
    vendas_hist = pd.read_excel(base_file, sheet_name="vendas")
    estoque = pd.read_excel(base_file, sheet_name="estoque")
    custos = pd.read_excel(base_file, sheet_name="custos")
    calendario = pd.read_excel(base_file, sheet_name="calendario")

    # ==============================
    # BASE DO APP (cadastros novos)
    # ==============================
    vendas_app_file = DADOS_PATH / "vendas_app.xlsx"

    if vendas_app_file.exists():
        vendas_app = pd.read_excel(vendas_app_file)
        vendas = pd.concat([vendas_hist, vendas_app], ignore_index=True)
    else:
        vendas = vendas_hist

    # ==============================
    # PADRONIZAR COLUNAS
    # ==============================
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()

    # Converter data
    if "dados" in vendas.columns:
        vendas["dados"] = pd.to_datetime(vendas["dados"])

    return produtos, vendas, estoque, custos, calendario


