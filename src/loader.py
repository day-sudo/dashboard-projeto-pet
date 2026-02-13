import pandas as pd
from pathlib import Path

def load_data():

    BASE_DIR = Path(__file__).resolve().parent.parent
    arquivo = BASE_DIR / "data" / "bd_empreendimento.xlsx"
    

    # padronizar colunas
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()

    vendas["data"] = pd.to_datetime(vendas["data"])

    return produtos, vendas, estoque, custos, calendario

