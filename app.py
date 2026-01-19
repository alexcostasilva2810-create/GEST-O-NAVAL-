import streamlit as st
import pandas as pd
import requests
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES DO NOTION
#----------------------------------#
NOTION_TOKEN = "ntn_uK635337593B2E2IGk4djZWXXf16GNziJUqcuyj8SH79Iq"
DATABASE_ID = "2ed025de7b79804eace0e1e80a186a49"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def enviar_ao_notion(dados):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Nome do Empurrador.": {"title": [{"text": {"content": dados['Empurrador']}}]},
            "Data": {"rich_text": [{"text": {"content": dados['Data']}}]},
            "Trecho": {"rich_text": [{"text": {"content": dados['Local']}}]},
            "Saldo Odm": {"number": dados['ODM_Zarpe_Ida']},
            "Plano Horas": {"number": dados['Plano_Total']},
            "L/H RPM": {"number": dados['LH_Ponderado']},
            "ODM FIM": {"number": dados['ODM_Fim_Final']}
        }
    }
    return requests.post(url, json=payload, headers=headers)

#----------------------------------#
# CONFIGURAÇÕES INICIAIS STREAMLIT
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
# BLOCO 1 - ABASTECIMENTO (VISUALIZAÇÃO)
#---------------------------------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Controle de Abastecimento")
    if not st.session_state.db_comb.empty:
        df_display = []
        for index, row in st.session_state.db_comb.iterrows():
            trecho = str(row.get('Local', '')).upper()
            origem_auto, destino_auto = (trecho.split('X', 1) + [""])[:2] if 'X' in trecho else (trecho, "")
            h_total = row.get('Plano_H_Ida', 0) + row.get('Plano_H_Volta', 0)
            lh_rpm_calc = (row['Plano_H_Ida'] * row['Queima_Ida'] + row['Plano_H_Volta'] * row['Queima_Volta']) / h_total if h_total > 0 else row.get('Queima_Ida', 0)

            df_display.append({
                "EDITAR": False,
                "ID": 1001 + index,
                "DATA SOLICITAÇÃO": row.get('Data', ''),
                "DATA ENTREGA": row.get('Data_Entrega', ''),
                "EMPURRADOR": row.get('Empurrador', ''),
                "CICLO": row.get('Ciclo', ''),
                "ORIGEM": origem_auto.strip(),
                "DESTINO": destino_auto.strip(),
                "LOCAL ABAST.": row.get('Local_Abast', ''),
                "ODM ZARPE": row.get('ODM_Zarpe_Ida', 0),
                "PLANO HORAS": h_total,
                "L/H RPM": round(lh_rpm_calc, 2),
                "ODM FIM": row.get('ODM_Fim_Final', 0)
            })

        st.data_editor(pd.DataFrame(df_display), use_container_width=True, hide_index=True)
    else:
        st.info("Aguardando lançamentos no Cálculo de Memória...")

#---------------------------------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (COM ENVIO NOTION)
#---------------------------------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria (Ida e Volta)")
    
    i1, i2, i3 = st.columns(3)
    with i1: emp_m = st.selectbox("EMPURRADOR", empurradores_lista)
    with i2: data_m = st.date_input("DATA DA VIAGEM", format="DD/MM/YYYY")
    with i3: trecho_m = st.text_input("TRECHO / SERVIÇO (Ex: MANAUS X BELEM)")

    st.divider()
    col_ida, col_volta = st.columns(2)

    def entrada_dados(prefixo):
        st.subheader(f"📍 {prefixo}")
        s_odm = st.number_input(f"SALDO DE ODM ({prefixo})", value=0.0, key=f"s_{prefixo}")
        o_comp = st.number_input(f"ODM COMPRA ({prefixo})", value=0.0, key=f"c_{prefixo}")
        t_hor = st.number_input(f"TOTAL PLANO DE HORAS ({prefixo})", value=0.0, key=f"h_{prefixo}")
        queima = st.number_input(f"QUEIMA L/H ({prefixo})", value=0.0, key=f"q_{prefixo}")
        h_mca = st.number_input(f"HORAS DE MCA ({prefixo})", value=0.0, key=f"mca_{prefixo}")
        lts_mca = st.number_input(f"LTS QUEIMA MCA ({prefixo})", value=7.0, key=f"l_{prefixo}")
        h_mano = st.number_input(f"HORA DE MANOBRA ({prefixo})", value=0.0, key=f"hm_{prefixo}")
        lh_mano = st.number_input(f"L/H MANOBRA ({prefixo})", value=0.0, key=f"lhm_{prefixo}")
        transf = st.number_input(f"TRANSFERÊNCIA BT ({prefixo})", value=0.0, key=f"t_{prefixo}")
        
        saida = s_odm + o_comp
        cons = (t_hor * queima) + (h_mca * lts_mca) + (h_mano * lh_mano)
        chegada = saida - cons - transf
        st.write(f"**ODM SAÍDA:** {saida:,.2f} | **CHEGADA:** {chegada:,.2f}")
        return {"saida": saida, "chegada": chegada, "t_hor": t_hor, "queima": queima}

    with col_ida: res_i = entrada_dados("IDA")
    with col_volta: res_v = entrada_dados("VOLTA")

    if st.button("💾 FINALIZAR E SALVAR (ENVIAR PARA NOTION)", use_container_width=True, type="primary"):
        # Cálculo da Média Ponderada para o Notion
        h_total = res_i['t_hor'] + res_v['t_hor']
        lh_ponderado = ((res_i['t_hor'] * res_i['queima']) + (res_v['t_hor'] * res_v['queima'])) / h_total if h_total > 0 else res_i['queima']
        odm_final = res_v['chegada'] if res_v['t_hor'] > 0 else res_i['chegada']

        # 1. Dados para o Session State (Seu banco atual)
        nova_linha_data = {
            "Empurrador": emp_m, "Data": data_m.strftime('%d/%m/%Y'), "Local": trecho_m,
            "ODM_Zarpe_Ida": res_i['saida'], "Plano_H_Ida": res_i['t_hor'], "Queima_Ida": res_i['queima'],
            "Plano_H_Volta": res_v['t_hor'], "Queima_Volta": res_v['queima'], "ODM_Fim_Final": odm_final
        }
        
        # 2. Envio para o Notion
        with st.spinner("Enviando dados para o Notion..."):
            dados_notion = {
                "Empurrador": emp_m, "Data": data_m.strftime('%d/%m/%Y'), "Local": trecho_m,
                "ODM_Zarpe_Ida": res_i['saida'], "Plano_Total": h_total,
                "LH_Ponderado": round(lh_ponderado, 2), "ODM_Fim_Final": odm_final
            }
            res_notion = enviar_ao_notion(dados_notion)

        if res_notion.status_code == 200:
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, pd.DataFrame([nova_linha_data])], ignore_index=True)
            st.success("Salvo localmente e enviado ao Notion!")
            st.rerun()
        else:
            st.error(f"Erro ao enviar para Notion: {res_notion.status_code} - {res_notion.text}")
