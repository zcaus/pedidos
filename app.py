import streamlit as st
from datetime import datetime
import pandas as pd
import os
from io import BytesIO

FILE_PATH = 'pedidos.csv'

def carregar_pedidos():
    if os.path.exists(FILE_PATH):
        pedidos = pd.read_csv(FILE_PATH)
    else:
        pedidos = pd.DataFrame(columns=["Nº Pedido", "Fornecedor", "Qtd.", "Valor (R$)", "Pedido por", "Recebido por", "Nº NF", "Dt. Receb.", "Hr. Receb.", "Status"])
        pedidos.to_csv(FILE_PATH, index=False)

    return pedidos

def salvar_pedidos():
    st.session_state.pedidos.to_csv("pedidos.csv", index=False)

def gerar_excel_download_link(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df['Hr. Receb.'] = df['Hr. Receb.'].apply(lambda x: x.strftime("%H:%M") if isinstance(x, datetime) else x)
    df['Dt. Receb.'] = df['Dt. Receb.'].apply(lambda x: x.strftime("%d/%m/%y") if isinstance(x, datetime) else x)
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def lancar_pedido():
    st.markdown("<h1 style='text-align: center;'>Sistema de Pedidos</h1>", unsafe_allow_html=True)  
    with st.form(key='pedido_form'):
        numero_pedido = st.text_input("Nº Pedido")
        nome_empresa = st.text_input("Fornecedor")
        quantidade = st.number_input("Quantidade", min_value=1)
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        pedido_por = st.text_input("Pedido por")
        submit_button = st.form_submit_button(label='Lançar Pedido')
        
        if submit_button:
            if numero_pedido in st.session_state.pedidos["Nº Pedido"].values:
                st.error("Erro: Número do pedido já existe!")
            else:
                novo_pedido = pd.DataFrame([{
                    "Nº Pedido": numero_pedido,
                    "Fornecedor": nome_empresa,
                    "Qtd.": quantidade,
                    "Valor (R$)": valor,
                    "Pedido por": pedido_por,                
                    "Status": "Em trânsito",
                    "Recebido por": "",
                    "Nº NF": "",
                    "Dt. Receb.": "",
                    "Hr. Receb.": ""
                }])
                st.session_state.pedidos = pd.concat([st.session_state.pedidos, novo_pedido], ignore_index=True)
                salvar_pedidos()
                st.success("Pedido lançado com sucesso!")
                st.write(f"Nº Pedido: {numero_pedido}")
                st.write(f"Fornecedor: {nome_empresa}")
                st.write(f"Quantidade: {quantidade}")
                st.write(f"Valor: R${valor:.2f}")
                st.write(f"Pedido por: {pedido_por}")

def confirmar_recebimento():
    st.markdown("<h1 style='text-align: center;'>Sistema de Recebimentos</h1>", unsafe_allow_html=True)  

    # Filtros
    col1, col2 = st.columns(2)
    with col1:
        fornecedor_filter = st.selectbox("Filtrar por Fornecedor", options=["Todos"] + list(st.session_state.pedidos["Fornecedor"].unique()))
    with col2:
        status_filter = st.selectbox("Filtrar por Status", options=["Todos"] + list(st.session_state.pedidos["Status"].unique()))

    # Aplicar filtros
    filtered_pedidos = st.session_state.pedidos
    if fornecedor_filter != "Todos":
        filtered_pedidos = filtered_pedidos[filtered_pedidos["Fornecedor"] == fornecedor_filter]
    if status_filter != "Todos":
        filtered_pedidos = filtered_pedidos[filtered_pedidos["Status"] == status_filter]

    st.dataframe(filtered_pedidos, use_container_width=True)

    with st.form("receber_pedido_form"):
        numero_pedido = st.text_input("Nº Pedido")
        recebido_por = st.text_input("Recebido por")
        numero_nf = st.text_input("Número da Nota Fiscal")
        data_recebimento = st.date_input("Data de Recebimento", datetime.today())
        hora_recebimento = st.time_input("Hora de Recebimento", datetime.now())
        submit_button = st.form_submit_button("Confirmar Recebimento")
        
    if submit_button:
                if numero_pedido in st.session_state.pedidos["Nº Pedido"].values:

                    index = st.session_state.pedidos[st.session_state.pedidos["Nº Pedido"] == numero_pedido].index[0]
                    st.session_state.pedidos.at[index, "Recebido por"] = recebido_por
                    st.session_state.pedidos.at[index, "Nº NF"] = numero_nf
                    st.session_state.pedidos.at[index, "Dt. Receb."] = data_recebimento
                    st.session_state.pedidos.at[index, "Hr. Receb."] = hora_recebimento
                    
                    st.session_state.pedidos.at[index, "Status"] = "Recebido"
                    
                    salvar_pedidos()
                    st.success("Recebimento confirmado e status atualizado para 'Recebido'!")
                else:
                    st.error("Nº Pedido não encontrado!")

def main():    
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = carregar_pedidos()
    
    st.sidebar.title("Menu")
    menu = ["Lançar Pedido", "Receber Pedido"]
    choice = st.sidebar.radio("Escolha uma opção", menu)
    
    if choice == "Lançar Pedido":
        lancar_pedido()
    elif choice == "Receber Pedido":
        confirmar_recebimento()
    
    excel_data = gerar_excel_download_link(st.session_state.pedidos)
    st.sidebar.download_button(
        label="Baixar Relatório",
        data=excel_data,
        file_name='relatorio_pedidos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

if __name__ == '__main__':
    main()