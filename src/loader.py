import pandas as pd
from pathlib import Path

def load_data():

    BASE_DIR = Path(__file__).resolve().parent.parent
    data_path = BASE_DIR / "data"

    produtos = pd.read_excel(data_path / "produtos.xlsx")
    vendas = pd.read_excel(data_path / "vendas.xlsx")
    estoque = pd.read_excel(data_path / "estoque.xlsx")
    custos = pd.read_excel(data_path / "custos.xlsx")
    calendario = pd.read_excel(data_path / "calendario.xlsx")

    # padronizar colunas
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()

    vendas["data"] = pd.to_datetime(vendas["data"])

    return produtos, vendas, estoque, custos, calendario

