import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

#----------------------------------#
# LISTA OFICIAL DE EMPURRADORES
#----------------------------------#
empurradores_lista = [
    "ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", 
    "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", 
    "QUARUBA", "TIMBORANA", "JATOBA"
]

#----------------------------------#
# BANCO DE DADOS (MEMÓRIA)
#----------------------------------#
if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame(columns=['SEL', 'ID', 'Empurrador', 'Data', 'Litros', 'ODM_Fim', 'Valor_NF'])

if 'db_rancho' not in st.session_state:
    st.session_state.db_rancho = pd.DataFrame(columns=['ID', 'Empurrador', 'Data', 'Tipo', 'Valor'])

#----------------------------------#
# BARRA LATERAL (MENU)
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Combustível", "🛒 Rancho", "📊 Dashboard"])

#----------------------------------#
# TELA: COMBUSTÍVEL (EDIÇÃO DIRETA NA TABELA)
#----------------------------------#
if aba == "⛽ Combustível":
    st.header("⛽ Gestão de Combustível")

    st.subheader("📝 Lançamento")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        emp = st.selectbox("EMPURRADOR", empurradores_lista)
        data_sol = st.date_input("DATA SOLICITAÇÃO", format="DD/MM/YYYY")
        solicitante = st.text_input("SOLICITANTE", value="ALEX")
        origem = st.text_input("ORIGEM")
        
    with col2:
        saldo_ant = st.number_input("SALDO ANTERIOR (L)", min_value=0.0, step=1.0)
        qtd_sol = st.number_input("QTD. SOLICITADA (L)", min_value=0.0, step=1.0)
        odm_z = saldo_ant + qtd_sol # SOMA AUTOMÁTICA
        st.success(f"⚓ ODM ZARPE (SOMA): {odm_z:,.2f} L")
        
    with col3:
        plano_h = st.number_input("PLANO HORAS", value=0.0, step=0.1)
        lh_rpm = st.number_input("L/H RPM", value=0.0, step=0.1)
        h_manobra = st.number_input("H. MANOBRA", value=0.0, step=0.1)
        lh_manobra = st.number_input("L/H MANOBRA", value=0.0, step=0.1)
        
    with col4:
        h_mca = st.number_input("H MCA", value=0.0, step=0.1)
        transf_balsa = st.number_input("TRANSF. BALSA", value=0.0, step=0.1)
        odm_fim = odm_z - (plano_h * lh_rpm) - (h_manobra * lh_manobra) - (h_mca * 7) - transf_balsa
        st.error(f"📉 ODM FINAL: {odm_fim:,.2f}")
        valor_nf = st.number_input("VALOR TOTAL R$ (Nota Fiscal)", min_value=0.0)
        local = st.text_input("LOCAL")

    # BOTÃO SALVAR NOVO
    if st.button("✅ SALVAR NOVO REGISTRO", use_container_width=True, type="primary"):
        nova_l = pd.DataFrame([{
            "SEL": False, "Empurrador": emp, "Data": data_sol.strftime('%d/%m/%Y'), 
            "Saldo_Ant": saldo_ant, "Qtd_Sol": qtd_sol, "ODM_Zarpe": odm_z,
            "Plano_H": plano_h, "LH_RPM": lh_rpm, "H_Manobra": h_manobra,
            "LH_Manobra": lh_manobra, "H_MCA": h_mca, "Transf": transf_balsa,
            "ODM_Fim": odm_fim, "Valor_NF": valor_nf, "Local": local
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    #----------------------------------#
    # TABELA COM TODAS AS COLUNAS E EDIÇÃO AO MARCAR
    #----------------------------------#
    st.divider()
    st.subheader("📋 Tabela de Registros (Marque SEL para editar a linha)")

    if not st.session_state.db_comb.empty:
        # Definimos quais colunas ficam travadas e quais liberam quando marcar
        # Se SEL for falso, tudo fica travado. Se SEL for verdadeiro, libera.
        
        # Criamos a tabela interativa
        # O segredo aqui é que o st.data_editor salva automaticamente ao desmarcar
        tabela_editada = st.data_editor(
            st.session_state.db_comb,
            use_container_width=True,
            hide_index=True,
            column_config={
                "SEL": st.column_config.CheckboxColumn("SEL", default=False),
                "Valor_NF": st.column_config.NumberColumn("Valor R$", format="R$ %.2f"),
                "ODM_Fim": st.column_config.NumberColumn("ODM Final", disabled=True)
            },
            key="editor_direto"
        )

        # Se houver mudança na tabela (ao desmarcar o SEL), atualizamos o banco
        if not tabela_editada.equals(st.session_state.db_comb):
            st.session_state.db_comb = tabela_editada
            st.toast("Alteração salva automaticamente!", icon="💾")
            
        # Botão para excluir caso precise
        if st.button("🗑️ Excluir Linhas Marcadas"):
            st.session_state.db_comb = st.session_state.db_comb[st.session_state.db_comb["SEL"] == False]
            st.rerun()
    else:
        st.info("Aguardando lançamentos...")

    #----------------------------------#
    # BLOCO: BOTÃO SALVAR
    #----------------------------------#
    if st.button("✅ SALVAR REGISTRO", use_container_width=True, type="primary"):
        nova_l = pd.DataFrame([{
            "SEL": False, 
            "ID": len(st.session_state.db_comb), 
            "Empurrador": emp, 
            "Data": data_sol.strftime('%d/%m/%Y'), 
            "Litros": odm_z, # Aqui salvamos a soma (Zarpe)
            "ODM_Fim": odm_fim, 
            "Valor_NF": valor_nf
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_l], ignore_index=True)
        st.rerun()

    #----------------------------------#
    # BLOCO: TABELA COM SEL (QUADRADO)
    #----------------------------------#
    st.divider()
    if not st.session_state.db_comb.empty:
        tabela_editavel = st.data_editor(
            st.session_state.db_comb,
            column_config={"SEL": st.column_config.CheckboxColumn("SEL", default=False)},
            disabled=["ID", "Empurrador", "Data", "Litros", "ODM_Fim", "Valor_NF"],
            hide_index=True, use_container_width=True, key="editor_comb"
        )

#----------------------------------#
# TELA: RANCHO (MANTIDA)
#----------------------------------#
elif aba == "🛒 Rancho":
    st.header("🛒 Gestão de Rancho")
    with st.form("form_rancho"):
        r1, r2 = st.columns(2)
        with r1:
            emp_r = st.selectbox("EMPURRADOR", empurradores_lista)
            data_r = st.date_input("DATA PEDIDO")
        with r2:
            tipo_r = st.selectbox("TIPO", ["Rancho Mensal", "Complemento"])
            valor_r = st.number_input("VALOR R$", min_value=0.0)
        if st.form_submit_button("✅ Salvar"):
            st.success("Pedido de Rancho Salvo!")
