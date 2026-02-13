import pandas as pd
import os

# Caminho base para garantir que o Streamlit encontre a pasta
DATA_PATH = "Dados"

def load_data():
    """
    Carrega todas as tabelas necessárias para o Dashboard.
    Retorna: produtos, vendas, estoque, custos, calendario
    """
    try:
        # Carregando as planilhas (ajuste os nomes se necessário)
        produtos = pd.read_excel(f"{DATA_PATH}/produtos.xlsx")
        vendas = pd.read_excel(f"{DATA_PATH}/vendas.xlsx")
        estoque = pd.read_excel(f"{DATA_PATH}/estoque.xlsx")
        custos = pd.read_excel(f"{DATA_PATH}/custos.xlsx")
        calendario = pd.read_excel(f"{DATA_PATH}/calendario.xlsx") # ou criar via código se preferir
        
        # Garantia de tipos
        if 'data' in vendas.columns:
            vendas['data'] = pd.to_datetime(vendas['data'])
            
        return produtos, vendas, estoque, custos, calendario
    
    except FileNotFoundError as e:
        # Erro amigável se o arquivo não for encontrado
        print(f"Erro Crítico: Arquivo não encontrado - {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def save_data(novo_dado, nome_arquivo):
    """
    Função para salvar novos lançamentos no Excel.
    - novo_dado: DataFrame com a linha a ser adicionada
    - nome_arquivo: nome do arquivo sem a extensão (ex: 'vendas')
    """
    caminho_completo = f"{DATA_PATH}/{nome_arquivo}.xlsx"
    
    try:
        # 1. Tenta carregar o arquivo existente
        df_atual = pd.read_excel(caminho_completo)
        
        # 2. Concatena (junta) o dado antigo com o novo
        df_atualizado = pd.concat([df_atual, novo_dado], ignore_index=True)
        
        # 3. Salva mantendo o formato Excel
        # engine='openpyxl' é essencial para não corromper o arquivo
        df_atualizado.to_excel(caminho_completo, index=False, engine='openpyxl')
        
        return True # Retorna Sucesso
        
    except Exception as e:
        print(f"❌ Erro ao salvar dados: {e}")
        return False # Retorna Falha


