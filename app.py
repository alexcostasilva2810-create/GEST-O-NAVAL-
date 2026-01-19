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
# TELA: COMBUSTÍVEL (VISUAL ORIGINAL + CÁLCULO ATIVADO)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    
    # 1. FORMULÁRIO ORIGINAL COMPLETO
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista)
            data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
            solicitante = st.text_input("SOLICITANTE", value="ALEX")
            origem = st.text_input("ORIGEM")
        with c2:
            # CAMPOS DO CÁLCULO MATEMÁTICO
            saldo_ant = st.number_input("SALDO ANTERIOR (Litros)", min_value=0.0, step=1.0)
            qtd_sol = st.number_input("QTD. SOLICITADA (Litros)", min_value=0.0, step=1.0)
            
            # A SOMA AUTOMÁTICA QUE APARECE NA TELA
            total_t = saldo_ant + qtd_sol
            st.info(f"📊 TOTAL NO TANQUE: {total_t:,.2f} L")
            
            odm_z = st.number_input("ODM ZARPE", step=0.1)
        with c3:
            plano_h = st.number_input("PLANO HORAS", step=0.1)
            lh_rpm = st.number_input("L/H RPM", step=0.1)
            h_manobra = st.number_input("H. MANOBRA", step=0.1)
            h_mca = st.number_input("H MCA", step=0.1)
        with c4:
            mes_ref = st.selectbox("MÊS/ANO", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            local = st.text_input("LOCAL")
            balsas = st.text_input("BALSAS")
            valor_c = st.number_input("VALOR TOTAL R$ (Diesel)", min_value=0.0)
            
        if st.form_submit_button("Salvar Abastecimento"):
            data_br = data_sol.strftime('%d/%m/%Y')
            # Salvando o resultado da soma (total_t) na coluna de Litros
            novo_c = pd.DataFrame([[emp, data_br, total_t, valor_c]], 
                                  columns=['Empurrador', 'Data', 'Litros', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, novo_c], ignore_index=True)
            st.success(f"✅ Salvo com sucesso! Total: {total_t:,.2f} Litros.")
            st.rerun()

    # 2. TABELA DE REGISTROS (Abaixo do formulário)
    st.divider()
    st.subheader("📋 Registros de Abastecimento")
    if not st.session_state.db_comb.empty:
        st.dataframe(st.session_state.db_comb, use_container_width=True)
        
        # 3. BLOCO DE AJUSTE (Para trocar o valor 0,00 pela Nota Fiscal depois)
        st.markdown("---")
        st.write("🔧 **Ajustar Valor de Nota Fiscal ou Remover Registro**")
        col_aj1, col_aj2, col_aj3 = st.columns([1, 1, 1])
        
        with col_aj1:
            id_edit = st.number_input("ID da Linha (número à esquerda):", min_value=0, step=1)
        with col_aj2:
            nova_nf = st.number_input("Novo Valor da Nota (R$):", min_value=0.0)
        
        if col_aj1.button("💾 Atualizar NF"):
            # Atualiza o valor na tabela sem mexer no resto
            st.session_state.db_comb.at[id_edit, 'Valor_Comb'] = nova_nf
            st.success(f"Valor da linha {id_edit} atualizado!")
            st.rerun()
            
        if col_aj3.button("🗑️ Excluir Linha"):
            st.session_state.db_comb = st.session_state.db_comb.drop(id_edit).reset_index(drop=True)
            st.rerun()

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
