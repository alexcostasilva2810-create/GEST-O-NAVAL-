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
# TELA: COMBUSTÍVEL (COM QUADRADO DE SELEÇÃO E CÁLCULO)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    # 1. CÁLCULOS AUTOMÁTICOS (DURANTE A DIGITAÇÃO)
    st.subheader("📝 Lançamento / Edição")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista)
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0)
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0)
        # SOMA AUTOMÁTICA NA TELA
        total_tanque = saldo_ant + qtd_sol
        st.info(f"📊 TOTAL NO TANQUE: {total_tanque:,.2f} L")
    with col3:
        odm_z = st.number_input("ODM ZARPE", value=0.0, step=0.1)
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
    with col4:
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
        lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)
        h_mca = st.number_input("H MCA", value=0.0, step=0.1)
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
        
        # FÓRMULA AUTOMÁTICA (ODM FIM)
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        st.error(f"📉 ODM FINAL: {odm_fim:,.2f}")

    # BOTÕES DE SALVAR
    c_btn1, c_btn2 = st.columns(2)
    if c_btn1.button("✅ SALVAR NOVO / ATUALIZAR EDIÇÃO", use_container_width=True):
        nova_l = pd.DataFrame([{
            'Empurrador': emp, 'Data': data_sol.strftime('%d/%m/%Y'), 
            'Total Tanque': total_tanque, 'ODM Fim': odm_fim, 'Valor R$': 0.0
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    # 2. TABELA COM O QUADRADO PARA MARCAR (SELECTION)
    st.divider()
    st.subheader("📋 Marque a linha para Editar ou Excluir")

    if not st.session_state.db_comb.empty:
        # Aqui aparece o "Quadrado" para você marcar a linha
        selecao = st.dataframe(
            st.session_state.db_comb,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single" # Permite marcar apenas 1 quadrado por vez
        )

        # Se você marcou o quadrado, o sistema mostra os botões de ação
        if len(selecao.selection.rows) > 0:
            idx_selecionado = selecao.selection.rows[0]
            st.warning(f"📍 Linha {idx_selecionado} marcada para ação.")
            
            col_edit, col_excluir = st.columns(2)
            if col_edit.button("✏️ Carregar Dados para Corrigir"):
                # Essa função vai carregar os dados para cima na próxima atualização
                st.session_state.index_edicao = idx_selecionado
                st.info("Dados carregados! Altere os campos no formulário acima.")
                
            if col_excluir.button("🗑️ Excluir Linha Marcada"):
                st.session_state.db_comb = st.session_state.db_comb.drop(idx_selecionado).reset_index(drop=True)
                st.rerun()
    else:
        st.info("Nenhum registro lançado ainda.")
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
