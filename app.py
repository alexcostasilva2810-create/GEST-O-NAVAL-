import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

#----------------------------------#
# CONFIGURAÇÕES E LISTA DE NAVIOS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

# Estilo Alerta
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

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['Empurrador', 'Mês', 'Data', 'Litros', 'Valor_Comb'])
if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🍱 Rancho", "📊 Dashboard & Relatórios"])

#----------------------------------#
# TELA: COMBUSTÍVEL (EDIÇÃO COMPATÍVEL)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    
    # Criamos um espaço para o formulário
    container_form = st.container()

    # 1. TABELA DE REGISTROS (Aparece primeiro para você ver o que quer editar)
    st.subheader("📋 Histórico de Lançamentos")
    if not st.session_state.db_comb.empty:
        st.dataframe(st.session_state.db_comb, use_container_width=True)
        
        # ÁREA DE AÇÃO: Editar ou Excluir
        c_edit, c_excluir = st.columns(2)
        
        with c_edit:
            idx_para_editar = st.number_input("Digite o ID da linha para ADICIONAR NOTA FISCAL:", min_value=0, step=1)
            novo_valor_nf = st.number_input("Novo Valor da Nota Fiscal (R$):", min_value=0.0)
            if st.button("💾 Atualizar Valor da Nota"):
                # Atualiza apenas a coluna de Valor na linha escolhida
                st.session_state.db_comb.at[idx_para_editar, 'Valor_Comb'] = novo_valor_nf
                st.success(f"✅ Valor atualizado na linha {idx_para_editar}!")
                st.rerun()

        with c_excluir:
            idx_remover = st.number_input("Digite o ID para REMOVER lançamento:", min_value=0, step=1)
            if st.button("🗑️ Excluir permanentemente"):
                st.session_state.db_comb = st.session_state.db_comb.drop(idx_remover).reset_index(drop=True)
                st.rerun()
    else:
        st.info("Nenhum registro para exibir.")

    st.divider()

    # 2. FORMULÁRIO DE NOVO LANÇAMENTO (Fica embaixo agora)
    with container_form.form("form_novo_comb"):
        st.subheader("➕ Novo Lançamento Operacional")
        f1, f2, f3 = st.columns(3)
        with f1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista)
            data_sol = st.date_input("DATA", format="DD/MM/YYYY")
        with f2:
            s_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0)
            q_sol = st.number_input("QTD SOLICITADA (L)", min_value=0.0)
        with f3:
            odm = st.number_input("ODM ZARPE", step=0.1)
            # Valor da nota começa em 0 se não tiver ainda
            val_nf_inicial = st.number_input("VALOR NF (Deixe 0 se não tiver)", min_value=0.0)
            
        if st.form_submit_button("✅ Salvar Novo"):
            total_l = s_ant + q_sol
            nova_l = pd.DataFrame([[emp, data_sol.strftime('%d/%m/%Y'), total_l, val_nf_inicial]], 
                                 columns=['Empurrador', 'Data', 'Litros', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
            st.success("Lançado!")
            st.rerun()

#----------------------------------#
# TELA: RANCHO
#----------------------------------#
elif aba == "🍱 Rancho":
    st.header("🍱 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores_lista)
            data_ent = st.date_input("DATA ENTREGA", format="DD/MM/YYYY") # DATA BR
        with r2:
            dias_val = st.number_input("DURAÇÃO (DIAS)", min_value=1, value=15)
            valor_ran = st.number_input("VALOR TOTAL R$", min_value=0.0)
        
        prox_rancho = data_ent + timedelta(days=dias_val)
        
        if st.form_submit_button("Salvar Rancho"):
            novo_r = pd.DataFrame([[emp_r, "Janeiro", prox_rancho, valor_ran]], 
                                  columns=['Empurrador', 'Mês', 'Proximo_Rancho', 'Valor_Rancho'])
            st.session_state.db_rancho = pd.concat([st.session_state.db_rancho, novo_r], ignore_index=True)
            st.success(f"Próximo rancho para {emp_r} em: {prox_rancho.strftime('%d/%m/%Y')}")

#----------------------------------#
# DASHBOARD
#----------------------------------#
elif aba == "📊 Dashboard & Relatórios":
    st.header("📊 Relatórios Consolidados")
    
    # Alerta de 5 dias
    hoje = datetime.now().date()
    for _, row in st.session_state.db_rancho.iterrows():
        dias = (row['Proximo_Rancho'] - hoje).days
        if 0 <= dias <= 5:
            st.markdown(f'<div class="alerta-piscante">⚠️ ATENÇÃO: Rancho do {row["Empurrador"]} vence em {dias} dias!</div>', unsafe_allow_html=True)
            
    st.write("Tabela de Custos Integrados:")
    st.dataframe(st.session_state.db_comb, use_container_width=True)
