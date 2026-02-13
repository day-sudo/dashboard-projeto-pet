import streamlit as st
import pandas as pd
import plotly.express as px
from src.loader import load_data, save_data # Certifique-se que save_data está no loader
import time

# ==============================
# CONFIGURAÇÃO PRO & CSS
# ==============================
st.set_page_config(
    page_title="EcoPad Manager PRO",
    layout="wide",
    page_icon="🌿",
    initial_sidebar_state="expanded"
)

# CSS para visual limpo e profissional
st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 1rem;}
        h1 {margin-top: -50px;}
        .stMetric {background-color: #0E1117; padding: 10px; border-radius: 5px;}
        /* Esconde menus padrões do Streamlit para parecer App Nativo */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================
# CARGA DE DADOS
# ==============================
try:
    # Força recarga dos dados para garantir atualização pós-lançamento
    produtos, vendas, estoque, custos, calendario = load_data()
    
    # Padronização
    for df in [produtos, vendas, estoque, custos, calendario]:
        df.columns = df.columns.str.strip().str.lower()
    vendas["valor_total"] = vendas["valor_unit"] * vendas["qtd"]

except Exception as e:
    st.error(f"Erro crítico no sistema: {e}")
    st.stop()

# ==============================
# NAVEGAÇÃO PRINCIPAL (SIDEBAR)
# ==============================
with st.sidebar:
    st.title("🌿 EcoPad PRO")
    st.write("---")
    
    # O "Menu" que troca as telas
    pagina = st.radio(
        "Navegação:", 
        ["📊 Dashboard Gerencial", "📝 Novo Lançamento"],
        index=0
    )
    
    st.write("---")
    
    # IA só aparece no Dashboard para não distrair no cadastro
    if pagina == "📊 Dashboard Gerencial":
        st.subheader("🤖 Eco-Inteligência")
        if st.button("Analisar Operação", type="primary"):
            with st.spinner("Processando Big Data..."):
                time.sleep(1)
                # Lógica IA
                rec = vendas["valor_total"].sum()
                meta = 1000 # Exemplo de meta
                if rec >= meta:
                    st.success("🚀 Meta Batida! O faturamento está saudável.")
                else:
                    st.warning(f"📉 Faltam R$ {meta - rec:.2f} para a meta.")
                
                # Alerta Estoque
                estoque["atual"] = estoque["estoque_inicial"] + estoque["entradas"] - estoque["saidas"]
                critico = estoque[estoque["atual"] <= estoque["ponto_reposicao"]]
                if not critico.empty:
                    st.error(f"⚠️ Atenção: {len(critico)} produtos com estoque baixo.")

# ==============================
# TELA 1: DASHBOARD (VISUALIZAÇÃO)
# ==============================
if pagina == "📊 Dashboard Gerencial":
    st.title("📈 Visão Estratégica")
    
    # Filtros Discretos (Expander fechado por padrão para limpeza)
    with st.expander("🔎 Filtros Avançados", expanded=False):
        col_fil1, col_fil2 = st.columns(2)
        vendas = vendas.merge(calendario, on="data", how="left")
        meses = vendas["nome_mes"].dropna().unique()
        sel_mes = col_fil1.multiselect("Mês", meses, default=meses)
        sel_canal = col_fil2.multiselect("Canal", vendas["plataforma"].unique(), default=vendas["plataforma"].unique())

    # Aplica Filtros
    df_view = vendas[vendas["nome_mes"].isin(sel_mes)]
    if sel_canal:
        df_view = df_view[df_view["plataforma"].isin(sel_canal)]

    # KPIs
    receita = df_view["valor_total"].sum()
    itens = df_view["qtd"].sum()
    lucro_aprox = receita * 0.40 # Exemplo simplificado de margem 40%
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Faturamento Total", f"R$ {receita:,.2f}", delta="Vs. Mês Anterior")
    c2.metric("Itens Vendidos", itens)
    c3.metric("Lucro Estimado", f"R$ {lucro_aprox:,.2f}")
    c4.metric("Ticket Médio", f"R$ {(receita/itens if itens > 0 else 0):,.2f}")

    st.markdown("---")

    # Gráficos (Clean Design)
    g1, g2 = st.columns(2)
    with g1:
        st.subheader("Vendas por Canal")
        fig1 = px.pie(df_view, names="plataforma", values="valor_total", hole=0.6, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig1.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig1, use_container_width=True)
    
    with g2:
        st.subheader("Evolução Diária")
        diario = df_view.groupby("data")["valor_total"].sum().reset_index()
        fig2 = px.line(diario, x="data", y="valor_total", markers=True, line_shape="spline")
        fig2.update_traces(line_color="#4CAF50") # Verde Eco
        fig2.update_layout(height=300, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig2, use_container_width=True)

# ==============================
# TELA 2: CADASTRO (OPERAÇÃO)
# ==============================
elif pagina == "📝 Novo Lançamento":
    st.title("📝 Central de Lançamentos")
    st.markdown("Insira os dados da venda. O sistema atualizará o Excel e os gráficos automaticamente.")
    
    with st.form("form_venda_pro", clear_on_submit=True):
        col_in1, col_in2 = st.columns(2)
        
        # Inputs
        data_in = col_in1.date_input("Data da Venda")
        canal_in = col_in2.selectbox("Canal de Venda", ["Shopee", "Mercado Livre", "WhatsApp", "Feira"])
        
        st.write("---")
        
        col_in3, col_in4 = st.columns(2)
        # Pega lista de produtos atualizada
        lista_prods = produtos["nome_produto"].unique()
        prod_in = col_in3.selectbox("Produto Vendido", lista_prods)
        qtd_in = col_in4.number_input("Quantidade", min_value=1, value=1)
        
        # Botão de Ação
        submitted = st.form_submit_button("💾 REGISTRAR VENDA", type="primary")
        
        if submitted:
            try:
                # 1. Recupera ID e Preço do Produto
                prod_info = produtos[produtos["nome_produto"] == prod_in].iloc[0]
                id_p = prod_info["id_produto"]
                preco_unit = prod_info["preco_venda"] # Assume que existe coluna preco_venda, senao usar valor manual
                
                # 2. Cria o DataFrame da nova linha
                # IMPORTANTE: As colunas devem bater com seu Excel 'Vendas.xlsx'
                novo_df = pd.DataFrame([{
                    "data": data_in,
                    "id_produto": id_p,
                    "qtd": qtd_in,
                    "valor_unit": preco_unit, # Ou input manual se variar
                    "plataforma": canal_in
                }])
                
                # 3. Salva usando a função do loader
                sucesso = save_data(novo_df, "vendas")
                
                if sucesso:
                    st.toast("✅ Venda registrada com sucesso!", icon="🎉")
                    time.sleep(1.5) # Tempo para ler a mensagem
                    st.rerun() # ATUALIZA A TELA SOZINHO
                else:
                    st.error("Erro ao salvar no Excel. Verifique se o arquivo está fechado.")
            
            except Exception as e:
                st.error(f"Erro no processamento: {e}")
