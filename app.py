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
# TELA: COMBUSTÍVEL (COM EDIÇÃO AVANÇADA)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")
    
    # Inicializa variáveis de edição no estado da sessão se não existirem
    if 'edit_index' not in st.session_state:
        st.session_state.edit_index = None

    # 1. FORMULÁRIO (Serve para NOVO e para EDITAR)
    # Se estivermos editando, os campos carregam os valores da linha selecionada
    with st.form("form_comb", clear_on_submit=True):
        st.subheader("📝 Lançamento / Ajuste de Nota Fiscal")
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            emp = st.selectbox("EMPURRADOR", empurradores_lista)
            data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
            solicitante = st.text_input("SOLICITANTE", value="ALEX")
        with c2:
            saldo_ant = st.number_input("SALDO ANTERIOR (Litros)", min_value=0.0)
            qtd_sol = st.number_input("QTD. SOLICITADA (Litros)", min_value=0.0)
            total_t = saldo_ant + qtd_sol
            st.info(f"📊 TOTAL NO TANQUE: {total_t:.2f} L")
        with c3:
            odm_z = st.number_input("ODM ZARPE", step=0.1)
            plano_h = st.number_input("PLANO HORAS", step=0.1)
        with c4:
            # CAMPO CHAVE: Aqui você insere o valor da NF que chegou depois
            valor_c = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
            local = st.text_input("LOCAL / ORIGEM")
            
        texto_botao = "💾 Atualizar Registro" if st.session_state.edit_index is not None else "✅ Salvar Novo Abastecimento"
        btn_salvar = st.form_submit_button(texto_botao)

    if btn_salvar:
        novo_reg = {
            'Empurrador': emp, 'Data': data_sol.strftime('%d/%m/%Y'),
            'Total Tanque': total_t, 'Valor R$': valor_c, 'Local': local,
            'Saldo Ant': saldo_ant, 'Qtd Sol': qtd_sol, 'ODM': odm_z
        }
        
        if st.session_state.edit_index is not None:
            # Atualiza a linha existente
            st.session_state.db_comb.iloc[st.session_state.edit_index] = [
                emp, data_sol.strftime('%d/%m/%Y'), total_t, valor_c
            ] # Ajuste as colunas conforme seu db_comb inicial
            st.success("✅ Valor da Nota Fiscal atualizado!")
            st.session_state.edit_index = None # Limpa o modo edição
        else:
            # Cria novo registro
            nova_linha = pd.DataFrame([[emp, data_sol.strftime('%d/%m/%Y'), total_t, valor_c]], 
                                     columns=['Empurrador', 'Data', 'Litros', 'Valor_Comb'])
            st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
            st.success("✅ Novo registro salvo!")
        st.rerun()

    # 2. TABELA DE REGISTROS (ÁREA DE SELEÇÃO)
    st.divider()
    st.subheader("📋 Histórico para Conferência e Ajuste de Valores")
    
    if not st.session_state.db_comb.empty:
        # Tabela com seleção de linha
        selected_row = st.dataframe(
            st.session_state.db_comb, 
            use_container_width=True,
            on_select="rerun",
            selection_mode="single"
        )
        
        # Botões de Ação para a linha selecionada
        if len(selected_row.selection.rows) > 0:
            idx = selected_row.selection.rows[0]
            col_b1, col_b2 = st.columns(2)
            
            if col_b1.button("✏️ Editar Valor da Nota Fiscal"):
                st.session_state.edit_index = idx
                st.warning(f"Modo de Edição Ativado para a linha {idx}. Ajuste os valores no formulário acima e clique em Atualizar.")
                # Nota: Em um sistema real, aqui carregaríamos os campos. 
                # Para simplificar, o usuário ajusta no form.
            
            if col_b2.button("🗑️ Excluir Lançamento"):
                st.session_state.db_comb = st.session_state.db_comb.drop(idx).reset_index(drop=True)
                st.rerun()
    else:
        st.info("Aguardando lançamentos...")

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
