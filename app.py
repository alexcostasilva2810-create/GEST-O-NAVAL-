import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

# Inicialização de dados (Enquanto não conectamos com o Google Sheets)
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Litros', 'Valor'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Valor'])

st.sidebar.title("🚢 Menu Principal")
aba = st.sidebar.radio("Selecione:", ["⛽ Combustível", "🍱 Rancho", "📊 Relatórios & Dashboard"])

empurradores = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

# --- TELA DE COMBUSTÍVEL (TODAS AS COLUNAS) ---
if aba == "⛽ Combustível":
    st.header("Gestão de Combustível")
    with st.form("form_comb"):
        c1, c2, c3 = st.columns(3)
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores)
            data_sol = st.date_input("DATA SOLICITAÇÃO")
            solicitante = st.text_input("SOLICITANTE")
            mes_ref = st.selectbox("MÊS DE REFERÊNCIA", ["Janeiro", "Fevereiro", "Março"])
        with c2:
            odm_z = st.number_input("ODM ZARPE", step=0.1)
            litros = st.number_input("LITROS TOTAL", min_value=0.0)
            valor_c = st.number_input("VALOR TOTAL R$ (Combustível)", min_value=0.0)
        with c3:
            local = st.text_input("LOCAL/FILIAL")
            nf = st.text_input("NF ID SC")
        
        if st.form_submit_button("Salvar Abastecimento"):
            novo = pd.DataFrame([[emp, mes_ref, litros, valor_c]], columns=['Empurrador', 'Mês', 'Litros', 'Valor'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, novo])
            st.success("Abastecimento salvo com sucesso!")

# --- TELA DE RANCHO ---
elif aba == "🍱 Rancho":
    st.header("Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores)
            mes_r = st.selectbox("MÊS", ["Janeiro", "Fevereiro", "Março"])
        with r2:
            valor_r = st.number_input("VALOR TOTAL RANCHO R$", min_value=0.0)
            
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, mes_r, valor_r]], columns=['Empurrador', 'Mês', 'Valor'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r])
            st.success("Rancho salvo com sucesso!")

# --- TELA DE INTEGRAÇÃO E DASHBOARD (A QUE VOCÊ PRECISA) ---
elif aba == "📊 Relatórios & Dashboard":
    st.header("📈 Integração e Indicadores por Empurrador")
    
    mes_filtro = st.selectbox("Selecione o Mês para Análise", ["Janeiro", "Fevereiro", "Março"])
    
    # Processamento dos Dados
    resumo_lista = []
    for e in empurradores:
        # Filtra combustível
        df_c = st.session_state.db_comb[(st.session_state.db_comb['Empurrador'] == e) & (st.session_state.db_comb['Mês'] == mes_filtro)]
        total_lts = df_c['Litros'].sum()
        gasto_c = df_c['Valor'].sum()
        qtd_abast = len(df_c)
        
        # Filtra rancho
        df_ran = st.session_state.db_rancho[(st.session_state.db_rancho['Empurrador'] == e) & (st.session_state.db_rancho['Mês'] == mes_filtro)]
        gasto_r = df_ran['Valor'].sum()
        qtd_ran = len(df_ran)
        
        resumo_lista.append({
            "Empurrador": e,
            "Abastecimentos": qtd_abast,
            "Total Litros": total_lts,
            "Gasto Combustível (R$)": gasto_c,
            "Ranchos Realizados": qtd_ran,
            "Gasto Rancho (R$)": gasto_r,
            "INVESTIMENTO TOTAL": gasto_c + gasto_r
        })
    
    df_final = pd.DataFrame(resumo_lista)
    
    # Tabela Completa
    st.subheader(f"Relatório de Atividades - {mes_filtro}")
    st.dataframe(df_final, use_container_width=True)
    
    st.divider()
    
    # Dashboard Visual
    col_gr1, col_gr2 = st.columns(2)
    
    with col_gr1:
        st.write("📊 **Gasto Total por Empurrador**")
        fig_bar = px.bar(df_final, x="Empurrador", y="INVESTIMENTO TOTAL", color="Empurrador", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with col_gr2:
        st.write("🍕 **Proporção de Custos (Geral)**")
        total_c = df_final['Gasto Combustível (R$)'].sum()
        total_r = df_final['Gasto Rancho (R$)'].sum()
        fig_pie = px.pie(values=[total_c, total_r], names=['Combustível', 'Rancho'], hole=.3)
        st.plotly_chart(fig_pie, use_container_width=True)
