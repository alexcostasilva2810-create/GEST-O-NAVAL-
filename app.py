import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

#----------------------------------#
# LISTA OFICIAL DE EMPURRADORES
#----------------------------------#
empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

#----------------------------------#
# BANCO DE DADOS (MEMÓRIA)
#----------------------------------#
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['SEL', 'ID', 'Empurrador', 'Data', 'Litros', 'ODM_Fim', 'Valor_NF'])

if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['ID', 'Empurrador', 'Data', 'Tipo', 'Valor'])

#----------------------------------#
# BARRA LATERAL (MENU)
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# TELA: COMBUSTÍVEL
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    st.subheader("📝 Lançamento e Edição")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista)
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
        origem = st.text_input("ORIGEM")
        
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0)
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0)
        
        # --- AJUSTE SOLICITADO ---
        # ODM ZARPE AGORA É A SOMA AUTOMÁTICA
        odm_z = saldo_ant + qtd_sol
        st.success(f"⚓ ODM ZARPE (SOMA): {odm_z:,.2f} L")
        
    with col3:
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
        lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)
        
    with col4:
        h_mca = st.number_input("H MCA", value=0.0, step=0.1)
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
        
        # FÓRMULA AUTOMÁTICA DO ODM FIM USANDO O NOVO ODM ZARPE (SOMA)
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        
        st.error(f"📉 ODM FINAL: {odm_fim:,.2f}")
        
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
        local = st.text_input("LOCAL")

    #----------------------------------#
    # BLOCO: BOTÃO SALVAR
    #----------------------------------#
    if st.button("✅ SALVAR REGISTRO", use_container_width=True, type="primary"):
        nova_l = pd.DataFrame([{
            "SEL": False, 
            "ID": len(st.session_state.db_comb), 
            "Empurrador": emp, 
            "Data": data_sol.strftime('%d/%m/%Y'), 
            "Litros": odm_z, # Aqui salvamos a soma (Zarpe)
            "ODM_Fim": odm_fim, 
            "Valor_NF": valor_nf
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    #----------------------------------#
    # BLOCO: TABELA COM SEL (QUADRADO)
    #----------------------------------#
    st.divider()
    if not st.session_state.db_comb.empty:
        tabela_editavel = st.data_editor(
            st.session_state.db_comb,
            column_config={"SEL": st.column_config.CheckboxColumn("SEL", default=False)},
            disabled=["ID", "Empurrador", "Data", "Litros", "ODM_Fim", "Valor_NF"],
            hide_index=True, use_container_width=True, key="editor_comb"
        )

#----------------------------------#
# TELA: RANCHO (MANTIDA)
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores_lista)
            data_r = st.date_input("DATA PEDIDO")
        with r2:
            tipo_r = st.selectbox("TIPO", ["Rancho Mensal", "Complemento"])
            valor_r = st.number_input("VALOR R$", min_value=0.0)
        if st.form_submit_button("✅ Salvar"):
            st.success("Pedido de Rancho Salvo!")
