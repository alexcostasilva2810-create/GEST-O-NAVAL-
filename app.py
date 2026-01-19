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

#---------------------------------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (MATEMÁTICA OFICIAL ALEX)
#---------------------------------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria (Ida e Volta)")
    
    # Identificação Superior
    i1, i2, i3 = st.columns(3)
    with i1: emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="v2_emp")
    with i2: data_m = st.date_input("DATA DA VIAGEM", key="v2_data")
    with i3: trecho_m = st.text_input("TRECHO / SERVIÇO", key="v2_trecho")

    st.divider()

    # Criamos as duas colunas: IDA e VOLTA
    col_ida, col_volta = st.columns(2)

    # Função interna para não repetir código e garantir a mesma matemática nos dois lados
    def processar_coluna(prefixo):
        st.subheader(f"📍 PERCURSO: {prefixo}")
        
        # --- ENTRADAS MANUAIS ---
        c1, c2 = st.columns(2)
        with c1:
            s_odm = st.number_input(f"SALDO DE ODM ({prefixo})", value=0.0, step=1.0, key=f"s_odm_{prefixo}")
            o_compra = st.number_input(f"ODM COMPRA ({prefixo})", value=0.0, step=1.0, key=f"o_comp_{prefixo}")
            t_plano = st.number_input(f"TOTAL PLANO DE HORAS ({prefixo})", value=0.0, step=0.1, key=f"t_plano_{prefixo}")
            rpm = st.number_input(f"RPM ({prefixo})", value=0.0, key=f"rpm_{prefixo}")
            queima = st.number_input(f"QUEIMA L/H ({prefixo})", value=0.0, key=f"queima_{prefixo}")
        
        with c2:
            h_mca = st.number_input(f"HORAS DE MCA ({prefixo})", value=0.0, step=0.1, key=f"h_mca_{prefixo}")
            lts_queima_mca = st.number_input(f"LTS QUEIMA MCA (6.5, 7 ou 8) ({prefixo})", value=7.0, step=0.5, key=f"lts_mca_{prefixo}")
            h_manobra = st.number_input(f"HORA DE MANOBRA ({prefixo})", value=0.0, key=f"h_mano_{prefixo}")
            lh_manobra = st.number_input(f"L/H MANOBRA ({prefixo})", value=0.0, key=f"lh_mano_{prefixo}")
            transf_bt = st.number_input(f"TRANSFERÊNCIA BT ({prefixo})", value=0.0, key=f"transf_{prefixo}")

        # --- MATEMÁTICA APLICADA ---
        o_saida = s_odm + o_compra
        dias_consumo = h_mca / 24 if h_mca > 0 else 0
        cons_mca = h_mca * lts_queima_mca
        cons_mcp = t_plano * queima
        cons_manobra = h_manobra * lh_manobra
        
        # RESULTADOS FINAIS DO PERCURSO
        chegada = o_saida - cons_mca - cons_mcp - cons_manobra - transf_bt
        total_consumo = cons_mca + cons_mcp + cons_manobra
        
        # EXIBIÇÃO DOS RESULTADOS (IGUAL AO VÍDEO)
        st.markdown(f"**ODM SAÍDA:** {o_saida:,.2f} L")
        st.markdown(f"**DIAS CONSUMO:** {dias_consumo:.2f} Dias")
        st.success(f"🏁 VAI CHEGAR COM: {chegada:,.2f} L")
        st.error(f"🔥 TOTAL CONSUMO {prefixo}: {total_consumo:,.2f} L")
        
        return {
            "saida": o_saida, "chegada": chegada, "consumo": total_consumo,
            "mcp": cons_mcp, "mca": cons_mca, "mano": cons_manobra, "transf": transf_bt
        }

    with col_ida:
        res_ida = processar_coluna("IDA")
    
    with col_volta:
        res_volta = processar_coluna("VOLTA")

    # Botão de Salvar que unifica os dois percursos na sua Tabela Geral
    st.divider()
    if st.button("💾 FINALIZAR MEMÓRIA E SALVAR NA TABELA", use_container_width=True, type="primary"):
        nova_linha = pd.DataFrame([{
            "SEL": False,
            "Empurrador": emp_m,
            "Data": data_m.strftime('%d/%m/%Y'),
            "Local": trecho_m,
            "ODM_Zarpe": res_ida['saida'], # Início da viagem
            "ODM_Fim": res_volta['chegada'], # Fim da viagem completa
            "Consumo_Total": res_ida['consumo'] + res_volta['consumo'],
            "Transf": res_ida['transf'] + res_volta['transf']
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
        st.success("Cálculo integrado com sucesso!")
        st.rerun()

#----------------------------------#
# BLOCOS RESTANTES
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
elif aba == "📊 Dashboard":
    st.header("📊 Dashboard")
