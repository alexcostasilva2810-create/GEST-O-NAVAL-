import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestão Naval Integrada", layout="wide")

# Estilo CSS para o Alerta Piscante
st.markdown("""
    <style>
    @keyframes blinker {  50% { opacity: 0; } }
    .alerta-piscante { 
        color: white; 
        background-color: red; 
        padding: 10px; 
        border-radius: 5px; 
        text-align: center;
        font-weight: bold;
        animation: blinker 1s linear infinite;
    }
    </style>
""", unsafe_allow_html=True)

# Inicialização de dados temporários (Enquanto não conectamos ao Google Sheets)
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Litros', 'Valor_Comb'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Data_Entrega', 'Proximo_Rancho', 'Valor_Rancho'])

st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

empurradores = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

# --- TELA DE RANCHO COM ALERTA ---
if aba == "🍱 Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores)
            data_ent = st.date_input("DATA DA ÚLTIMA ENTREGA")
            valor_r = st.number_input("VALOR TOTAL RANCHO R$", min_value=0.0)
        with r2:
            dias_duracao = st.number_input("DURACÃO ESTIMADA (DIAS)", min_value=1, value=15)
            prox_data = data_ent + timedelta(days=dias_duracao)
            st.info(f"Previsão do Próximo Rancho: {prox_data.strftime('%d/%m/%Y')}")
        
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, data_ent.strftime('%B'), data_ent, prox_data, valor_r]], 
                                  columns=['Empurrador', 'Mês', 'Data_Entrega', 'Proximo_Rancho', 'Valor_Rancho'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r])
            st.success("Dados de Rancho Salvos!")

# --- TELA DE INTEGRAÇÃO TOTAL (O QUE VOCÊ PEDIU) ---
elif aba == "📊 Dashboard & Relatórios":
    st.header("📈 Relatório Consolidado e Alertas")
    
    # Verificação de Alertas de 5 dias
    hoje = datetime.now().date()
    for _, row in st.session_state.db_rancho.iterrows():
        dias_para_vencer = (row['Proximo_Rancho'] - hoje).days
        if 0 <= dias_para_vencer <= 5:
            st.markdown(f'<div class="alerta-piscante">⚠️ ATENÇÃO: Programar novo rancho para {row["Empurrador"]}! Vence em {row["Proximo_Rancho"].strftime("%d/%m/%Y")}</div>', unsafe_allow_html=True)

    # Tabela de Integração
    resumo = []
    for e in empurradores:
        gasto_c = st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]['Valor_Comb'].sum()
        lts = st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]['Litros'].sum()
        gasto_r = st.session_state.db_rancho[st.session_state.db_rancho['Empurrador'] == e]['Valor_Rancho'].sum()
        resumo.append({"Empurrador": e, "Total Litros": lts, "Custo Combustível": gasto_c, "Custo Rancho": gasto_r, "TOTAL GERAL": gasto_c + gasto_r})
    
    df_resumo = pd.DataFrame(resumo)
    st.subheader("📋 Tabela Geral de Custos")
    st.dataframe(df_resumo, use_container_width=True)

    # Dashboards (Pizza e Barras)
    c_dash1, c_dash2 = st.columns(2)
    with c_dash1:
        fig_bar = px.bar(df_resumo, x="Empurrador", y="TOTAL GERAL", title="Gasto Total por Empurrador", color="Empurrador")
        st.plotly_chart(fig_bar, use_container_width=True)
    with c_dash2:
        pizza_data = pd.DataFrame({'Cat': ['Combustível', 'Rancho'], 'Val': [df_resumo['Custo Combustível'].sum(), df_resumo['Custo Rancho'].sum()]})
        fig_pie = px.pie(pizza_data, values='Val', names='Cat', title="Distribuição de Gastos (%)", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)

# (Mantenha aqui sua aba de Combustível com os campos que você já tem)
