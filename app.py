import streamlit as st
import pandas as pd
import plotly.express as px
from src.loader import load_data
import time

# ==============================
# CONFIGURAÇÃO INICIAL
# ==============================
st.set_page_config(
    page_title="EcoPad Manager",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# ==============================
# FUNÇÃO DE "IA" LÓGICA
# ==============================
def gerar_insights_ia(df_vendas, df_estoque, lucro_atual):
    insights = []
    if not df_vendas.empty:
        top_canal = df_vendas.groupby("plataforma")["valor_total"].sum().idxmax()
        insights.append(f"📢 **Canal Forte:** A {top_canal} é sua maior fonte de renda.")
    
    estoque_critico = df_estoque[df_estoque["status"] == "BAIXO"]
    if not estoque_critico.empty:
        prod_critico = estoque_critico.iloc[0]["nome_produto"]
        insights.append(f"🚨 **Risco:** O produto *{prod_critico}* está com estoque baixo.")
    
    if lucro_atual < 0:
        insights.append("📉 **Atenção:** A operação está em fase de investimento (lucro negativo).")
    else:
        insights.append("🚀 **Saúde Financeira:** Operação lucrativa!")
    return insights

# ==============================
# CARREGAR DADOS
# ==============================
try:
    produtos, vendas, estoque, custos, calendario = load_data()
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()
    vendas["valor_total"] = vendas["valor_unit"] * vendas["qtd"]
except Exception as e:
    st.error(f"Erro no carregamento: {e}")
    st.stop()

# ==============================
# BARRA LATERAL (COCKPIT)
# ==============================
with st.sidebar:
    st.title("🌿 Gerenciador EcoPad")
    st.markdown("*Gestão Estratégica & Sustentável*")
    st.divider()

    with st.expander("🔍 Filtros Operacionais", expanded=True):
        vendas = vendas.merge(calendario, on="data", how="left")
        meses = vendas["nome_mes"].dropna().unique()
        mes_selecionado = st.multiselect("Período (Mês):", options=meses, default=meses)
        
        plataformas = vendas["plataforma"].unique()
        canal_selecionado = st.multiselect("Canal de Venda:", options=plataformas, default=plataformas)

    vendas_filtradas = vendas[vendas["nome_mes"].isin(mes_selecionado)]
    if canal_selecionado:
        vendas_filtradas = vendas_filtradas[vendas_filtradas["plataforma"].isin(canal_selecionado)]

    st.divider()
    st.subheader("🤖 Assistente Virtual")
    if st.button("Gerar Análise Estratégica"):
        with st.spinner("Analisando..."):
            time.sleep(1)
            # Recálculo rápido para a IA
            rec_ia = vendas_filtradas["valor_total"].sum()
            cust_fixo_ia = custos["valor"].sum()
            v_full_ia = vendas_filtradas.merge(produtos, on="id_produto", how="left")
            c_var_ia = (v_full_ia["qtd"] * v_full_ia["custo_unit"].fillna(0)).sum()
            lucro_ia = rec_ia - cust_fixo_ia - c_var_ia
            
            # Recálculo estoque para IA
            estoque["atual"] = estoque["estoque_inicial"] + estoque["entradas"] - estoque["saidas"]
            estoque["status"] = estoque.apply(lambda x: "BAIXO" if x["atual"] <= x["ponto_reposicao"] else "OK", axis=1)
            estoque_ia = estoque.merge(produtos[["id_produto", "nome_produto"]], on="id_produto")
            
            dicas = gerar_insights_ia(vendas_filtradas, estoque_ia, lucro_ia)
            for dica in dicas:
                st.info(dica)

    st.divider()
    st.subheader("🔔 Alertas")
    estoque["atual_alert"] = estoque["estoque_inicial"] + estoque["entradas"] - estoque["saidas"]
    criticos = estoque[estoque["atual_alert"] <= estoque["ponto_reposicao"]]
    if not criticos.empty:
        st.error(f"Reponha {len(criticos)} itens!")
    else:
        st.success("Estoque OK ✅")

# ==============================
# ÁREA PRINCIPAL (DASHBOARD)
# ==============================
st.title("📊 Visão Geral da Operação")

receita = vendas_filtradas["valor_total"].sum()
itens = vendas_filtradas["qtd"].sum()
custo_fixo = custos["valor"].sum()

vendas_full = vendas_filtradas.merge(produtos, on="id_produto", how="left")
custo_var = (vendas_full["qtd"] * vendas_full["custo_unit"].fillna(0)).sum()

# CORREÇÃO AQUI: Usando a variável correta 'custo_fixo'
lucro = receita - custo_fixo - custo_var

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento", f"R$ {receita:,.2f}")
col2.metric("Vendas (Qtd)", itens)
col3.metric("Custos Fixos", f"R$ {custo_fixo:,.2f}")
col4.metric("Resultado", f"R$ {lucro:,.2f}")

st.divider()

col_g1, col_g2 = st.columns(2)
with col_g1:
    st.markdown("### 🛒 Performance por Canal")
    if not vendas_filtradas.empty:
        fig1 = px.pie(vendas_filtradas, names="plataforma", values="valor_total", hole=0.6)
        st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.markdown("### 📈 Tendência de Faturamento")
    if not vendas_filtradas.empty:
        vendas_dia = vendas_filtradas.groupby("data")["valor_total"].sum().reset_index()
        fig2 = px.area(vendas_dia, x="data", y="valor_total", color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("### 📦 Controle de Estoque")
estoque_view = estoque.merge(produtos[["id_produto", "nome_produto"]], on="id_produto")
estoque_view["atual"] = estoque_view["estoque_inicial"] + estoque_view["entradas"] - estoque_view["saidas"]
estoque_view["status_visual"] = estoque_view.apply(lambda x: "🔴 COMPRAR" if x["atual"] <= x["ponto_reposicao"] else "🟢 OK", axis=1)

st.dataframe(
    estoque_view[["nome_produto", "atual", "ponto_reposicao", "status_visual"]],
    use_container_width=True,
    hide_index=True
)
