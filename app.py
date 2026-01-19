import streamlit as st
import pd as pd

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = ["ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", "QUARUBA", "TIMBORANA", "JATOBA"]

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['SEL', 'Empurrador', 'Data', 'Saldo_Ant', 'Qtd_Sol', 'ODM_Zarpe', 'Plano_H', 'LH_RPM', 'H_MCA', 'ODM_Fim', 'Local'])

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
# Nome alterado para "Cálculo de Memória" no menu
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Calculo de mémoria", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# BLOCO 1 - ABASTECIMENTO 
#----------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Lançamento de Abastecimento")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista, key="t1_emp")
        data_sol = st.date_input("DATA", format="DD/MM/YYYY", key="t1_data")
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0, key="t1_saldo")
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0, key="t1_qtd")
        odm_z = saldo_ant + qtd_sol
        st.success(f"⚓ TOTAL NO TANQUE: {odm_z:,.2f}")
    with col3:
        origem = st.text_input("LOCAL / NF", key="t1_local")
        if st.button("✅ SALVAR ABASTECIMENTO", use_container_width=True, type="primary"):
            nova_l = pd.DataFrame([{"SEL": False, "Empurrador": emp, "Data": data_sol.strftime('%d/%m/%Y'), "Saldo_Ant": saldo_ant, "Qtd_Sol": qtd_sol, "ODM_Zarpe": odm_z, "ODM_Fim": odm_z, "Local": origem}])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
            st.rerun()

    st.divider()
    st.subheader("📋 Tabela Geral de Combustível")
    if not st.session_state.db_comb.empty:
        tabela_editada = st.data_editor(st.session_state.db_comb, use_container_width=True, hide_index=True, column_config={"SEL": st.column_config.CheckboxColumn("SEL", default=False)}, key="ed_geral")
        if st.button("🗑️ Excluir Selecionados"):
            st.session_state.db_comb = st.session_state.db_comb[st.session_state.db_comb["SEL"] == False]
            st.rerun()

#----------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (IDA/VOLTA)
#----------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria (Ida e Volta)")
    
    # Linha de Identificação
    c_id1, c_id2, c_id3 = st.columns(3)
    with c_id1:
        emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="t2_emp")
    with c_id2:
        data_m = st.date_input("DATA DA VIAGEM", key="t2_data")
    with c_id3:
        trecho_m = st.text_input("TRECHO GERAL", key="t2_trecho")

    st.divider()

    # Colunas Lado a Lado: IDA e VOLTA
    col_ida, col_volta = st.columns(2)

    with col_ida:
        st.subheader("🚀 PERCURSO: IDA")
        h_ini_i = st.number_input("HORÍMETRO INICIAL (IDA)", value=0.0, key="h_i_i")
        h_fim_i = st.number_input("HORÍMETRO FINAL (IDA)", value=0.0, key="h_f_i")
        media_i = st.number_input("MÉDIA L/H (IDA)", value=0.0, key="m_i")
        horas_i = h_fim_i - h_ini_i
        cons_i = horas_i * media_i
        st.info(f"Consumo Ida: {cons_i:.2f} L")

    with col_volta:
        st.subheader("🔙 PERCURSO: VOLTA")
        h_ini_v = st.number_input("HORÍMETRO INICIAL (VOLTA)", value=0.0, key="h_i_v")
        h_fim_v = st.number_input("HORÍMETRO FINAL (VOLTA)", value=0.0, key="h_f_v")
        media_v = st.number_input("MÉDIA L/H (VOLTA)", value=0.0, key="m_v")
        horas_v = h_fim_v - h_ini_v
        cons_v = horas_v * media_v
        st.info(f"Consumo Volta: {cons_v:.2f} L")

    st.divider()
    
    # Resumo Final e MCA
    res1, res2, res3 = st.columns(3)
    with res1:
        h_mca_m = st.number_input("HORAS MCA (GERAL)", value=0.0, key="t2_mca")
        cons_mca = h_mca_m * 7.0
    with res2:
        total_consumo = cons_i + cons_v + cons_mca
        st.error(f"📉 CONSUMO TOTAL: {total_consumo:,.2f} L")
    with res3:
        st.write("---")
        if st.button("💾 SALVAR E INTEGRAR", use_container_width=True, type="primary"):
            # Envia os dados somados para a tabela principal
            nova_med = pd.DataFrame([{
                "SEL": False, 
                "Empurrador": emp_m, 
                "Data": data_m.strftime('%d/%m/%Y'), 
                "Plano_H": horas_i + horas_v, 
                "LH_RPM": (media_i + media_v)/2, 
                "H_MCA": h_mca_m, 
                "ODM_Fim": total_consumo, 
                "Local": trecho_m
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_med], ignore_index=True)
            st.success("Medição enviada para a Tabela Geral!")
            st.rerun()

#----------------------------------#
# BLOCO 3 - RANCHO
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
    st.info("Espaço para lançamentos de pedidos de rancho.")

#----------------------------------#
# BLOCO 4 - DASHBOARD
#----------------------------------#
elif aba == "📊 Dashboard":
    st.header("📊 Dashboard de Consumo")
