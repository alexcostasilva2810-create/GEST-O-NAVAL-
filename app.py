import streamlit as st
import pandas as pd
from datetime import datetime

#----------------------------------#
# CONFIGURAÇÕES INICIAIS
#----------------------------------#
st.set_page_config(page_title="Gestão Integrada Naval", layout="wide")

empurradores_lista = ["ANGELO", "ANGICO", "AROEIRA", "BRENO", "CANJERANA", "CUMARU", "IPE", "SAMAUMA", "JACARANDA", "LUIZ FELIPE", "QUARUBA", "TIMBORANA", "JATOBA"]

if 'db_comb' not in st.session_state:
    st.session_state.db_comb = pd.DataFrame()

#----------------------------------#
# MENU LATERAL
#----------------------------------#
st.sidebar.title("🚢 Menu de Gestão")
aba = st.sidebar.radio("Navegação", ["⛽ Abastecimento", "📝 Calculo de mémoria", "🛒 Rancho", "📊 Dashboard"])

#---------------------------------------------------------#
# BLOCO 1 - ABASTECIMENTO (COM TRAVA DE EDIÇÃO E SALVAMENTO)
#---------------------------------------------------------#
if aba == "⛽ Abastecimento":
    st.header("⛽ Controle de Abastecimento")
    st.caption("Selecione a linha na coluna 'EDITAR' para liberar o preenchimento manual.")
    
    if not st.session_state.db_comb.empty:
        # 1. PROCESSAMENTO DOS DADOS PARA EXIBIÇÃO
        df_display = []
        for index, row in st.session_state.db_comb.iterrows():
            # Lógica de Origem/Destino
            trecho = str(row.get('Local', '')).upper()
            origem_auto, destino_auto = (trecho.split('X', 1) + [""])[:2] if 'X' in trecho else (trecho, "")

            # Matemática Média Ponderada
            h_total = row.get('Plano_H_Ida', 0) + row.get('Plano_H_Volta', 0)
            if h_total > 0:
                lh_rpm_calc = (row['Plano_H_Ida'] * row['Queima_Ida'] + row['Plano_H_Volta'] * row['Queima_Volta']) / h_total
            else:
                lh_rpm_calc = row.get('Queima_Ida', 0)

            df_display.append({
                "EDITAR": False, # Checkbox para liberar edição
                "ID": 1001 + index,
                "DATA SOLICITAÇÃO": row.get('Data', ''),
                "DATA ENTREGA": row.get('Data_Entrega', ''), # Busca do banco
                "EMPURRADOR": row.get('Empurrador', ''),
                "CICLO": row.get('Ciclo', ''),               # Busca do banco
                "ORIGEM": origem_auto.strip(),
                "DESTINO": destino_auto.strip(),
                "LOCAL ABAST.": row.get('Local_Abast', ''), # Busca do banco
                "ODM ZARPE": row.get('ODM_Zarpe_Ida', 0),
                "ODM COMPRA": row.get('ODM_Compra_Ida', 0),
                "PLANO HORAS": h_total,
                "L/H RPM": round(lh_rpm_calc, 2),
                "H MCA": row.get('H_MCA_Ida', 0) + row.get('H_MCA_Volta', 0),
                "ODM FIM": row.get('ODM_Fim_Final', 0)
            })

        df_editor = pd.DataFrame(df_display)

        # 2. O EDITOR DE DADOS (Configurado para editar apenas campos manuais)
        # O usuário só consegue editar se marcar o checkbox 'EDITAR'
        editado = st.data_editor(
            df_editor,
            use_container_width=True,
            hide_index=True,
            column_config={
                "EDITAR": st.column_config.CheckboxColumn("EDITAR", help="Marque para editar esta linha"),
                "ID": st.column_config.Column(disabled=True),
                "DATA SOLICITAÇÃO": st.column_config.Column(disabled=True),
                "EMPURRADOR": st.column_config.Column(disabled=True),
                "ORIGEM": st.column_config.Column(disabled=True),
                "DESTINO": st.column_config.Column(disabled=True),
                "ODM ZARPE": st.column_config.Column(disabled=True),
                "ODM COMPRA": st.column_config.Column(disabled=True),
                "PLANO HORAS": st.column_config.Column(disabled=True),
                "L/H RPM": st.column_config.Column(disabled=True),
                "H MCA": st.column_config.Column(disabled=True),
                "ODM FIM": st.column_config.Column(disabled=True),
                # Campos liberados
                "DATA ENTREGA": st.column_config.TextColumn("DATA ENTREGA"),
                "LOCAL ABAST.": st.column_config.TextColumn("LOCAL ABAST."),
                "CICLO": st.column_config.TextColumn("CICLO"),
            },
            key="editor_abast_v3"
        )

        # 3. BOTÃO PARA GRAVAR ALTERAÇÕES
        col_btn1, col_btn2 = st.columns([1, 4])
        with col_btn1:
            if st.button("💾 Gravar Alterações", type="primary", use_container_width=True):
                # Atualiza o banco de dados original (session_state) com o que foi digitado
                for i, row_edit in editado.iterrows():
                    if row_edit["EDITAR"]: # Só atualiza se o checkbox estiver marcado
                        st.session_state.db_comb.at[i, 'Data_Entrega'] = row_edit['DATA ENTREGA']
                        st.session_state.db_comb.at[i, 'Local_Abast'] = row_edit['LOCAL ABAST.']
                        st.session_state.db_comb.at[i, 'Ciclo'] = row_edit['CICLO']
                
                st.success("Dados gravados com sucesso!")
                st.rerun()
        
        with col_btn2:
            if st.button("🗑️ Excluir Selecionados"):
                linhas_para_manter = [i for i, r in editado.iterrows() if not r["EDITAR"]]
                st.session_state.db_comb = st.session_state.db_comb.iloc[linhas_para_manter].reset_index(drop=True)
                st.rerun()

    else:
        st.info("Aguardando lançamentos no Cálculo de Memória...")
#---------------------------------------------------------#
# BLOCO 2 - CALCULO DE MÉMORIA (DATA BR NO CALENDÁRIO)
#---------------------------------------------------------#
elif aba == "📝 Calculo de mémoria":
    st.header("📝 Calculo de mémoria (Ida e Volta)")
    
    i1, i2, i3 = st.columns(3)
    with i1: 
        emp_m = st.selectbox("EMPURRADOR", empurradores_lista, key="v2_emp")
    with i2: 
        # Calendário configurado para formato Brasileiro
        data_m = st.date_input("DATA DA VIAGEM", format="DD/MM/YYYY", key="v2_data")
    with i3: 
        trecho_m = st.text_input("TRECHO / SERVIÇO (Ex: MANAUS X BELEM)", key="v2_trecho")

    st.divider()
    col_ida, col_volta = st.columns(2)

    def entrada_dados(prefixo):
        st.subheader(f"📍 {prefixo}")
        s_odm = st.number_input(f"SALDO DE ODM ({prefixo})", value=0.0, step=1.0, key=f"s_{prefixo}")
        o_comp = st.number_input(f"ODM COMPRA ({prefixo})", value=0.0, step=1.0, key=f"c_{prefixo}")
        t_hor = st.number_input(f"TOTAL PLANO DE HORAS ({prefixo})", value=0.0, step=0.1, key=f"h_{prefixo}")
        queima = st.number_input(f"QUEIMA L/H ({prefixo})", value=0.0, step=0.1, key=f"q_{prefixo}")
        h_mca = st.number_input(f"HORAS DE MCA ({prefixo})", value=0.0, step=0.1, key=f"mca_{prefixo}")
        lts_mca = st.number_input(f"LTS QUEIMA MCA ({prefixo})", value=7.0, step=0.1, key=f"l_{prefixo}")
        h_mano = st.number_input(f"HORA DE MANOBRA ({prefixo})", value=0.0, step=0.1, key=f"hm_{prefixo}")
        lh_mano = st.number_input(f"L/H MANOBRA ({prefixo})", value=0.0, step=0.1, key=f"lhm_{prefixo}")
        transf = st.number_input(f"TRANSFERÊNCIA BT ({prefixo})", value=0.0, step=1.0, key=f"t_{prefixo}")
        
        saida = s_odm + o_comp
        cons = (t_hor * queima) + (h_mca * lts_mca) + (h_mano * lh_mano)
        chegada = saida - cons - transf
        
        st.write(f"**ODM SAÍDA:** {saida:,.2f} | **CHEGADA:** {chegada:,.2f}")
        return {"saida": saida, "chegada": chegada, "t_hor": t_hor, "queima": queima, "h_mca": h_mca, "h_mano": h_mano, "lh_mano": lh_mano}

    with col_ida: res_i = entrada_dados("IDA")
    with col_volta: res_v = entrada_dados("VOLTA")

    if st.button("💾 FINALIZAR E SALVAR", use_container_width=True, type="primary"):
        # Salvamento com datas já formatadas em string BR
        nova_linha = pd.DataFrame([{
            "Empurrador": emp_m, 
            "Data": data_m.strftime('%d/%m/%Y'), 
            "Mes_Ano": data_m.strftime('%m/%Y'),
            "Local": trecho_m, 
            "ODM_Zarpe_Ida": res_i['saida'],
            "Plano_H_Ida": res_i['t_hor'], 
            "Queima_Ida": res_i['queima'],
            "Plano_H_Volta": res_v['t_hor'], 
            "Queima_Volta": res_v['queima'],
            "H_Mano_Ida": res_i['h_mano'], 
            "H_Mano_Volta": res_v['h_mano'],
            "LH_Mano_Ida": res_i['lh_mano'], 
            "LH_Mano_Volta": res_v['lh_mano'],
            "H_MCA_Ida": res_i['h_mca'], 
            "H_MCA_Volta": res_v['h_mca'],
            "ODM_Fim_Final": res_v['chegada'] if res_v['t_hor'] > 0 else res_i['chegada']
        }])
        st.session_state.db_comb = pd.concat([st.session_state.db_comb, nova_linha], ignore_index=True)
        st.success("Salvo com sucesso no padrão BR!")
        st.rerun()
