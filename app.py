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
# TELA: COMBUSTÍVEL (ESTILO PLANILHA DINÂMICA)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    # Variável para controlar se estamos editando
    if 'idx_edit' not in st.session_state:
        st.session_state.idx_edit = None

    # --- BLOCO DE ENTRADA (FORA DO FORM PARA SER AUTOMÁTICO) ---
    st.subheader("📝 Lançamento Operacional")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista)
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
        origem = st.text_input("ORIGEM")
        
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0)
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0)
        # SOMA INSTANTÂNEA
        total_tanque = saldo_ant + qtd_sol
        st.info(f"📊 TOTAL NO TANQUE: {total_tanque:,.2f} L")
        odm_zarpe = st.number_input("ODM ZARPE", value=0.0, step=0.1)

    with col3:
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
        lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)

    with col4:
        h_mca = st.number_input("H MCA", value=0.0, step=0.1)
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
        
        # CÁLCULO DA FÓRMULA AUTOMÁTICO DURANTE A DIGITAÇÃO
        odm_final = odm_zarpe - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        
        st.error(f"📉 ODM FINAL: {odm_final:,.2f}")
        
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
        local = st.text_input("LOCAL")

    # BOTÕES DE AÇÃO
    c_btn1, c_btn2 = st.columns(2)
    if st.session_state.idx_edit is None:
        if c_btn1.button("✅ Salvar Novo Lançamento", use_container_width=True):
            nova_linha = pd.DataFrame([{
                'ID': len(st.session_state.db_comb), 'Marcar': '', 'Empurrador': emp, 
                'Data': data_sol.strftime('%d/%m/%Y'), 'Litros': total_tanque, 
                'ODM_Fim': odm_final, 'Valor_Comb': valor_nf
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
            st.rerun()
    else:
        if c_btn1.button("💾 SALVAR EDIÇÃO", type="primary", use_container_width=True):
            idx = st.session_state.idx_edit
            st.session_state.db_comb.at[idx, 'Empurrador'] = emp
            st.session_state.db_comb.at[idx, 'Litros'] = total_tanque
            st.session_state.db_comb.at[idx, 'ODM_Fim'] = odm_final
            st.session_state.db_comb.at[idx, 'Valor_Comb'] = valor_nf
            st.session_state.idx_edit = None
            st.rerun()
        if c_btn2.button("❌ Cancelar Edição", use_container_width=True):
            st.session_state.idx_edit = None
            st.rerun()

    # --- TABELA DE HISTÓRICO ---
    st.divider()
    st.subheader("📋 Tabela de Registros")
    
    if not st.session_state.db_comb.empty:
        # Atualiza a coluna de marcação visual
        df_visual = st.session_state.db_comb.copy()
        if st.session_state.idx_edit is not None:
            df_visual.at[st.session_state.idx_edit, 'Marcar'] = '📍 EDITANDO'
            
        st.dataframe(df_visual, use_container_width=True, hide_index=True)
        
        # Bloco de comando para editar
        st.write("---")
        c_sel, c_ed, c_ex = st.columns([1, 1, 1])
        id_escolhido = c_sel.number_input("Digite o ID para Marcar:", min_value=0, step=1)
        
        if c_ed.button("✏️ Marcar e Carregar para Editar"):
            st.session_state.idx_edit = id_escolhido
            st.rerun()
            
        if c_ex.button("🗑️ Excluir Definitivamente"):
            st.session_state.db_comb = st.session_state.db_comb.drop(id_escolhido).reset_index(drop=True)
            # Reajusta os IDs
            st.session_state.db_comb['ID'] = st.session_state.db_comb.index
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
