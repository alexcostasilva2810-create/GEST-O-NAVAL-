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
# TELA: COMBUSTÍVEL (ESTILO PLANILHA COM CHECKBOX)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    # 1. CÁLCULOS AUTOMÁTICOS DURANTE A DIGITAÇÃO
    st.subheader("📝 Lançamento e Edição")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista)
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
        origem = st.text_input("ORIGEM")
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0)
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0)
        # SOMA AUTOMÁTICA
        total_t = saldo_ant + qtd_sol
        st.info(f"📊 TOTAL NO TANQUE: {total_t:,.2f} L")
        odm_z = st.number_input("ODM ZARPE", value=0.0, step=0.1)
    with col3:
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
        lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)
    with col4:
        h_mca = st.number_input("H MCA", value=0.0, step=0.1)
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
        
        # FÓRMULA DO EXCEL AUTOMÁTICA
        # ODM FIM = G - (H*I) - (J*K) - (L*7) - M
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        st.error(f"📉 ODM FINAL: {odm_fim:,.2f}")
        
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)

    # BOTÕES DE SALVAR
    c_save, c_clear = st.columns(2)
    if c_save.button("✅ SALVAR LANÇAMENTO / EDIÇÃO", use_container_width=True, type="primary"):
        nova_linha = pd.DataFrame([{
            "SEL": False, "ID": len(st.session_state.db_comb), "Empurrador": emp, 
            "Data": data_sol.strftime('%d/%m/%Y'), "Litros": total_t, 
            "ODM_Fim": odm_fim, "Valor_NF": valor_nf
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
        st.rerun()

    # 2. TABELA COM O QUADRADO (CHECKBOX) PARA MARCAR
    st.divider()
    st.subheader("📋 Histórico de Lançamentos")
    st.write("Marque o quadrado na coluna **'SEL'** para selecionar a linha:")

    if not st.session_state.db_comb.empty:
        # data_editor cria os quadradinhos (checkbox) automaticamente para colunas Booleanas
        tabela_editavel = st.data_editor(
            st.session_state.db_comb,
            column_config={
                "SEL": st.column_config.CheckboxColumn("SEL", help="Marque para selecionar", default=False),
            },
            disabled=["ID", "Empurrador", "Data", "Litros", "ODM_Fim", "Valor_NF"],
            hide_index=True,
            use_container_width=True
        )

        # Lógica para identificar qual linha foi marcada com o X
        linhas_marcadas = tabela_editavel[tabela_editavel["SEL"] == True]

        if not linhas_marcadas.empty:
            idx_selecionado = linhas_marcadas.index[0]
            st.warning(f"📍 Linha {idx_selecionado} marcada no quadrado!")
            
            b_ed, b_ex = st.columns(2)
            if b_ed.button("✏️ Carregar para Corrigir"):
                # Aqui você faria a lógica de carregar nos campos
                st.info("Dados prontos para edição no formulário acima.")
            
            if b_ex.button("🗑️ Excluir Linha Marcada"):
                st.session_state.db_comb = st.session_state.db_comb.drop(idx_selecionado).reset_index(drop=True)
                # Reorganiza os IDs
                st.session_state.db_comb['ID'] = st.session_state.db_comb.index
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
