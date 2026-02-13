import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# CONFIGURAÇÃO
# =========================

st.set_page_config(
    page_title="EcoPad Manager PRO",
    page_icon="🌿",
    layout="wide"
)

ARQUIVO = "historico_ecopad.xlsx"


# =========================
# FUNÇÕES DE DADOS
# =========================

def carregar_dados():
    vendas = pd.read_excel(ARQUIVO, sheet_name="Vendas")
    estoque = pd.read_excel(ARQUIVO, sheet_name="Estoque")
    return vendas, estoque


def salvar_venda(nova_linha):
    vendas, estoque = carregar_dados()

    vendas = pd.concat(
        [vendas, pd.DataFrame([nova_linha])],
        ignore_index=True
    )

    with pd.ExcelWriter(ARQUIVO, engine="openpyxl") as writer:
        vendas.to_excel(writer, sheet_name="Vendas", index=False)
        estoque.to_excel(writer, sheet_name="Estoque", index=False)


def salvar_estoque(nova_linha):
    vendas, estoque = carregar_dados()

    produto = nova_linha["Produto"]
    qtd = nova_linha["Quantidade"]

    if produto in estoque["Produto"].values:
        estoque.loc[estoque["Produto"] == produto,
                     "Quantidade"] += qtd
    else:
        estoque = pd.concat(
            [estoque, pd.DataFrame([nova_linha])],
            ignore_index=True
        )

    with pd.ExcelWriter(ARQUIVO, engine="openpyxl") as writer:
        vendas.to_excel(writer, sheet_name="Vendas", index=False)
        estoque.to_excel(writer, sheet_name="Estoque", index=False)


# =========================
# MENU LATERAL
# =========================

menu = st.sidebar.radio(
    "🌿 EcoPad Manager PRO",
    ["📊 Dashboard",
     "➕ Nova Venda",
     "📦 Estoque",
     "📁 Histórico"]
)

vendas, estoque = carregar_dados()

# =========================
# DASHBOARD
# =========================

if menu == "📊 Dashboard":

    st.title("📊 Painel de Controle")

    total_vendas = vendas["Valor"].sum()
    total_itens = vendas["Quantidade"].sum()
    produtos = vendas["Produto"].nunique()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Receita Total", f"R$ {total_vendas:.2f}")
    col2.metric("📦 Itens Vendidos", total_itens)
    col3.metric("🛍 Produtos", produtos)

    st.divider()

    st.subheader("📈 Vendas por Produto")
    vendas_prod = vendas.groupby("Produto")["Quantidade"].sum()
    st.bar_chart(vendas_prod)

    st.subheader("📦 Estoque Atual")
    st.dataframe(estoque, use_container_width=True)


# =========================
# NOVA VENDA
# =========================

elif menu == "➕ Nova Venda":

    st.title("➕ Registrar Nova Venda")

    with st.form("form_venda"):

        data = st.date_input("Data", datetime.today())

        produto = st.selectbox(
            "Produto",
            estoque["Produto"].tolist()
        )

        quantidade = st.number_input(
            "Quantidade",
            min_value=1,
            step=1
        )

        valor = st.number_input(
            "Valor total (R$)",
            min_value=0.0,
            step=1.0
        )

        salvar = st.form_submit_button("Registrar")

        if salvar:

            nova_venda = {
                "Data": data,
                "Produto": produto,
                "Quantidade": quantidade,
                "Valor": valor
            }

            salvar_venda(nova_venda)

            st.success("Venda registrada com sucesso! 🚀")
            st.rerun()


# =========================
# CONTROLE DE ESTOQUE
# =========================

elif menu == "📦 Estoque":

    st.title("📦 Controle de Estoque")

    with st.form("form_estoque"):

        produto = st.text_input("Produto")

        quantidade = st.number_input(
            "Quantidade a adicionar",
            min_value=1,
            step=1
        )

        salvar = st.form_submit_button("Adicionar ao estoque")

        if salvar and produto:

            nova_linha = {
                "Produto": produto,
                "Quantidade": quantidade
            }

            salvar_estoque(nova_linha)

            st.success("Estoque atualizado! 📦")
            st.rerun()

    st.divider()

    st.subheader("📦 Estoque Atual")
    st.dataframe(estoque, use_container_width=True)


# =========================
# HISTÓRICO
# =========================

elif menu == "📁 Histórico":

    st.title("📁 Histórico Completo")

    st.subheader("🛒 Vendas")
    st.dataframe(vendas, use_container_width=True)

    st.subheader("📦 Estoque")
    st.dataframe(estoque, use_container_width=True)

