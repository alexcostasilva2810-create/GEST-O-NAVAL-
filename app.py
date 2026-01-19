import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

# Simulação de Banco de Dados (Para o Dashboard funcionar agora)
# Nota: No próximo passo vamos conectar à sua planilha real
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Litros', 'Valor'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Valor'])

st.sidebar.title("🚢 Sistema Naval")
menu = st.sidebar.radio("Navegação", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

empurradores = ["EMPURRADOR 01", "EMPURRADOR 02", "EMPURRADOR 03"]

# --- TELAS DE LANÇAMENTO (Combustível e Rancho) ---
if menu == "⛽ Combustível":
    st.header("Gestão de Combustível")
    with st.form("form_comb"):
        c1, c2 = st.columns(2)
        emp = c1.selectbox("EMPURRADOR", empurradores)
        mes = c1.selectbox("MÊS", ["Janeiro", "Fevereiro", "Março"])
        litros = c2.number_input("LITROS", min_value=0.0)
        valor = c2.number_input("VALOR TOTAL R$", min_value=0.0)
        if st.form_submit_button("Salvar Abastecimento"):
            new_data = pd.DataFrame([[emp, mes, litros, valor]], columns=['Empurrador', 'Mês', 'Litros', 'Valor'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, new_data])
            st.success("Registrado!")

elif menu == "🍱 Rancho":
    st.header("Gestão de Rancho")
    with st.form("form_rancho"):
        c1, c2 = st.columns(2)
        emp = c1.selectbox("EMPURRADOR", empurradores)
        mes = c1.selectbox("MÊS", ["Janeiro", "Fevereiro", "Março"])
        valor = c2.number_input("VALOR TOTAL RANCHO R$", min_value=0.0)
        if st.form_submit_button("Salvar Rancho"):
            new_data = pd.DataFrame([[emp, mes, valor]], columns=['Empurrador', 'Mês', 'Valor'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, new_data])
            st.success("Registrado!")

# --- TELA DE INTEGRAÇÃO (A que você pediu) ---
elif menu == "📊 Dashboard & Relatórios":
    st.header("Integração Total de Gastos")
    
    # Filtro de Mês
    mes_sel = st.selectbox("Filtrar por Mês", ["Janeiro", "Fevereiro", "Março"])
    
    # Cálculos de Integração
    df_c = st.session_state.db_comb[st.session_state.db_comb['Mês'] == mes_sel]
    df_r = st.session_state.db_rancho[st.session_state.db_rancho['Mês'] == mes_sel]
    
    resumo = []
    for e in empurradores:
        lts = df_c[df_c['Empurrador'] == e]['Litros'].sum()
        v_comb = df_c[df_c['Empurrador'] == e]['Valor'].sum()
        v_rancho = df_r[df_r['Empurrador'] == e]['Valor'].sum()
        resumo.append([e, lts, v_comb, v_rancho, v_comb + v_rancho])
    
    df_final = pd.DataFrame(resumo, columns=['Empurrador', 'Total Litros', 'Gasto Combustível', 'Gasto Rancho', 'Gasto Total'])
    
    st.subheader(f"Tabela de Resumo - {mes_sel}")
    st.dataframe(df_final, use_container_width=True)
    
    st.divider()
    
    # Dashboard (Gráficos)
    col_dash1, col_dash2 = st.columns(2)
    with col_dash1:
        st.write("📊 **Gasto Total por Empurrador (R$)**")
        fig_barra = px.bar(df_final, x='Empurrador', y='Gasto Total', color='Empurrador')
        st.plotly_chart(fig_barra, use_container_width=True)
        
    with col_dash2:
        st.write("🍕 **Divisão de Custos (Combustível vs Rancho)**")
        pizza_data = pd.DataFrame({
            'Categoria': ['Combustível', 'Rancho'],
            'Valor': [df_final['Gasto Combustível'].sum(), df_final['Gasto Rancho'].sum()]
        })
        fig_pizza = px.pie(pizza_data, values='Valor', names='Categoria')
        st.plotly_chart(fig_pizza, use_container_width=True)
