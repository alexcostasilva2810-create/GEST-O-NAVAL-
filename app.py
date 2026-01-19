import streamlit as st
import pandas as pd
import plotly.express as px

# Simulando dados (Em breve conectaremos com sua planilha oficial)
# Aqui o sistema vai ler tudo o que você salvou
if 'dados_combustivel' not in st.session_state:
    st.session_state.dados_combustivel = pd.DataFrame(columns=['EMPURRADOR', 'MES', 'LITROS', 'TOTAL_RS'])
if 'dados_rancho' not in st.session_state:
    st.session_state.dados_rancho = pd.DataFrame(columns=['EMPURRADOR', 'MES', 'TOTAL_RS'])

st.sidebar.title("Navegação")
aba = st.sidebar.radio("Ir para:", ["Combustível", "Rancho", "Relatório Geral", "Dashboard"])

# --- ABA RELATÓRIO GERAL ---
if aba == "Relatório Geral":
    st.header("📋 Relatório Consolidado por Empurrador")
    
    emp_filtro = st.selectbox("Selecione o Empurrador para análise", ["Todos"] + ["EMPURRADOR 01", "EMPURRADOR 02"])
    mes_filtro = st.selectbox("Mês de Competência", ["Janeiro", "Fevereiro", "Março"])

    # Tabela resumo que você pediu
    st.subheader(f"Resumo de Gastos - {mes_filtro}")
    
    # Exemplo de como a tabela aparecerá:
    data_exemplo = {
        'Empurrador': ['EMPURRADOR 01'],
        'Qtd Abastecimentos': [4],
        'Total Litros': [12500],
        'Gasto Combustível (R$)': [75000.00],
        'Qtd Ranchos': [2],
        'Gasto Rancho (R$)': [4200.00],
        'Custo Total (R$)': [79200.00]
    }
    df_resumo = pd.DataFrame(data_exemplo)
    st.table(df_resumo)

# --- ABA DASHBOARD ---
elif aba == "Dashboard":
    st.header("📊 Dashboard de Indicadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Custos Totais por Categoria")
        # Gráfico de Pizza que você pediu
        fig_pizza = px.pie(values=[75000, 4200], names=['Combustível', 'Rancho'], title="Distribuição de Gastos")
        st.plotly_chart(fig_pizza)
        
    with col2:
        st.subheader("Consumo de Litros por Empurrador")
        # Gráfico de Barras que você pediu
        fig_barra = px.bar(x=["Emp 01", "Emp 02", "Emp 03"], y=[12000, 9500, 15000], title="Litros Comprados", labels={'x':'Empurrador', 'y':'Litros'})
        st.plotly_chart(fig_barra)
