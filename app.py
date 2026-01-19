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
# TELA: COMBUSTÍVEL (DINÂMICA EXCEL)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista)
            data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
            solicitante = st.text_input("SOLICITANTE", value="ALEX")
            origem = st.text_input("ORIGEM")
            
        with c2:
            saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0)
            qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0)
            # Soma do tanque (conforme pedido anteriormente)
            total_t = saldo_ant + qtd_sol
            st.info(f"📊 TOTAL NO TANQUE: {total_t:,.2f} L")
            odm_z = st.number_input("ODM ZARPE", value=0.0, step=0.1)
            
        with c3:
            plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
            lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
            h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
            lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)
            
        with c4:
            h_mca = st.number_input("H MCA", value=0.0, step=0.1)
            transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
            
            # --- CÁLCULO DA SUA FÓRMULA DO EXCEL ---
            # ODM FIM = ODM ZARPE - (PLANO H * LH RPM) - (H MANOBRA * LH MANOBRA) - (H MCA * 7) - TRANSF BALSA
            odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
            
            st.warning(f"📉 ODM FINAL CALCULADO: {odm_fim:,.2f}")
            
            valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
            local = st.text_input("LOCAL")

        if st.form_submit_button("✅ Salvar Abastecimento"):
            data_br = data_sol.strftime('%d/%m/%Y')
            nova_linha = pd.DataFrame([[emp, data_br, total_t, odm_fim, valor_nf]], 
                                     columns=['Empurrador', 'Data', 'Litros', 'ODM_Fim', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
            st.success(f"Registro salvo! ODM Final: {odm_fim:,.2f}")
            st.rerun()

    # 2. TABELA COM ID PARA EDIÇÃO
    st.divider()
    st.subheader("📋 Histórico de Lançamentos")
    if not st.session_state.db_comb.empty:
        st.dataframe(st.session_state.db_comb, use_container_width=True)
        
        # Bloco de Edição/Exclusão por ID
        col_ed, col_ex = st.columns(2)
        idx = col_ed.number_input("ID para ajustar Nota Fiscal ou Excluir:", min_value=0, step=1)
        
        if col_ed.button("✏️ Editar Valor da NF"):
            # Aqui você pode carregar para editar como fizemos antes
            st.info("Função de edição ativa para o ID selecionado.")
            
        if col_ex.button("🗑️ Excluir Linha"):
            st.session_state.db_comb = st.session_state.db_comb.drop(idx).reset_index(drop=True)
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
