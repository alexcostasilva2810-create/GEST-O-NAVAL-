import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

# Estilo para o Alerta Piscante
st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0; } }
    .alerta-piscante { 
        color: white; background-color: #FF0000; 
        padding: 15px; border-radius: 10px; 
        text-align: center; font-weight: bold;
        animation: blinker 1.5s linear infinite;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Banco de dados temporário
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Litros', 'Valor_Comb'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Data_Entrega', 'Proximo_Rancho', 'Valor_Rancho'])

st.sidebar.title("🚢 Menu de Navegação")
aba = st.sidebar.radio("Ir para:", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

empurradores = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

# --- TELA DE RANCHO COMPLETA COM ALERTA ---
if aba == "🍱 Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        col1, col2 = st.columns(2)
        with col1:
            emp_r = st.selectbox("EMPURRADOR", empurradores)
            comprador = st.text_input("COMPRADOR")
            sc = st.text_input("SC")
            data_sol = st.date_input("DATA SOLICITAÇÃO")
        with col2:
            data_ent = st.date_input("DATA ENTREGA (ÚLTIMA)")
            dias_validade = st.number_input("DURAÇÃO ESTIMADA (DIAS)", min_value=1, value=15)
            valor_r = st.number_input("VALOR TOTAL RANCHO R$", min_value=0.0)
            desc = st.text_area("DESCRIÇÃO DO MATERIAL")
        
        prox_data = data_ent + timedelta(days=dias_validade)
        
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, data_ent.strftime('%B'), data_ent, prox_data, valor_r]], 
                                  columns=['Empurrador', 'Mês', 'Data_Entrega', 'Proximo_Rancho', 'Valor_Rancho'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r])
            st.success(f"Rancho salvo! Próxima previsão: {prox_data.strftime('%d/%m/%Y')}")

# --- TELA DE INTEGRAÇÃO E ALERTAS ---
elif aba == "📊 Dashboard & Relatórios":
    st.header("📈 Relatório Geral e Alertas de Vencimento")
    
    # Lógica do Alerta de 5 dias
    hoje = datetime.now().date()
    for _, row in st.session_state.db_rancho.iterrows():
        dias_restantes = (row['Proximo_Rancho'] - hoje).days
        if 0 <= dias_restantes <= 5:
            st.markdown(f'<div class="alerta-piscante">⚠️ ALERTA: Programar novo rancho para o {row["Empurrador"]}! Vencimento em {row["Proximo_Rancho"].strftime("%d/%m/%Y")} ({dias_restantes} dias)</div>', unsafe_allow_html=True)

    # Tabela de Integração Total
    resumo = []
    for e in empurradores:
        gasto_c = st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]['Valor_Comb'].sum()
        lts = st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]['Litros'].sum()
        gasto_r = st.session_state.db_rancho[st.session_state.db_rancho['Empurrador'] == e]['Valor_Rancho'].sum()
        resumo.append({
            "Empurrador": e, 
            "Abastecimentos": len(st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]),
            "Total Litros": lts, 
            "R$ Combustível": gasto_c, 
            "R$ Rancho": gasto_r, 
            "INVESTIMENTO TOTAL": gasto_c + gasto_r
        })
    
    df_resumo = pd.DataFrame(resumo)
    st.subheader("📋 Tabela Consolidada")
    st.dataframe(df_resumo, use_container_width=True)

    # Dashboard
    col_gr1, col_gr2 = st.columns(2)
    with col_gr1:
        fig_bar = px.bar(df_resumo, x="Empurrador", y="INVESTIMENTO TOTAL", title="Gasto Total por Embarcação", color="Empurrador", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_gr2:
        pizza_data = pd.DataFrame({'Cat': ['Diesel', 'Rancho'], 'Val': [df_resumo['R$ Combustível'].sum(), df_resumo['R$ Rancho'].sum()]})
        fig_pie = px.pie(pizza_data, values='Val', names='Cat', title="Divisão de Custos Operacionais", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

# (Aba de combustível continua aqui conforme você já tem)
