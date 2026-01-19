import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

#----------------------------------#
# CONFIGURAÇÕES E LISTA DE NAVIOS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

# Estilo Alerta
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

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Data', 'Litros', 'Valor_Comb'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

#----------------------------------#
# TELA: COMBUSTÍVEL (COM CÁLCULO DE SALDO)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista)
            data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
            solicitante = st.text_input("SOLICITANTE", value="ALEX")
        
        with c2:
            # NOVOS CAMPOS DE CÁLCULO
            saldo_anterior = st.number_input("SALDO ANTERIOR (Litros)", min_value=0.0, step=1.0)
            qtd_solicitada = st.number_input("QTD. SOLICITADA (Litros)", min_value=0.0, step=1.0)
            
            # CÁLCULO AUTOMÁTICO
            total_tanque = saldo_anterior + qtd_solicitada
            st.info(f"📊 TOTAL NO TANQUE: {total_tanque:.2f} Litros")
            
        with c3:
            odm_z = st.number_input("ODM ZARPE", step=0.1)
            plano_h = st.number_input("PLANO HORAS", step=0.1)
            h_mca = st.number_input("H MCA", step=0.1)
            
        with c4:
            valor_c = st.number_input("VALOR TOTAL R$ (Diesel)", min_value=0.0)
            local = st.text_input("LOCAL / ORIGEM")
            
        if st.form_submit_button("Salvar Abastecimento"):
            data_br = data_sol.strftime('%d/%m/%Y')
            # Salvamos o Total Tanque no banco de dados
            novo_c = pd.DataFrame([[emp, data_br, total_tanque, valor_c]], 
                                  columns=['Empurrador', 'Data', 'Litros', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, novo_c], ignore_index=True)
            st.success(f"✅ Sucesso! Total de {total_tanque} litros registrado para o {emp}.")

#----------------------------------#
# TELA: RANCHO
#----------------------------------#
elif aba == "🍱 Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores_lista)
            data_ent = st.date_input("DATA ENTREGA", format="DD/MM/YYYY") # DATA BR
        with r2:
            dias_val = st.number_input("DURAÇÃO (DIAS)", min_value=1, value=15)
            valor_ran = st.number_input("VALOR TOTAL R$", min_value=0.0)
        
        prox_rancho = data_ent + timedelta(days=dias_val)
        
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, "Janeiro", prox_rancho, valor_ran]], 
                                  columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r], ignore_index=True)
            st.success(f"Próximo rancho para {emp_r} em: {prox_rancho.strftime('%d/%m/%Y')}")

#----------------------------------#
# DASHBOARD
#----------------------------------#
elif aba == "📊 Dashboard & Relatórios":
    st.header("📊 Relatórios Consolidados")
    
    # Alerta de 5 dias
    hoje = datetime.now().date()
    for _, row in st.session_state.db_rancho.iterrows():
        dias = (row['Proximo_Rancho'] - hoje).days
        if 0 <= dias <= 5:
            st.markdown(f'<div class="alerta-piscante">⚠️ ATENÇÃO: Rancho do {row["Empurrador"]} vence em {dias} dias!</div>', unsafe_allow_html=True)
            
    st.write("Tabela de Custos Integrados:")
    st.dataframe(st.session_state.db_comb, use_container_width=True)
