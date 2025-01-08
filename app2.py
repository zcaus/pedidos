import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# Conexão com o banco de dados
def conectar_banco():
    conexao = sqlite3.connect("pedidos.db")
    cursor = conexao.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS pedidos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cliente TEXT,
                        produto TEXT,
                        quantidade INTEGER,
                        valor REAL,
                        status TEXT DEFAULT "Pendente",
                        recebido_por TEXT,
                        hora_recebimento TEXT,
                        data_recebimento TEXT,
                        nr_nf TEXT)''')
    conexao.commit()
    return conexao

# Função para salvar pedidos
def salvar_pedido():
    cliente = entry_cliente.get()
    produto = entry_produto.get()
    quantidade = entry_quantidade.get()
    valor = entry_valor.get()

    if not cliente or not produto or not quantidade or not valor:
        messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
        return

    try:
        quantidade = int(quantidade)
        valor = float(valor)
    except ValueError:
        messagebox.showerror("Erro", "Quantidade e Valor devem ser numéricos!")
        return

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO pedidos (cliente, produto, quantidade, valor) VALUES (?, ?, ?, ?)",
                   (cliente, produto, quantidade, valor))
    conexao.commit()
    conexao.close()

    messagebox.showinfo("Sucesso", "Pedido salvo com sucesso!")
    entry_cliente.delete(0, tk.END)
    entry_produto.delete(0, tk.END)
    entry_quantidade.delete(0, tk.END)
    entry_valor.delete(0, tk.END)

    carregar_pedidos()

# Função para abrir a janela de confirmação
def abrir_confirmacao():
    pedido_selecionado = treeview.selection()
    if not pedido_selecionado:
        messagebox.showerror("Erro", "Nenhum pedido selecionado!")
        return

    pedido_id = treeview.item(pedido_selecionado, "values")[0]

    # Janela para preenchimento dos dados
    janela_confirmacao = tk.Toplevel(janela)
    janela_confirmacao.title("Confirmar Recebimento")

    ttk.Label(janela_confirmacao, text="Recebido por:").grid(row=0, column=0, padx=5, pady=5)
    entry_recebido_por = ttk.Entry(janela_confirmacao)
    entry_recebido_por.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(janela_confirmacao, text="Hora do Recebimento:").grid(row=1, column=0, padx=5, pady=5)
    entry_hora = ttk.Entry(janela_confirmacao)
    entry_hora.insert(0, datetime.now().strftime("%H:%M:%S"))  # Preenchimento automático
    entry_hora.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(janela_confirmacao, text="Data do Recebimento:").grid(row=2, column=0, padx=5, pady=5)
    entry_data = ttk.Entry(janela_confirmacao)
    entry_data.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Preenchimento automático
    entry_data.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(janela_confirmacao, text="Nr da NF:").grid(row=3, column=0, padx=5, pady=5)
    entry_nr_nf = ttk.Entry(janela_confirmacao)
    entry_nr_nf.grid(row=3, column=1, padx=5, pady=5)

    def confirmar():
        recebido_por = entry_recebido_por.get()
        hora = entry_hora.get()
        data = entry_data.get()
        nr_nf = entry_nr_nf.get()

        if not recebido_por or not hora or not data or not nr_nf:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios!")
            return

        conexao = conectar_banco()
        cursor = conexao.cursor()
        cursor.execute("""
            UPDATE pedidos 
            SET status = 'Recebido', recebido_por = ?, hora_recebimento = ?, data_recebimento = ?, nr_nf = ?
            WHERE id = ?
        """, (recebido_por, hora, data, nr_nf, pedido_id))
        conexao.commit()
        conexao.close()

        messagebox.showinfo("Sucesso", "Pedido confirmado como recebido!")
        carregar_pedidos()
        janela_confirmacao.destroy()

    ttk.Button(janela_confirmacao, text="Confirmar", command=confirmar).grid(row=4, column=0, columnspan=2, pady=10)

# Função para carregar pedidos no Treeview
def carregar_pedidos():
    for row in treeview.get_children():
        treeview.delete(row)

    conexao = conectar_banco()
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM pedidos")
    for row in cursor.fetchall():
        treeview.insert("", tk.END, values=row)
    conexao.close()

# Interface principal
janela = tk.Tk()
janela.title("Sistema de Pedidos")

# Aba de lançamento de pedidos
notebook = ttk.Notebook(janela)
aba_pedidos = ttk.Frame(notebook)
aba_confirmacao = ttk.Frame(notebook)
notebook.add(aba_pedidos, text="Lançar Pedido")
notebook.add(aba_confirmacao, text="Confirmar Recebimento")
notebook.pack(expand=True, fill="both")

# Widgets para lançamento de pedidos
ttk.Label(aba_pedidos, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
entry_cliente = ttk.Entry(aba_pedidos)
entry_cliente.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(aba_pedidos, text="Produto:").grid(row=1, column=0, padx=5, pady=5)
entry_produto = ttk.Entry(aba_pedidos)
entry_produto.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(aba_pedidos, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
entry_quantidade = ttk.Entry(aba_pedidos)
entry_quantidade.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(aba_pedidos, text="Valor:").grid(row=3, column=0, padx=5, pady=5)
entry_valor = ttk.Entry(aba_pedidos)
entry_valor.grid(row=3, column=1, padx=5, pady=5)

btn_salvar = ttk.Button(aba_pedidos, text="Salvar Pedido", command=salvar_pedido)
btn_salvar.grid(row=4, column=0, columnspan=2, pady=10)

# Widgets para confirmação de recebimento
treeview = ttk.Treeview(aba_confirmacao, columns=("id", "cliente", "produto", "quantidade", "valor", "status", "recebido_por", "hora_recebimento", "data_recebimento", "nr_nf"), show="headings")
treeview.heading("id", text="ID")
treeview.heading("cliente", text="Cliente")
treeview.heading("produto", text="Produto")
treeview.heading("quantidade", text="Quantidade")
treeview.heading("valor", text="Valor")
treeview.heading("status", text="Status")
treeview.heading("recebido_por", text="Recebido Por")
treeview.heading("hora_recebimento", text="Hora")
treeview.heading("data_recebimento", text="Data")
treeview.heading("nr_nf", text="Nr NF")
treeview.pack(expand=True, fill="both", padx=5, pady=5)

btn_confirmar = ttk.Button(aba_confirmacao, text="Confirmar Recebimento", command=abrir_confirmacao)
btn_confirmar.pack(pady=10)

# Carregar pedidos ao iniciar
carregar_pedidos()

janela.mainloop()
