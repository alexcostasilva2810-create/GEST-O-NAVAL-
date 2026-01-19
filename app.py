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

# BANCO DE DADOS COMPLETO (Contém todos os campos das duas telas)
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=[
        'SEL', 'Empurrador', 'Data', 'Solicitante', 'Origem', 'Saldo_Ant', 'Qtd_Sol', 
        'ODM_Zarpe', 'H_Ini_Ida', 'H_Fim_Ida', 'Media_Ida', 'H_Ini_Volta', 'H_Fim_Volta', 
        'Media_Volta', 'H_MCA', 'Media_Ponderada', 'Consumo_Total', 'Valor_NF', 'Local_Trecho'
    ])

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Calculo de mémoria", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# BLOCO 1 - ABASTECIMENTO
#----------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Lançamento de Abastecimento")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista, key="t1_emp")
        data_sol = st.date_input("DATA", format="DD/MM/YYYY", key="t1_data")
        solicitante = st.text_input("SOLICITANTE", value="ALEX", key="t1_soli")
    with col2:
        origem = st.text_input("ORIGEM / LOCAL", key="t1_orig")
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0, key="t1_saldo")
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0, key="t1_qtd")
    with col3:
        odm_z = saldo_ant + qtd_sol
        st.success(f"⚓ ODM ZARPE: {odm_z:,.2f}")
        valor_nf = st.number_input("VALOR TOTAL R$ (NF)", min_value=0.0, key="t1_nf")
    with col4:
        st.write("---")
        if st.button("✅ SALVAR ABASTECIMENTO", use_container_width=True, type="primary"):
            nova_l = pd.DataFrame([{
                "SEL": False, "Empurrador": emp, "Data": data_sol.strftime('%d/%m/%Y'), 
                "Solicitante": solicitante, "Origem": origem, "Saldo_Ant": saldo_ant, 
                "Qtd_Sol": qtd_sol, "ODM_Zarpe": odm_z, "Valor_NF": valor_nf,
                "Consumo_Total": 0.0, "Media_Ponderada": 0.0 # Campos de consumo zerados no abastecimento
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
            st.rerun()

    st.divider()
    st.subheader("📋 Tabela Geral de Registros")
    if not st.session_state.db_comb.empty:
        st.data_editor(st.session_state.db_comb, use_container_width=True, hide_index=True, key="ed_geral")

#----------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (COM MÉDIA PONDERADA)
#----------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria com Média Ponderada")
    
    # Identificação Geral
    c_id1, c_id2, c_id3 = st.columns(3)
    with c_id1:
        emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="t2_emp")
    with c_id2:
        data_m = st.date_input("DATA DA VIAGEM", key="t2_data")
    with c_id3:
        trecho_m = st.text_input("TRECHO / SERVIÇO", key="t2_trecho")

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
        st.info(f"Horas: {horas_i:.1f}h | Consumo: {cons_i:.2f}L")

    with col_volta:
        st.subheader("🔙 PERCURSO: VOLTA")
        h_ini_v = st.number_input("HORÍMETRO INICIAL (VOLTA)", value=0.0, key="h_i_v")
        h_fim_v = st.number_input("HORÍMETRO FINAL (VOLTA)", value=0.0, key="h_f_v")
        media_v = st.number_input("MÉDIA L/H (VOLTA)", value=0.0, key="m_v")
        horas_v = h_fim_v - h_ini_v
        cons_v = horas_v * media_v
        st.info(f"Horas: {horas_v:.1f}h | Consumo: {cons_v:.2f}L")

    st.divider()
    
    # Cálculos Finais (Média Ponderada)
    res1, res2, res3 = st.columns(3)
    with res1:
        h_mca_m = st.number_input("HORAS MCA (GERAL)", value=0.0, key="t2_mca")
        cons_mca = h_mca_m * 7.0
        st.write(f"Consumo MCA: {cons_mca:.2f}L")
        
    with res2:
        total_horas = horas_i + horas_v
        total_cons_motores = cons_i + cons_v
        
        # --- CÁLCULO MÉDIA PONDERADA (IGUAL AO EXCEL) ---
        if total_horas > 0:
            media_ponderada = total_cons_motores / total_horas
        else:
            media_ponderada = 0.0
            
        st.metric("MÉDIA PONDERADA L/H", f"{media_ponderada:.2f}")

    with res3:
        total_geral_consumo = total_cons_motores + cons_mca
        st.error(f"📉 CONSUMO TOTAL GERAL: {total_geral_consumo:,.2f} L")
        
        if st.button("💾 SALVAR E INTEGRAR", use_container_width=True, type="primary"):
            nova_med = pd.DataFrame([{
                "SEL": False, 
                "Empurrador": emp_m, 
                "Data": data_m.strftime('%d/%m/%Y'),
                "Local_Trecho": trecho_m,
                "H_Ini_Ida": h_ini_i, "H_Fim_Ida": h_fim_i, "Media_Ida": media_i,
                "H_Ini_Volta": h_ini_v, "H_Fim_Volta": h_fim_v, "Media_Volta": media_v,
                "H_MCA": h_mca_m,
                "Media_Ponderada": media_ponderada,
                "Consumo_Total": total_geral_consumo
            }])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_med], ignore_index=True)
            st.success("✅ Cálculo de Memória salvo na Tabela Geral!")
            st.rerun()

#----------------------------------#
# BLOCOS RESTANTES
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
elif aba == "📊 Dashboard":
    st.header("📊 Dashboard")
