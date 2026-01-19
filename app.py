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
# TELA: COMBUSTÍVEL (ESTILO ORIGINAL + FUNÇÃO EDITAR)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    
    # Criamos uma memória para saber qual linha estamos editando
    if 'index_edicao' not in st.session_state:
        st.session_state.index_edicao = None

    # Se clicou em editar, buscamos os valores antigos para preencher o formulário
    valores_padrao = {
        "emp": empurradores_lista[0], "data": datetime.now(), "saldo": 0.0, "qtd": 0.0, "valor": 0.0
    }
    
    if st.session_state.index_edicao is not None:
        linha = st.session_state.db_comb.iloc[st.session_state.index_edicao]
        valores_padrao["emp"] = linha['Empurrador']
        valores_padrao["valor"] = float(linha['Valor_Comb'])
        st.warning(f"⚠️ Você está EDITANDO a linha {st.session_state.index_edicao}. Altere os campos e salve.")

    # 1. SEU FORMULÁRIO ORIGINAL
    with st.form("form_comb"):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista, index=empurradores_lista.index(valores_padrao["emp"]))
            data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
            solicitante = st.text_input("SOLICITANTE", value="ALEX")
        with c2:
            saldo_ant = st.number_input("SALDO ANTERIOR (Litros)", min_value=0.0, step=1.0)
            qtd_sol = st.number_input("QTD. SOLICITADA (Litros)", min_value=0.0, step=1.0)
            total_t = saldo_ant + qtd_sol
            st.info(f"📊 TOTAL NO TANQUE: {total_t:,.2f} L")
        with c3:
            odm_z = st.number_input("ODM ZARPE", step=0.1)
            plano_h = st.number_input("PLANO HORAS", step=0.1)
            h_mca = st.number_input("H MCA", step=0.1)
        with c4:
            local = st.text_input("LOCAL / ORIGEM")
            valor_c = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0, value=valores_padrao["valor"])
            
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.form_submit_button("✅ Salvar / Atualizar"):
            data_br = data_sol.strftime('%d/%m/%Y')
            
            if st.session_state.index_edicao is not None:
                # ATUALIZA A LINHA EXISTENTE
                st.session_state.db_comb.at[st.session_state.index_edicao, 'Empurrador'] = emp
                st.session_state.db_comb.at[st.session_state.index_edicao, 'Data'] = data_br
                st.session_state.db_comb.at[st.session_state.index_edicao, 'Litros'] = total_t
                st.session_state.db_comb.at[st.session_state.index_edicao, 'Valor_Comb'] = valor_c
                st.session_state.index_edicao = None # Limpa a memória de edição
            else:
                # CRIA NOVA LINHA
                nova_l = pd.DataFrame([[emp, data_br, total_t, valor_c]], 
                                     columns=['Empurrador', 'Data', 'Litros', 'Valor_Comb'])
                st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
            
            st.success("Operação realizada com sucesso!")
            st.rerun()

    # 2. SUA TABELA COM O BOTÃO DE EDIÇÃO QUE VOCÊ PEDIU
    st.divider()
    st.subheader("📋 Registros de Abastecimento")
    if not st.session_state.db_comb.empty:
        st.dataframe(st.session_state.db_comb, use_container_width=True)
        
        c_ed, c_ex = st.columns(2)
        id_escolhido = c_ed.number_input("ID para editar ou excluir:", min_value=0, step=1)
        
        if c_ed.button("✏️ Carregar para Editar"):
            st.session_state.index_edicao = id_escolhido
            st.rerun()
            
        if c_ex.button("🗑️ Excluir Linha"):
            st.session_state.db_comb = st.session_state.db_comb.drop(id_escolhido).reset_index(drop=True)
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
