import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

#----------------------------------#
# BANCO DE DADOS (MEMÓRIA)
#----------------------------------#
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=[
        'SEL', 'Empurrador', 'Data', 'Saldo_Ant', 'Qtd_Sol', 'ODM_Zarpe',
        'Plano_H', 'LH_RPM', 'H_Manobra', 'H_MCA', 'Transf',
        'ODM_Fim', 'Valor_NF', 'Local'
    ])

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "📝 Controle Diário", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# BLOCO 1 - ABASTECIMENTO (COMBUSTÍVEL)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    st.subheader("📝 Lançamento de Abastecimento")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista, key="c_emp")
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
        origem = st.text_input("ORIGEM")
    with c2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0, key="c_saldo")
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0, key="c_qtd")
        odm_z = saldo_ant + qtd_sol # SOMA AUTOMÁTICA
        st.success(f"⚓ ODM ZARPE (SOMA): {odm_z:,.2f} L")
    with c3:
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1, key="c_plano")
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1, key="c_rpm")
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1, key="c_mano")
    with c4:
        h_mca = st.number_input("H MCA", value=0.0, step=0.1, key="c_mca")
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1, key="c_transf")
        # FÓRMULA ODM FIM
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_mca * 7) - transf_balsa
        st.error(f"📉 ODM FINAL: {odm_fim:,.2f}")
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0, key="c_nf")

    if st.button("✅ SALVAR NOVO ABASTECIMENTO", use_container_width=True, type="primary"):
        nova_l = pd.DataFrame([{
            "SEL": False, "Empurrador": emp, "Data": data_sol.strftime('%d/%m/%Y'), 
            "Saldo_Ant": saldo_ant, "Qtd_Sol": qtd_sol, "ODM_Zarpe": odm_z,
            "Plano_H": plano_h, "LH_RPM": lh_rpm, "H_Manobra": h_manobra,
            "H_MCA": h_mca, "Transf": transf_balsa,
            "ODM_Fim": odm_fim, "Valor_NF": valor_nf, "Local": origem
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    st.divider()
    st.subheader("📋 Tabela de Registros Integrados")
    if not st.session_state.db_comb.empty:
        tabela_editada = st.data_editor(
            st.session_state.db_comb,
            use_container_width=True,
            hide_index=True,
            column_config={"SEL": st.column_config.CheckboxColumn("SEL", default=False)},
            key="editor_direto"
        )
        if not tabela_editada.equals(st.session_state.db_comb):
            st.session_state.db_comb = tabela_editada
            st.toast("Alteração salva!")
        
        if st.button("🗑️ Excluir Linhas Marcadas"):
            st.session_state.db_comb = st.session_state.db_comb[st.session_state.db_comb["SEL"] == False]
            st.rerun()

#----------------------------------#
# BLOCO 2 - CONTROLE DIÁRIO (VÍDEO 2)
#----------------------------------#
elif aba == "📝 Controle Diário":
    st.header("📝 Lançamento de Medição Diária")
    st.write("Cálculo de consumo diário por horímetro.")

    d1, d2, d3, d4 = st.columns(4)
    with d1:
        emp_v2 = st.selectbox("EMPURRADOR", empurradores_lista, key="v2_emp")
        data_v2 = st.date_input("DATA", format="DD/MM/YYYY", key="v2_data")
        trecho = st.text_input("TRECHO / SERVIÇO", key="v2_trecho")
    with d2:
        h_ini = st.number_input("HORÍMETRO INICIAL", min_value=0.0, step=0.1, key="v2_hini")
        h_fim = st.number_input("HORÍMETRO FINAL", min_value=0.0, step=0.1, key="v2_hfim")
        horas_trab = h_fim - h_ini
        st.metric("HORAS TRABALHADAS", f"{horas_trab:.1f} h")
    with d3:
        media_lh = st.number_input("MÉDIA L/H", value=0.0, step=0.1, key="v2_media")
        consumo_motor = horas_trab * media_lh
        st.metric("CONSUMO MOTOR (L)", f"{consumo_motor:.2f} L")
    with d4:
        mca_h = st.number_input("HORAS MCA", value=0.0, step=0.1, key="v2_mca")
        consumo_total_dia = consumo_motor + (mca_h * 7.0)
        st.warning(f"⛽ TOTAL CONSUMIDO: {consumo_total_dia:,.2f} L")

    if st.button("🚀 FINALIZAR E ATUALIZAR TABELA GERAL", use_container_width=True, type="primary"):
        nova_linha_comb = pd.DataFrame([{
            "SEL": False, "Empurrador": emp_v2, "Data": data_v2.strftime('%d/%m/%Y'),
            "Saldo_Ant": 0.0, "Qtd_Sol": 0.0, "ODM_Zarpe": 0.0,
            "Plano_H": horas_trab, "LH_RPM": media_lh, "H_Manobra": 0.0,
            "H_MCA": mca_h, "Transf": 0.0,
            "ODM_Fim": consumo_total_dia, "Valor_NF": 0.0, "Local": trecho
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha_comb], ignore_index=True)
        st.success("✅ Enviado para a Tabela de Combustível!")
        st.rerun()

#----------------------------------#
# BLOCO 3 - RANCHO
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
    st.info("Área em construção para provisões.")

#----------------------------------#
# BLOCO 4 - DASHBOARD
#----------------------------------#
elif aba == "📊 Dashboard":
    st.header("📊 Dashboard")
    st.write("Resumo estatístico dos lançamentos.")
