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
# BANCO DE DADOS (MEMÓRIA UNIFICADA)
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
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Medição Diária", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# BLOCO 1 - ABASTECIMENTO (TELA 1)
#----------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Lançamento de Abastecimento")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista, key="t1_emp")
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY", key="t1_data")
        origem = st.text_input("ORIGEM/LOCAL", key="t1_origem")
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0, key="t1_saldo")
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0, key="t1_qtd")
        odm_z = saldo_ant + qtd_sol # SOMA AUTOMÁTICA
        st.success(f"⚓ ODM ZARPE: {odm_z:,.2f}")
    with col3:
        # Campos de ajuste manual para abastecimento se necessário
        h_mano = st.number_input("H. MANOBRA", value=0.0, key="t1_mano")
        valor_nf = st.number_input("VALOR TOTAL R$", min_value=0.0, key="t1_nf")
    with col4:
        st.write("---")
        if st.button("✅ SALVAR ABASTECIMENTO", use_container_width=True, type="primary"):
            nova_l = pd.DataFrame([{
                "SEL": False, "Empurrador": emp, "Data": data_sol.strftime('%d/%m/%Y'), 
                "Saldo_Ant": saldo_ant, "Qtd_Sol": qtd_sol, "ODM_Zarpe": odm_z,
                "Plano_H": 0.0, "LH_RPM": 0.0, "H_Manobra": h_mano,
                "H_MCA": 0.0, "Transf": 0.0, "ODM_Fim": odm_z, 
                "Valor_NF": valor_nf, "Local": origem
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
            st.rerun()

    st.divider()
    st.subheader("📋 Tabela Geral de Combustível (Abastecimentos e Medições)")
    if not st.session_state.db_comb.empty:
        tabela_editada = st.data_editor(
            st.session_state.db_comb,
            use_container_width=True,
            hide_index=True,
            column_config={"SEL": st.column_config.CheckboxColumn("SEL", default=False)},
            key="editor_geral"
        )
        if st.button("🗑️ Excluir Selecionados"):
            st.session_state.db_comb = st.session_state.db_comb[st.session_state.db_comb["SEL"] == False]
            st.rerun()

#----------------------------------#
# BLOCO 2 - MEDIÇÃO DIÁRIA (TELA 2)
#----------------------------------#
elif aba == "📝 Medição Diária":
    st.header("📝 Medição de Consumo Diário")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="t2_emp")
        data_m = st.date_input("DATA MEDIÇÃO", format="DD/MM/YYYY", key="t2_data")
        trecho = st.text_input("TRECHO / SERVIÇO", key="t2_trecho")
    with m2:
        h_ini = st.number_input("HORÍMETRO INICIAL", min_value=0.0, step=0.1, key="t2_hini")
        h_fim = st.number_input("HORÍMETRO FINAL", min_value=0.0, step=0.1, key="t2_hfim")
        horas_t = h_fim - h_ini
        st.metric("HORAS TRABALHADAS", f"{horas_t:.1f} h")
    with m3:
        media_lh = st.number_input("MÉDIA L/H RPM", value=0.0, step=0.1, key="t2_media")
        consumo_mp = horas_t * media_lh
        st.metric("CONS. MOTOR (L)", f"{consumo_mp:.2f}")
    with m4:
        h_mca_m = st.number_input("HORAS MCA", value=0.0, step=0.1, key="t2_mca")
        total_consumo = consumo_mp + (h_mca_m * 7.0)
        st.error(f"📉 TOTAL CONSUMO: {total_consumo:,.2f}")
        
        if st.button("💾 SALVAR NA TABELA DE COMBUSTÍVEL", use_container_width=True, type="primary"):
            nova_med = pd.DataFrame([{
                "SEL": False, "Empurrador": emp_m, "Data": data_m.strftime('%d/%m/%Y'),
                "Saldo_Ant": 0.0, "Qtd_Sol": 0.0, "ODM_Zarpe": 0.0,
                "Plano_H": horas_t, "LH_RPM": media_lh, "H_Manobra": 0.0,
                "H_MCA": h_mca_m, "Transf": 0.0,
                "ODM_Fim": total_consumo, "Valor_NF": 0.0, "Local": trecho
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_med], ignore_index=True)
            st.success("✅ Medição enviada para a tabela principal!")
            st.rerun()

#----------------------------------#
# BLOCO 3 - RANCHO
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
    st.write("Área para provisões.")

#----------------------------------#
# BLOCO 4 - DASHBOARD
#----------------------------------#
elif aba == "📊 Dashboard":
    st.header("📊 Resumo Estatístico")
