import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão Naval", layout="wide")

# Lista de Empurradores (ID comum)
EMPURRADORES = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

st.sidebar.title("Navegação")
aba = st.sidebar.radio("Ir para:", ["Combustível", "Rancho", "Escolta"])

if aba == "Combustível":
    st.header("⛽ Gestão de Combustível")
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.selectbox("EMPURRADOR", EMPURRADORES)
            st.date_input("DATA SOLICITAÇÃO")
            st.text_input("SOLICITANTE")
            st.text_input("ORIGEM")
            st.text_input("DESTINO")
        with c2:
            st.number_input("ODM ZARPE")
            st.number_input("PLANO HORAS")
            st.number_input("L/H RPM")
            st.number_input("H. MANOBRA")
        with c3:
            st.number_input("L/H MANOBRA")
            st.number_input("H MCA")
            st.text_input("TRANSF. BALSA")
            st.number_input("ODM FIM")
        with c4:
            st.text_input("MÊS/ANO")
            st.text_input("BALSAS")
            st.text_input("LOCAL")
            st.number_input("LITROS")
            
        st.form_submit_button("Salvar Abastecimento")

elif aba == "Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            st.selectbox("EMPURRADOR", EMPURRADORES)
            st.text_input("ALERTA")
            st.text_input("COMPRADOR")
            st.text_input("SC")
            st.text_input("SOLICITANTE")
        with r2:
            st.date_input("DATA SOLICITAÇÃO")
            st.date_input("ENTREGA")
            st.number_input("DIAS PROXIMO", step=1)
            st.text_area("DESCRIÇÃO DO MATERIAL")
            
        st.form_submit_button("Salvar Rancho")
