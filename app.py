import streamlit as st
import pandas as pd
import requests
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES DO NOTION (DADOS DAS SUAS IMAGENS)
#----------------------------------#
# Token copiado da sua imagem image_31a663.png
NOTION_TOKEN = "ntn_uK635337593B2E2IGk4djZWXXf16GNziJUqcuyj8SH79Iq"

# ID extraído da sua imagem image_3036a4.png
DATABASE_ID = "2ed025de7b79804eace0e1e80a186a49"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def enviar_ao_notion(dados):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Nome do Empurrador.": {"title": [{"text": {"content": str(dados['Empurrador'])}}]},
            "Data": {"rich_text": [{"text": {"content": str(dados['Data'])}}]},
            "Trecho": {"rich_text": [{"text": {"content": str(dados['Local'])}}]},
            "Saldo Odm": {"number": float(dados['ODM_Zarpe_Ida'])},
            "Plano Horas": {"number": float(dados['Plano_Total'])},
            "L/H RPM": {"number": float(dados['LH_Ponderado'])},
            "ODM FIM": {"number": float(dados['ODM_Fim_Final'])}
        }
    }
    return requests.post(url, json=payload, headers=headers)

#----------------------------------#
# INTERFACE STREAMLIT
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame()

st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Calculo de mémoria"])

if aba == "⛽ Abastecimento":
    st.header("⛽ Controle de Abastecimento")
    st.dataframe(st.session_state.db_comb, use_container_width=True)

elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria")
    
    i1, i2, i3 = st.columns(3)
    with i1: emp_m = st.selectbox("EMPURRADOR", ["ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", "QUARUBA", "TIMBORANA", "JATOBA"])
    with i2: data_m = st.date_input("DATA DA VIAGEM", format="DD/MM/YYYY")
    with i3: trecho_m = st.text_input("TRECHO / SERVIÇO")

    st.divider()
    col_ida, col_volta = st.columns(2)

    def entrada_dados(prefixo):
        st.subheader(f"📍 {prefixo}")
        s_odm = st.number_input(f"SALDO DE ODM ({prefixo})", value=0.0, key=f"s_{prefixo}")
        t_hor = st.number_input(f"TOTAL HORAS ({prefixo})", value=0.0, key=f"h_{prefixo}")
        queima = st.number_input(f"QUEIMA L/H ({prefixo})", value=0.0, key=f"q_{prefixo}")
        saida = s_odm
        chegada = saida - (t_hor * queima)
        st.info(f"**ODM SAÍDA:** {saida:,.2f} | **CHEGADA:** {chegada:,.2f}")
        return {"saida": saida, "chegada": chegada, "t_hor": t_hor, "queima": queima}

    with col_ida: res_i = entrada_dados("IDA")
    with col_volta: res_v = entrada_dados("VOLTA")

    if st.button("💾 FINALIZAR E SALVAR (ENVIAR PARA NOTION)", use_container_width=True, type="primary"):
        h_total = res_i['t_hor'] + res_v['t_hor']
        lh_pond = ((res_i['t_hor'] * res_i['queima']) + (res_v['t_hor'] * res_v['queima'])) / h_total if h_total > 0 else 0
        odm_f = res_v['chegada'] if res_v['t_hor'] > 0 else res_i['chegada']

        dados_v = {
            "Empurrador": emp_m, "Data": data_m.strftime('%d/%m/%Y'), "Local": trecho_m.upper(),
            "ODM_Zarpe_Ida": res_i['saida'], "Plano_Total": h_total,
            "LH_Ponderado": round(lh_pond, 2), "ODM_Fim_Final": odm_f
        }
        
        with st.spinner("Enviando..."):
            res = enviar_ao_notion(dados_v)

        if res.status_code == 200:
            st.success("✅ SALVO COM SUCESSO!")
            st.balloons()
        else:
            st.error(f"Erro {res.status_code}: {res.text}")
