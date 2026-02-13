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
# FUNÇÃO DE "IA" LÓGICA (SIMULAÇÃO DE ANÁLISE)
# ==============================
def gerar_insights_ia(df_vendas, df_estoque, lucro_atual):
    insights = []
    
    # 1. Análise de Canal
    if not df_vendas.empty:
        top_canal = df_vendas.groupby("plataforma")["valor_total"].sum().idxmax()
        insights.append(f"📢 **Canal Forte:** A {top_canal} é sua maior fonte de renda hoje. Foque anúncios lá.")
    
    # 2. Análise de Estoque Crítico
    estoque_critico = df_estoque[df_estoque["status"] == "BAIXO"]
    if not estoque_critico.empty:
        prod_critico = estoque_critico.iloc[0]["nome_produto"] # Pega o primeiro da lista (ajuste feito aqui)
        insights.append(f"🚨 **Risco:** O produto *{prod_critico}* está crítico. Reponha urgente para não pausar anúncios.")
    
    # 3. Análise Financeira
    if lucro_atual < 0:
        insights.append("📉 **Atenção Financeira:** Estamos operando no negativo (Investimento). Monitore o CAC (Custo de Aquisição).")
    else:
        insights.append("🚀 **Saúde Financeira:** Parabéns! A operação está lucrativa.")

    return insights

# ==============================
# CARREGAR DADOS
# ==============================
try:
    produtos, vendas, estoque, custos, calendario = load_data()
    
    # Limpeza básica
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()
        
    vendas["valor_total"] = vendas["valor_unit"] * vendas["qtd"]

except Exception as e:
    st.error(f"Erro no carregamento: {e}")
    st.stop()

# ==============================
# BARRA LATERAL (O COCKPIT)
# ==============================

with st.sidebar:
    # 1. Branding
    st.title("🌿 EcoPad Manager")
    st.markdown("*Gestão Estratégica & Sustentável*")
    st.divider()

    # 2. Filtros Inteligentes (Expansíveis)
    with st.expander("🔍 Filtros Operacionais", expanded=True):
        # Merge datas
        vendas = vendas.merge(calendario, on="data", how="left")
        meses = vendas["nome_mes"].dropna().unique()
        
        mes_selecionado = st.multiselect(
            "Período (Mês):",
            options=meses,
            default=meses
        )
        
        plataformas = vendas["plataforma"].unique()
        canal_selecionado = st.multiselect(
            "Canal de Venda:",
            options=plataformas,
            default=plataformas
        )

    # Aplicar Filtros
    vendas_filtradas = vendas[vendas["nome_mes"].isin(mes_selecionado)]
    if canal_selecionado:
        vendas_filtradas = vendas_filtradas[vendas_filtradas["plataforma"].isin(canal_selecionado)]

    st.divider()

    # 3. Área de Inteligência (IA)
    st.subheader("🤖 Assistente Virtual")
    
    if st.button("Gerar Análise Estratégica"):
        with st.spinner("Analisando dados..."):
            time.sleep(1.5) # Efeito visual de "pensando"
            
            # Recalcula lucro rápido para a IA
            rec_ia = vendas_filtradas["valor_total"].sum()
            cust_prod_ia = (vendas_filtradas["qtd"] * 10).sum() # Simplificado para exemplo
            lucro_ia = rec_ia - custos["valor"].sum() - cust_prod_ia
            
            # Recalcula estoque para IA
            estoque["estoque_atual"] = estoque["estoque_inicial"] + estoque["entradas"] - estoque["saidas"]
            estoque["status"] = estoque.apply(lambda x: "BAIXO" if x["estoque_atual"] <= x["ponto_reposicao"] else "OK", axis=1)
            
            dicas = gerar_insights_ia(vendas_filtradas, estoque, lucro_ia)
            
            for dica in dicas:
                st.info(dica)

    st.divider()

    # 4. Alertas Rápidos (Sempre visíveis)
    st.subheader("🔔 Alertas")
    # Checar estoque baixo
    estoque_real = estoque.copy()
    estoque_real["atual"] = estoque_real["estoque_inicial"] + estoque_real["entradas"] - estoque_real["saidas"]
    criticos = estoque_real[estoque_real["atual"] <= estoque_real["ponto_reposicao"]]
    
    if not criticos.empty:
        st.error(f"{len(criticos)} Itens precisam de reposição!")
        st.markdown(f"**Item crítico:** {criticos.iloc[0]['nome_produto']}") # Correção aplicada aqui
    else:
        st.success("Estoque Saudável ✅")

# ==============================
# ÁREA PRINCIPAL (DASHBOARD)
# ==============================

st.title("📊 Visão Geral da Operação")

# KPIs
receita = vendas_filtradas["valor_total"].sum()
itens = vendas_filtradas["qtd"].sum()
custo_fixo = custos["valor"].sum()

# Custo Variável (Produto)
vendas_full = vendas_filtradas.merge(produtos, on="id_produto", how="left")
custo_var = (vendas_full["qtd"] * vendas_full["custo_unit"]).sum()

lucro = receita - cost_fixo - custo_var if 'custo_var' in locals() else receita - custo_fixo # Fallback simples

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento", f"R$ {receita:,.2f}")
col2.metric("Vendas (Qtd)", itens)
col3.metric("Custos Fixos", f"R$ {custo_fixo:,.2f}")
col4.metric("Resultado", f"R$ {lucro:,.2f}", delta_color="normal")

# Gráficos
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("### 🛒 Performance por Canal")
    if not vendas_filtradas.empty:
        fig1 = px.pie(vendas_filtradas, names="plataforma", values="valor_total", hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

with col_g2:
    st.markdown("### 📈 Curva de Crescimento")
    if not vendas_filtradas.empty:
        vendas_dia = vendas_filtradas.groupby("data")["valor_total"].sum().reset_index()
        fig2 = px.area(vendas_dia, x="data", y="valor_total", color_discrete_sequence=['#4CAF50'])
        st.plotly_chart(fig2, use_container_width=True)

# Tabela de Estoque
st.markdown("### 📦 Controle de Estoque")
# Recalculo para exibição principal
estoque_view = estoque_real.merge(produtos[["id_produto", "nome_produto"]], on="id_produto")
estoque_view["status_visual"] = estoque_view.apply(lambda x: "🔴 COMPRAR" if x["atual"] <= x["ponto_reposicao"] else "🟢 OK", axis=1)

st.dataframe(
    estoque_view[["nome_produto", "atual", "ponto_reposicao", "status_visual"]],
    use_container_width=True,
    hide_index=True
)
