import streamlit as st
from datetime import datetime
import pandas as pd
import os
from io import BytesIO

# Função para carregar pedidos do arquivo CSV
@st.cache_data
def carregar_pedidos():
    file_path = 'pedidos.csv'
    if os.path.exists(file_path):
        pedidos = pd.read_csv(file_path)
    else:
        pedidos = pd.DataFrame(columns=["ID", "Empresa", "Produto", "Qtd.", "Valor (R$)", "Pedido por", "Status", "Recebido por", "Nº NF", "Dt. Receb.", "Hr. Receb."])
    return pedidos

# Função para salvar pedidos no arquivo CSV
def salvar_pedidos():
    file_path = 'pedidos.csv'
    st.session_state.pedidos.to_csv(file_path, index=False)

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

# Função para lançar um novo pedido
def lancar_pedido():
    st.markdown("<h1 style='text-align: center;'>Sistema de Pedidos</h1>", unsafe_allow_html=True)  
    with st.form(key='pedido_form'):
        nome_empresa = st.text_input("Empresa")
        produto = st.text_input("Produto")
        quantidade = st.number_input("Quantidade", min_value=1)
        valor = st.number_input("Valor", min_value=0.0, format="%.2f")
        pedido_por = st.text_input("Pedido por")
        submit_button = st.form_submit_button(label='Lançar Pedido')
        
        if submit_button:
            novo_pedido = pd.DataFrame([{
                "ID": str(len(st.session_state.pedidos) + 1).zfill(3),
                "Empresa": nome_empresa,
                "Produto": produto,
                "Qtd.": quantidade,
                "Valor (R$)": valor,
                "Pedido por": pedido_por,                
                "Status": "Pendente",
                "Recebido por": "",
                "Nº NF": "",
                "Dt. Receb.": "",
                "Hr. Receb.": ""
            }])
            st.session_state.pedidos = pd.concat([st.session_state.pedidos, novo_pedido], ignore_index=True)
            salvar_pedidos()
            st.success("Pedido lançado com sucesso!")
            st.write(f"Empresa: {nome_empresa}")
            st.write(f"Produto: {produto}")
            st.write(f"Quantidade: {quantidade}")
            st.write(f"Valor: R${valor:.2f}")
            st.write(f"Pedido por: {pedido_por}")

# Função para confirmar o recebimento de um pedido
def confirmar_recebimento():
    st.markdown("<h1 style='text-align: center;'>Controle de Recebimento</h1>", unsafe_allow_html=True)      
    st.subheader("Pedidos Lançados")
    col1, col2 = st.columns(2)
    with col1:
        empresa_filter = st.selectbox("Filtrar por Empresa", options=[""] + st.session_state.pedidos['Empresa'].unique().tolist())
    with col2:
        status_filter = st.selectbox("Filtrar por Status", options=["Todos", "Pendente", "Entregue"])
    
    pedidos = st.session_state.pedidos

    if empresa_filter:
        pedidos = pedidos[pedidos['Empresa'].str.contains(empresa_filter, case=False)]
    if status_filter != "Todos":
        pedidos = pedidos[pedidos['Status'] == status_filter]        
    
    st.dataframe(pedidos, use_container_width=True)
    
    with st.form(key='confirmacao_form'):
        pedido_id = st.text_input("ID do Pedido")
        data_recebimento = st.date_input("Data de Recebimento", value=datetime.today())
        nf_recebimento = st.text_input("Número da Nota Fiscal")
        quem_recebeu = st.text_input("Recebido por")
        hora_recebimento_formatada = datetime.now().strftime("%H:%M")
        hora_recebimento = st.text_input("Hora de Recebimento", value=hora_recebimento_formatada)
        
        confirmar_button = st.form_submit_button(label='Confirmar Recebimento')
        
        if confirmar_button:
            st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Status'] = 'Entregue'
            st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Recebido por'] = quem_recebeu
            st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Nº NF'] = nf_recebimento
            st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Dt. Receb.'] = data_recebimento.strftime("%d/%m/%y")
            st.session_state.pedidos.loc[st.session_state.pedidos['ID'] == pedido_id, 'Hr. Receb.'] = hora_recebimento
            salvar_pedidos()
            st.success("Recebimento confirmado com sucesso!")
            st.write(f"ID do Pedido: {pedido_id}")
            st.write(f"Recebido por: {quem_recebeu}")
            st.write(f"Nº NF: {nf_recebimento}")
            st.write(f"Dt. Receb.: {data_recebimento.strftime('%d/%m/%y')}")
            st.write(f"Hr. Receb.: {hora_recebimento}")

# Função principal
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
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("<h3 style='font-size:10px;'>Feito por Cauã Moreira</h3>", unsafe_allow_html=True)

if __name__ == '__main__':
    main()