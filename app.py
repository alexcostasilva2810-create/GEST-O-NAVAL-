import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS E LISTA
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

#----------------------------------#
# BANCO DE DADOS (MEMÓRIA)
#----------------------------------#
if 'db_comb' not in st.session_state or 'SEL' not in st.session_state.db_comb.columns:
    st.session_state.db_comb = pd.DataFrame(columns=['SEL', 'ID', 'Empurrador', 'Data', 'Litros', 'ODM_Fim', 'Valor_NF'])

#----------------------------------#
# BARRA LATERAL (MENU)
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "📊 Dashboard"])

#----------------------------------#
# TELA: COMBUSTÍVEL
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    #----------------------------------#
    # BLOCO: ENTRADA E CÁLCULOS AUTOMÁTICOS
    #----------------------------------#
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
        
        # CÁLCULO DE SOMA AUTOMÁTICO
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
        
        # FÓRMULA DO EXCEL (ODM FIM AUTOMÁTICO)
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        
        st.error(f"📉 ODM FINAL CALCULADO: {odm_fim:,.2f}")
        
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
        local = st.text_input("LOCAL")

    #----------------------------------#
    # BLOCO: BOTÃO SALVAR
    #----------------------------------#
    if st.button("✅ SALVAR NOVO REGISTRO", use_container_width=True, type="primary"):
        nova_l = pd.DataFrame([{
            "SEL": False, 
            "ID": len(st.session_state.db_comb), 
            "Empurrador": emp, 
            "Data": data_sol.strftime('%d/%m/%Y'), 
            "Litros": total_t, 
            "ODM_Fim": odm_fim, 
            "Valor_NF": valor_nf
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    #----------------------------------#
    # BLOCO: TABELA COM QUADRADO (SEL)
    #----------------------------------#
    st.divider()
    st.subheader("📋 Tabela de Registros")
    st.write("Marque o quadrado **SEL** para selecionar a linha:")

    if not st.session_state.db_comb.empty:
        tabela_editavel = st.data_editor(
            st.session_state.db_comb,
            column_config={
                "SEL": st.column_config.CheckboxColumn("SEL", default=False),
            },
            disabled=["ID", "Empurrador", "Data", "Litros", "ODM_Fim", "Valor_NF"],
            hide_index=True,
            use_container_width=True,
            key="editor_comb"
        )

        # Lógica para Editar/Excluir a linha marcada
        linhas_sel = tabela_editavel[tabela_editavel["SEL"] == True]

        if not linhas_sel.empty:
            idx = linhas_sel.index[0]
            st.warning(f"📍 Linha {idx} selecionada no quadrado.")
            
            c_ed, c_ex = st.columns(2)
            if c_ed.button("✏️ Carregar para Editar"):
                # Função para carregar os dados
                st.info("Dados prontos para edição nos campos acima.")
            
            if c_ex.button("🗑️ Excluir Linha Marcada"):
                st.session_state.db_comb = st.session_state.db_comb.drop(idx).reset_index(drop=True)
                st.session_state.db_comb['ID'] = st.session_state.db_comb.index
                st.rerun()
    else:
        st.info("Aguardando lançamentos...")

#----------------------------------#
# TELA: DASHBOARD (OPCIONAL)
#----------------------------------#
elif aba == "📊 Dashboard":
    st.header("📊 Resumo de Dados")
    st.write("Em desenvolvimento...")
