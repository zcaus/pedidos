import streamlit as st
from datetime import datetime
import pandas as pd
import os
from io import BytesIO

# Caminho do arquivo CSV
FILE_PATH = 'pedidos.csv'

# Função para carregar pedidos do arquivo CSV
@st.cache_data
def carregar_pedidos():
    if os.path.exists(FILE_PATH):
        pedidos = pd.read_csv(FILE_PATH)
    else:
        pedidos = pd.DataFrame(columns=["ID", "Empresa", "Produto", "Qtd.", "Valor (R$)", "Pedido por", "Status", "Recebido por", "Nº NF", "Dt. Receb.", "Hr. Receb."])
        pedidos.to_csv(FILE_PATH, index=False)
    return pedidos

# Função para salvar pedidos no arquivo CSV
def salvar_pedidos():
    st.session_state.pedidos.to_csv(FILE_PATH, index=False)

# Função para gerar link de download do Excel
def gerar_excel_download_link(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df['Hr. Receb.'] = df['Hr. Receb.'].apply(lambda x: x.strftime("%H:%M") if isinstance(x, datetime) else x)
    df['Dt. Receb.'] = df['Dt. Receb.'].apply(lambda x: x.strftime("%d/%m/%y") if isinstance(x, datetime) else x)
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Função para lançar pedidos
def lancar_pedido():
    st.title("Lançar Pedido")
    with st.form("lancar_pedido_form"):
        id = st.text_input("ID")
        empresa = st.text_input("Empresa")
        produto = st.text_input("Produto")
        qtd = st.number_input("Quantidade", min_value=1)
        valor = st.number_input("Valor Unitário (R$)", min_value=0.0, format="%.2f")
        pedido_por = st.text_input("Pedido por")
        status = st.selectbox("Status", ["Pendente", "Concluído"])
        submit_button = st.form_submit_button("Adicionar Pedido")
        
        if submit_button:
            novo_pedido = {
                "ID": id,
                "Empresa": empresa,
                "Produto": produto,
                "Qtd.": qtd,
                "Valor (R$)": valor,
                "Pedido por": pedido_por,
                "Status": status,
                "Recebido por": "",
                "Nº NF": "",
                "Dt. Receb.": "",
                "Hr. Receb.": ""
            }
            st.session_state.pedidos = st.session_state.pedidos.append(novo_pedido, ignore_index=True)
            salvar_pedidos()
            st.success("Pedido adicionado com sucesso!")

# Função para confirmar recebimento de pedidos
def confirmar_recebimento():
    st.title("Receber Pedido")
    with st.form("receber_pedido_form"):
        id = st.selectbox("Selecione o ID do Pedido", st.session_state.pedidos["ID"])
        recebido_por = st.text_input("Recebido por")
        numero_nf = st.text_input("Número da Nota Fiscal")
        data_recebimento = st.date_input("Data de Recebimento", datetime.today())
        hora_recebimento = st.time_input("Hora de Recebimento", datetime.now())
        submit_button = st.form_submit_button("Confirmar Recebimento")
        
        if submit_button:
            index = st.session_state.pedidos[st.session_state.pedidos["ID"] == id].index[0]
            st.session_state.pedidos.at[index, "Recebido por"] = recebido_por
            st.session_state.pedidos.at[index, "Nº NF"] = numero_nf
            st.session_state.pedidos.at[index, "Dt. Receb."] = data_recebimento
            st.session_state.pedidos.at[index, "Hr. Receb."] = hora_recebimento
            salvar_pedidos()
            st.success("Recebimento confirmado com sucesso!")

# Função principal
def main():
    # Carregar pedidos na sessão
    if 'pedidos' not in st.session_state:
        st.session_state.pedidos = carregar_pedidos()
    
    # Sidebar
    st.sidebar.title("Menu")
    menu = ["Lançar Pedido", "Receber Pedido"]
    choice = st.sidebar.radio("Escolha uma opção", menu)
    
    # Lógica principal
    if choice == "Lançar Pedido":
        lancar_pedido()
    elif choice == "Receber Pedido":
        confirmar_recebimento()
    
    # Link para baixar o relatório
    excel_data = gerar_excel_download_link(st.session_state.pedidos)
    st.sidebar.download_button(
        label="Baixar Relatório",
        data=excel_data,
        file_name='relatorio_pedidos.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='font-size:10px;'>Feito por Cauã Moreira</h3>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()
