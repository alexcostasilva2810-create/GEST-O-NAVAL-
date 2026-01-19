import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = ["ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", "QUARUBA", "TIMBORANA", "JATOBA"]

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame()

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Calculo de mémoria", "🛒 Rancho", "📊 Dashboard"])

#---------------------------------------------------------#
# BLOCO 1 - ABASTECIMENTO (REFORMULADO)
#---------------------------------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Tabela de Abastecimento e Movimentação")
    
    if not st.session_state.db_comb.empty:
        df_abast = []
        for index, row in st.session_state.db_comb.iterrows():
            # Tratar Origem e Destino pelo "X"
            trecho = str(row.get('Local', '')).upper()
            origem_auto, destino_auto = (trecho.split('X', 1) + [""])[:2] if 'X' in trecho else (trecho, "")

            # Matemática L/H RPM (Média Ponderada)
            h_total = row['Plano_H_Ida'] + row['Plano_H_Volta']
            if h_total > 0:
                lh_rpm_calc = (row['Plano_H_Ida'] * row['Queima_Ida'] + row['Plano_H_Volta'] * row['Queima_Volta']) / h_total
            else:
                lh_rpm_calc = row['Queima_Ida']

            df_abast.append({
                "DATA SOLICITAÇÃO": datetime.now().strftime('%d/%m/%Y'), # Data de hoje em BR
                "SOLICITANTE": "ALEX",
                "EMPURRADOR": row['Empurrador'],
                "MÊS/ANO": row['Mes_Ano'],
                "ORIGEM": origem_auto.strip(),
                "DESTINO": destino_auto.strip(),
                "ODM ZARPE": row['ODM_Zarpe_Ida'],
                "PLANO HORAS": h_total,
                "L/H RPM": round(lh_rpm_calc, 2),
                "H. MANOBRA": row['H_Mano_Ida'] + row['H_Mano_Volta'],
                "L/H MANOBRA": row['LH_Mano_Ida'] + row['LH_Mano_Volta'],
                "H MCA": row['H_MCA_Ida'] + row['H_MCA_Volta'],
                "ODM FIM": row['ODM_Fim_Final']
            })

        # Exibição com formatação de números
        st.data_editor(
            pd.DataFrame(df_abast), 
            use_container_width=True, 
            hide_index=True, 
            key="view_abast"
        )
    else:
        st.info("Aguardando lançamentos no Cálculo de Memória...")

#---------------------------------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (DATA BR NO CALENDÁRIO)
#---------------------------------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria (Ida e Volta)")
    
    i1, i2, i3 = st.columns(3)
    with i1: 
        emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="v2_emp")
    with i2: 
        # Calendário configurado para formato Brasileiro
        data_m = st.date_input("DATA DA VIAGEM", format="DD/MM/YYYY", key="v2_data")
    with i3: 
        trecho_m = st.text_input("TRECHO / SERVIÇO (Ex: MANAUS X BELEM)", key="v2_trecho")

    st.divider()
    col_ida, col_volta = st.columns(2)

    def entrada_dados(prefixo):
        st.subheader(f"📍 {prefixo}")
        s_odm = st.number_input(f"SALDO DE ODM ({prefixo})", value=0.0, step=1.0, key=f"s_{prefixo}")
        o_comp = st.number_input(f"ODM COMPRA ({prefixo})", value=0.0, step=1.0, key=f"c_{prefixo}")
        t_hor = st.number_input(f"TOTAL PLANO DE HORAS ({prefixo})", value=0.0, step=0.1, key=f"h_{prefixo}")
        queima = st.number_input(f"QUEIMA L/H ({prefixo})", value=0.0, step=0.1, key=f"q_{prefixo}")
        h_mca = st.number_input(f"HORAS DE MCA ({prefixo})", value=0.0, step=0.1, key=f"mca_{prefixo}")
        lts_mca = st.number_input(f"LTS QUEIMA MCA ({prefixo})", value=7.0, step=0.1, key=f"l_{prefixo}")
        h_mano = st.number_input(f"HORA DE MANOBRA ({prefixo})", value=0.0, step=0.1, key=f"hm_{prefixo}")
        lh_mano = st.number_input(f"L/H MANOBRA ({prefixo})", value=0.0, step=0.1, key=f"lhm_{prefixo}")
        transf = st.number_input(f"TRANSFERÊNCIA BT ({prefixo})", value=0.0, step=1.0, key=f"t_{prefixo}")
        
        saida = s_odm + o_comp
        cons = (t_hor * queima) + (h_mca * lts_mca) + (h_mano * lh_mano)
        chegada = saida - cons - transf
        
        st.write(f"**ODM SAÍDA:** {saida:,.2f} | **CHEGADA:** {chegada:,.2f}")
        return {"saida": saida, "chegada": chegada, "t_hor": t_hor, "queima": queima, "h_mca": h_mca, "h_mano": h_mano, "lh_mano": lh_mano}

    with col_ida: res_i = entrada_dados("IDA")
    with col_volta: res_v = entrada_dados("VOLTA")

    if st.button("💾 FINALIZAR E SALVAR", use_container_width=True, type="primary"):
        # Salvamento com datas já formatadas em string BR
        nova_linha = pd.DataFrame([{
            "Empurrador": emp_m, 
            "Data": data_m.strftime('%d/%m/%Y'), 
            "Mes_Ano": data_m.strftime('%m/%Y'),
            "Local": trecho_m, 
            "ODM_Zarpe_Ida": res_i['saida'],
            "Plano_H_Ida": res_i['t_hor'], 
            "Queima_Ida": res_i['queima'],
            "Plano_H_Volta": res_v['t_hor'], 
            "Queima_Volta": res_v['queima'],
            "H_Mano_Ida": res_i['h_mano'], 
            "H_Mano_Volta": res_v['h_mano'],
            "LH_Mano_Ida": res_i['lh_mano'], 
            "LH_Mano_Volta": res_v['lh_mano'],
            "H_MCA_Ida": res_i['h_mca'], 
            "H_MCA_Volta": res_v['h_mca'],
            "ODM_Fim_Final": res_v['chegada'] if res_v['t_hor'] > 0 else res_i['chegada']
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
        st.success("Salvo com sucesso no padrão BR!")
        st.rerun()
