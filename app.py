import streamlit as st
import pandas as pd
import plotly.express as px
from src.loader import load_data

st.set_page_config(
    page_title="Dashboard Projeto Pet",
    layout="wide",
    page_icon="📊"
)

st.title("📊 Dashboard - Projeto Pet")

# ==============================
# CARREGAR DADOS
# ==============================

produtos, vendas, estoque, custos, calendario = load_data()

# 🔥 Garantir colunas minúsculas (segurança extra)
for df in [produtos, vendas, estoque, custos, calendario]:
    df.columns = df.columns.str.strip().str.lower()

# 🔥 Criar valor_total corretamente
vendas["valor_total"] = vendas["valor_unit"] * vendas["qtd"]

# ==============================
# FILTRO DE MÊS
# ==============================

st.sidebar.header("Filtros")

vendas = vendas.merge(calendario, on="data", how="left")

meses = vendas["nome_mes"].dropna().unique()
mes_selecionado = st.sidebar.multiselect(
    "Selecione o mês",
    meses,
    default=meses
)

if mes_selecionado:
    vendas_filtradas = vendas[vendas["nome_mes"].isin(mes_selecionado)]
else:
    vendas_filtradas = vendas

# ==============================
# KPIs
# ==============================

receita = vendas_filtradas["valor_total"].sum()
itens_vendidos = vendas_filtradas["qtd"].sum()

# Merge para calcular custo
vendas_custo = vendas_filtradas.merge(
    produtos[["id_produto", "custo_unit"]],
    on="id_produto",
    how="left"
)

custo_total = (vendas_custo["qtd"] * vendas_custo["custo_unit"]).sum()
custos_operacionais = custos["valor"].sum()
lucro = receita - custo_total - custos_operacionais

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Receita Total", f"R$ {receita:,.2f}")
col2.metric("📦 Itens Vendidos", itens_vendidos)
col3.metric("💸 Custos Operacionais", f"R$ {custos_operacionais:,.2f}")
col4.metric("📈 Lucro Estimado", f"R$ {lucro:,.2f}")

st.divider()

# ==============================
# GRÁFICOS
# ==============================

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.subheader("Vendas por Plataforma")
    vendas_plat = (
        vendas_filtradas
        .groupby("plataforma")["valor_total"]
        .sum()
        .reset_index()
    )
    fig1 = px.pie(
        vendas_plat,
        names="plataforma",
        values="valor_total",
        hole=0.4
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.subheader("Evolução de Vendas")
    vendas_dia = (
        vendas_filtradas
        .groupby("data")["valor_total"]
        .sum()
        .reset_index()
    )
    fig2 = px.line(
        vendas_dia,
        x="data",
        y="valor_total",
        markers=True
    )
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==============================
# ESTOQUE
# ==============================

st.subheader("📦 Status do Estoque")

estoque["estoque_atual"] = (
    estoque["estoque_inicial"]
    + estoque["entradas"]
    - estoque["saidas"]
)

estoque["status"] = estoque.apply(
    lambda x: "🚨 Repor"
    if x["estoque_atual"] <= x["ponto_reposicao"]
    else "✅ OK",
    axis=1
)

estoque_view = estoque.merge(
    produtos[["id_produto", "nome_produto"]],
    on="id_produto"
)

st.dataframe(
    estoque_view[
        ["nome_produto", "estoque_atual", "ponto_reposicao", "status"]
    ],
    use_container_width=True
)
