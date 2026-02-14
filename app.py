import streamlit as st

# ==============================
# CONFIGURAÇÃO INICIAL (OBRIGATORIAMENTE PRIMEIRO)
# ==============================
st.set_page_config(
    page_title="Gerenciador EcoPad",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
from src.loader import load_data
import time
st.sidebar.image("logo_ecopad.png", width=100)
st.sidebar.title("EcoPad Manager")


# ==============================
# FUNÇÃO DE INSIGHTS
# ==============================
def gerar_insights_ia(df_vendas, df_estoque, lucro_atual):
    insights = []

    if not df_vendas.empty:
        top_canal = df_vendas.groupby("plataforma")["valor_total"].sum().idxmax()
        insights.append(f"📢 Canal forte: {top_canal}")

    estoque_critico = df_estoque[df_estoque["status"] == "BAIXO"]
    if not estoque_critico.empty:
        prod_critico = estoque_critico.iloc[0]["nome_produto"]
        insights.append(f"🚨 Estoque baixo: {prod_critico}")

    if lucro_atual < 0:
        insights.append("📉 Operação com prejuízo.")
    else:
        insights.append("🚀 Operação lucrativa.")

    return insights

# ==============================
# CARREGAR DADOS
# ==============================
try:
    produtos, vendas, estoque, custos, calendario = load_data()

    # Padronizar colunas
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()

    # Converter datas
    vendas["data"] = pd.to_datetime(vendas["data"], errors="coerce")
    calendario["data"] = pd.to_datetime(calendario["data"], errors="coerce")

    # Criar valor total
    vendas["valor_total"] = vendas["valor_unit"] * vendas["qtd"]

except Exception as e:
    st.error(f"Erro no carregamento dos dados: {e}")
    st.stop()

# ==============================
# SIDEBAR
# ==============================
with st.sidebar:

    st.title("🌿 Gestão Estratégica")
    st.divider()

    # Merge com calendário
    vendas = vendas.merge(calendario, on="data", how="left")

    meses = vendas["nome_mes"].dropna().unique()
    plataformas = vendas["plataforma"].dropna().unique()

    mes_sel = st.multiselect("Período (Mês)", meses, default=meses)
    canal_sel = st.multiselect("Canal", plataformas, default=plataformas)

    vendas_filtradas = vendas.copy()

    if mes_sel:
        vendas_filtradas = vendas_filtradas[
            vendas_filtradas["nome_mes"].isin(mes_sel)
        ]

    if canal_sel:
        vendas_filtradas = vendas_filtradas[
            vendas_filtradas["plataforma"].isin(canal_sel)
        ]

    # Assistente IA
    st.divider()
    st.subheader("🤖 Assistente")

    if st.button("Gerar análise"):

        with st.spinner("Analisando..."):

            receita_ia = vendas_filtradas["valor_total"].sum()
            custo_fixo_ia = custos["valor"].sum()

            v_full = vendas_filtradas.merge(produtos, on="id_produto", how="left")

            custo_var_ia = (
                v_full["qtd"] * v_full["custo_unit"].fillna(0)
            ).sum()

            lucro_ia = receita_ia - custo_fixo_ia - custo_var_ia

            estoque["atual"] = (
                estoque["estoque_inicial"]
                + estoque["entradas"]
                - estoque["saidas"]
            )

            estoque["status"] = estoque.apply(
                lambda x: "BAIXO"
                if x["atual"] <= x["ponto_reposicao"]
                else "OK",
                axis=1,
            )

            estoque_ia = estoque.merge(
                produtos[["id_produto", "nome_produto"]],
                on="id_produto"
            )

            dicas = gerar_insights_ia(
                vendas_filtradas,
                estoque_ia,
                lucro_ia
            )

            for d in dicas:
                st.info(d)

# ==============================
# DASHBOARD PRINCIPAL
# ==============================
st.title("📈 Visão Geral da Operação")

receita = vendas_filtradas["valor_total"].sum()
itens = vendas_filtradas["qtd"].sum()
custo_fixo = custos["valor"].sum()

vendas_full = vendas_filtradas.merge(
    produtos,
    on="id_produto",
    how="left"
)

custo_var = (
    vendas_full["qtd"] * vendas_full["custo_unit"].fillna(0)
).sum()

lucro = receita - custo_fixo - custo_var

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric("Faturamento", f"R$ {receita:,.2f}")
col2.metric("Itens vendidos", itens)
col3.metric("Custos fixos", f"R$ {custo_fixo:,.2f}")
col4.metric("Resultado", f"R$ {lucro:,.2f}")

st.divider()

# ==============================
# GRÁFICOS
# ==============================
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("🛒 Vendas por canal")

    if not vendas_filtradas.empty:
        fig1 = px.pie(
            vendas_filtradas,
            names="plataforma",
            values="valor_total",
            hole=0.5
        )
        st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.subheader("👩🏻‍💻 Evolução das vendas")

    if not vendas_filtradas.empty:
        vendas_dia = (
            vendas_filtradas
            .groupby("data")["valor_total"]
            .sum()
            .reset_index()
        )

        fig2 = px.area(
            vendas_dia,
            x="data",
            y="valor_total"
        )

        st.plotly_chart(fig2, use_container_width=True)

# ==============================
# ESTOQUE
# ==============================
st.subheader("📦 Controle de Estoque")

estoque_view = estoque.merge(
    produtos[["id_produto", "nome_produto"]],
    on="id_produto"
)

estoque_view["atual"] = (
    estoque_view["estoque_inicial"]
    + estoque_view["entradas"]
    - estoque_view["saidas"]
)

estoque_view["status"] = estoque_view.apply(
    lambda x: "🔴 COMPRAR"
    if x["atual"] <= x["ponto_reposicao"]
    else "🟢 OK",
    axis=1
)

st.dataframe(
    estoque_view[
        ["nome_produto", "atual", "ponto_reposicao", "status"]
    ],
    use_container_width=True,
    hide_index=True
)

