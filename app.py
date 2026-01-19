import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

#----------------------------------#
# ESTILOS E ALERTAS (CSS)
#----------------------------------#
st.markdown("""
    <style>
    @keyframes blinker { 50% { opacity: 0; } }
    .alerta-piscante { 
        color: white; background-color: #FF0000; 
        padding: 15px; border-radius: 10px; 
        text-align: center; font-weight: bold;
        animation: blinker 1.5s linear infinite;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

#----------------------------------#
# BANCO DE DADOS TEMPORÁRIO
#----------------------------------#
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Data', 'Litros', 'Valor_Comb'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])

#----------------------------------#
# BARRA LATERAL (MENU)
#----------------------------------#
st.sidebar.title("🚢 MENU DE GESTÃO")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

empurradores = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

#----------------------------------#
# TELA: COMBUSTÍVEL
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores)
            data_sol = st.date_input("DATA SOLICITAÇÃO")
            solicitante = st.text_input("SOLICITANTE")
            origem = st.text_input("ORIGEM")
        with c2:
            odm_z = st.number_input("ODM ZARPE", step=0.1)
            plano_h = st.number_input("PLANO HORAS", step=0.1)
            lh_rpm = st.number_input("L/H RPM", step=0.1)
            h_manobra = st.number_input("H. MANOBRA", step=0.1)
        with c3:
            lh_manobra = st.number_input("L/H MANOBRA", step=0.1)
            h_mca = st.number_input("H MCA", step=0.1)
            transf = st.text_input("TRANSF. BALSA")
            odm_fim = st.number_input("ODM FIM", step=0.1)
        with c4:
            mes_ref = st.selectbox("MÊS/ANO", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
            balsas = st.text_input("BALSAS")
            local = st.text_input("LOCAL")
            litros = st.number_input("LITROS TOTAL", min_value=0.0)
            valor_c = st.number_input("VALOR TOTAL R$ (Diesel)", min_value=0.0)
            
        if st.form_submit_button("Salvar Abastecimento"):
            novo_c = pd.DataFrame([[emp, mes_ref, data_sol, litros, valor_c]], 
                                  columns=['Empurrador', 'Mês', 'Data', 'Litros', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, novo_c], ignore_index=True)
            st.success("Abastecimento salvo com sucesso!")

#----------------------------------#
# TELA: RANCHO
#----------------------------------#
elif aba == "🍱 Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores)
            comprador = st.text_input("COMPRADOR")
            sc = st.text_input("SC")
            data_ent = st.date_input("DATA ENTREGA")
        with r2:
            dias_val = st.number_input("DURAÇÃO ESTIMADA (DIAS)", min_value=1, value=15)
            valor_ran = st.number_input("VALOR TOTAL RANCHO R$", min_value=0.0)
            desc = st.text_area("DESCRIÇÃO")
        
        prox_rancho = data_ent + timedelta(days=dias_val)
        
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, data_ent.strftime('%B'), prox_rancho, valor_ran]], 
                                  columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r], ignore_index=True)
            st.success(f"Dados salvos! Próximo vencimento: {prox_rancho.strftime('%d/%m/%Y')}")

#----------------------------------#
# TELA: DASHBOARD E INTEGRAÇÃO
#----------------------------------#
elif aba == "📊 Dashboard & Relatórios":
    st.header("📊 Dashboard e Integração de Custos")
    
    # Lógica de Alerta Piscante (5 dias)
    hoje = datetime.now().date()
    for _, row in st.session_state.db_rancho.iterrows():
        dias = (row['Proximo_Rancho'] - hoje).days
        if 0 <= dias <= 5:
            st.markdown(f'<div class="alerta-piscante">⚠️ PROGRAMAR NOVO RANCHO: {row["Empurrador"]} vence em {row["Proximo_Rancho"].strftime("%d/%m/%Y")} ({dias} dias)!</div>', unsafe_allow_html=True)

    # Tabela de Integração Total
    resumo = []
    for e in empurradores:
        df_c = st.session_state.db_comb[st.session_state.db_comb['Empurrador'] == e]
        df_r = st.session_state.db_rancho[st.session_state.db_rancho['Empurrador'] == e]
        
        resumo.append({
            "Empurrador": e,
            "Qtd Abast.": len(df_c),
            "Litros": df_c['Litros'].sum(),
            "R$ Diesel": df_c['Valor_Comb'].sum(),
            "R$ Rancho": df_r['Valor_Rancho'].sum(),
            "INVESTIMENTO TOTAL": df_c['Valor_Comb'].sum() + df_r['Valor_Rancho'].sum()
        })
    
    df_res = pd.DataFrame(resumo)
    st.subheader("📋 Relatório Consolidado")
    st.dataframe(df_res, use_container_width=True)

    st.divider()

    # Gráficos
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_bar = px.bar(df_res, x="Empurrador", y="INVESTIMENTO TOTAL", title="Custo Total (Diesel + Rancho)", color="Empurrador", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)
    with col_g2:
        pizza_data = pd.DataFrame({
            'Item': ['Diesel', 'Rancho'], 
            'Val': [df_res['R$ Diesel'].sum(), df_res['R$ Rancho'].sum()]
        })
