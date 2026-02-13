import pandas as pd
from pathlib import Path
import streamlit as st  # Corrigido o import

# Detecta onde o app está rodando (Nuvem ou PC)
BASE_DIR = Path(__file__).resolve().parent.parent

def load_dados():
    # Lista de nomes possíveis que você mencionou ter na pasta
    arquivos_possiveis = [
        "Dados/base_historica.xlsx",
        "dados/base_historica.xlsx",
        "Dados/historico_ecopad.xlsx",
        "dados/historico_ecopad.xlsx",
        "historico_ecopad.xlsx",
        "base_historica.xlsx"
    ]
    
    caminho_final = None
    
    # O "Detetive": Procura qual desses arquivos realmente existe no seu GitHub
    for nome in arquivos_possiveis:
        teste_path = BASE_DIR / nome
        if teste_path.exists():
            caminho_final = teste_path
            break

    if not caminho_final:
        return None, None, None, None, None

    try:
        # Tenta ler as abas. Se o seu Excel tiver nomes de abas diferentes, 
        # o pandas vai avisar, mas aqui usamos os nomes padrão que definimos.
        produtos = pd.read_excel(caminho_final, sheet_name="produtos")
        vendas = pd.read_excel(caminho_final, sheet_name="vendas")
        estoque = pd.read_excel(caminho_final, sheet_name="estoque")
        custos = pd.read_excel(caminho_final, sheet_name="custos")
        calendario = pd.read_excel(caminho_final, sheet_name="calendario")

        # Padroniza tudo para minúsculo para os gráficos não quebrarem
        for df in [produtos, vendas, estoque, custos, calendario]:
            df.columns = df.columns.str.strip().str.lower()

        return produtos, vendas, estoque, custos, calendario
    except Exception as e:
        print(f"Erro na leitura: {e}")
        return None, None, None, None, None

def salvar_venda_app(nova_venda_df):
    # Salva em um arquivo simples na raiz para evitar erro de permissão de pasta
    vendas_app_file = BASE_DIR / "vendas_cadastradas.xlsx"
    
    if vendas_app_file.exists():
        df_existente = pd.read_excel(vendas_app_file)
        df_final = pd.concat([df_existente, nova_venda_df], ignore_index=True)
    else:
        df_final = nova_venda_df
        
    df_final.to_excel(vendas_app_file, index=False, engine="openpyxl")
    return True

def salvar_estoque(nova_linha):
    # Salva o estoque em um arquivo separado
    estoque_file = BASE_DIR / "estoque_app.xlsx"
    
    nova_df = pd.DataFrame([nova_linha])

    try:
        if estoque_file.exists():
            df_existente = pd.read_excel(estoque_file)
            df_final = pd.concat([df_existente, nova_df], ignore_index=True)
        else:
            df_final = nova_df

        df_final.to_excel(estoque_file, index=False, engine="openpyxl")
        return True
    except Exception as e:
        print(f"Erro ao salvar estoque: {e}")
        return False

