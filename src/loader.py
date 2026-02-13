import pandas as pd
from pathlib import Path
import os

# Caminho robusto para funcionar na nuvem e local
BASE_DIR = Path(__file__).parent.parent
DADOS_PATH = BASE_DIR / "Dados"

def load_dados():
    # ==============================
    # BASE HISTÓRICA
    # ==============================
    base_file = DADOS_PATH / "base_historica.xlsx"
    
    # Se o arquivo não existir, criamos um erro amigável
    if not base_file.exists():
        return None, None, None, None, None

    produtos = pd.read_excel(base_file, sheet_name="produtos")
    vendas_hist = pd.read_excel(base_file, sheet_name="vendas")
    estoque = pd.read_excel(base_file, sheet_name="estoque")
    custos = pd.read_excel(base_file, sheet_name="custos")
    calendario = pd.read_excel(base_file, sheet_name="calendario")

    # ==============================
    # BASE DO APP (Integração de novos lançamentos)
    # ==============================
    vendas_app_file = DADOS_PATH / "vendas_app.xlsx"

    if vendas_app_file.exists():
        vendas_app = pd.read_excel(vendas_app_file)
        vendas = pd.concat([vendas_hist, vendas_app], ignore_index=True)
    else:
        vendas = vendas_hist

    # Padronizar colunas
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()

    # Converter data - Verificando se a coluna existe
    if "data" in vendas.columns:
        vendas["data"] = pd.to_datetime(vendas["data"])

    return produtos, vendas, estoque, custos, calendario

def salvar_venda_app(nova_venda_df):
    """Salva apenas no arquivo incremental para não corromper a base histórica"""
    vendas_app_file = DADOS_PATH / "vendas_app.xlsx"
    
    if vendas_app_file.exists():
        df_existente = pd.read_excel(vendas_app_file)
        df_final = pd.concat([df_existente, nova_venda_df], ignore_index=True)
    else:
        df_final = nova_venda_df
        
    df_final.to_excel(vendas_app_file, index=False, engine="openpyxl")


