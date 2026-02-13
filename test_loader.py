import pandas as pd
import os

# Define o caminho da pasta de dados
DATA_PATH = "Dados"

def load_data():
    """Carrega as planilhas do Excel para o sistema."""
    try:
        produtos = pd.read_excel(f"{DATA_PATH}/produtos.xlsx")
        vendas = pd.read_excel(f"{DATA_PATH}/vendas.xlsx")
        estoque = pd.read_excel(f"{DATA_PATH}/estoque.xlsx")
        custos = pd.read_excel(f"{DATA_PATH}/custos.xlsx")
        calendario = pd.read_excel(f"{DATA_PATH}/calendario.xlsx")
        
        # Garante que a coluna de data seja lida corretamente
        if 'data' in vendas.columns:
            vendas['data'] = pd.to_datetime(vendas['data'])
            
        return produtos, vendas, estoque, custos, calendario
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def save_data(novo_df, nome_planilha):
    """Salva novos lançamentos no Excel."""
    caminho = f"{DATA_PATH}/{nome_planilha}.xlsx"
    try:
        # Lê o arquivo existente
        df_antigo = pd.read_excel(caminho)
        # Adiciona a nova linha
        df_atualizado = pd.concat([df_antigo, novo_df], ignore_index=True)
        # Salva de volta
        df_atualizado.to_excel(caminho, index=False, engine='openpyxl')
        return True
    except Exception as e:
        print(f"Erro ao salvar: {e}")
        return False


