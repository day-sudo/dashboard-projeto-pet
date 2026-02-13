import streamlit as st
import pandas as pd
from datetime import datetime
from src.loader import load_dados, salvar_venda_app # Agora usamos o seu loader!

# =========================
# CONFIGURAÇÃO
# =========================
st.set_page_config(
    page_title="EcoPad Manager PRO",
    page_icon="🌿",
    layout="wide"
)

# Carregamento Único
produtos, vendas, estoque, custos, calendario = load_dados()

if produtos is None:
    st.error("❌ Base de dados não encontrada na pasta 'Dados'.")
    st.stop()

# =========================
# MENU LATERAL
# =========================
menu = st.sidebar.radio(
    "🌿 EcoPad Manager PRO",
    ["📊 Dashboard", "➕ Nova Venda", "📦 Estoque", "📁 Histórico"]
)

# =========================
# DASHBOARD
# =========================
if menu == "📊 Dashboard":
    st.title("📊 Painel de Controle")

    # Cálculos usando as colunas padronizadas (minúsculas) do loader
    total_vendas = vendas["valor_total"].sum() if "valor_total" in vendas.columns else 0
    total_itens = vendas["qtd"].sum()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Receita Total", f"R$ {total_vendas:,.2f}")
    col2.metric("📦 Itens Vendidos", total_itens)
    col3.metric("🛍️ Produtos Ativos", len(produtos))

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📈 Vendas por Produto")
        # Gráfico dinâmico
        vendas_prod = vendas.groupby("id_produto")["qtd"].sum()
        st.bar_chart(vendas_prod)
    
    with c2:
        st.subheader("📦 Alerta de Estoque")
        st.dataframe(estoque[estoque["quantidade"] < 5], use_container_width=True)

# =========================
# NOVA VENDA
# =========================
elif menu == "➕ Nova Venda":
    st.title("➕ Registrar Nova Venda")

    with st.form("form_venda", clear_on_submit=True):
        col1, col2 = st.columns(2)
        data = col1.date_input("Data", datetime.today())
        # Busca produtos do dataframe carregado
        produto_nome = col2.selectbox("Produto", produtos["nome_produto"].unique())
        
        col3, col4 = st.columns(2)
        quantidade = col3.number_input("Quantidade", min_value=1, step=1)
        valor_unit = col4.number_input("Valor Unitário (R$)", min_value=0.0)

        if st.form_submit_button("Registrar"):
            # Lógica PRO: Pegar o ID do produto automaticamente
            id_prod = produtos[produtos["nome_produto"] == produto_nome]["id_produto"].values[0]
            
            nova_linha = pd.DataFrame([{
                "data": data,
                "id_produto": id_prod,
                "qtd": quantidade,
                "valor_unit": valor_unit,
                "valor_total": quantidade * valor_unit
            }])
            
            salvar_venda_app(nova_linha)
            st.success("Venda enviada para processamento! 🚀")
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


