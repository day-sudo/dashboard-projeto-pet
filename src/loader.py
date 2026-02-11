import pandas as pd
from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Caminho do arquivo Excel
DATA_PATH = BASE_DIR / "data" / "bd_empreendimento.xlsx"


def load_data():
    # Ler abas do Excel
    produtos = pd.read_excel(DATA_PATH, sheet_name="Produtos")
    vendas = pd.read_excel(DATA_PATH, sheet_name="Vendas")
    estoque = pd.read_excel(DATA_PATH, sheet_name="Estoque")
    custos = pd.read_excel(DATA_PATH, sheet_name="Custos")
    calendario = pd.read_excel(DATA_PATH, sheet_name="Calendario")

    # Converter colunas de data
    vendas["data"] = pd.to_datetime(vendas["data"])
    custos["data"] = pd.to_datetime(custos["data"])

    # Criar valor total da venda
    vendas["Valor_Total"] = vendas["qtd"] * vendas["valor_unit"]

    return produtos, vendas, estoque, custos, calendario

