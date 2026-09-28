import tkinter as tk
from tkinter import ttk, messagebox


def exibir_mensagem():
    texto = entrada_texto.get().strip()
    if not texto:
        messagebox.showwarning("Aviso", "Por favor, digite algum texto antes de clicar no botão!")
        return

    # Exibe caixa de diálogo com o texto informado
    messagebox.showinfo("Mensagem Recebida", f"Você digitou:\n\n{texto}")
    # Também atualiza o rótulo de resultado na própria janela
    lbl_resultado.config(text=f"Última mensagem: {texto}", foreground="#1e7e34")


# Criação da janela principal
janela = tk.Tk()
janela.title("Aplicação GUI")
janela.geometry("420x260")
janela.resizable(False, False)

# Configuração de estilo ttk
estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TLabel", font=("Helvetica", 10))
estilo.configure("TButton", font=("Helvetica", 10, "bold"), padding=6)
estilo.configure("TEntry", font=("Helvetica", 11), padding=4)

# Container principal com padding
container = ttk.Frame(janela, padding=20)
container.pack(fill="both", expand=True)

# Título / Instrução
lbl_instrucao = ttk.Label(
    container,
    text="Digite o texto no campo abaixo:",
    font=("Helvetica", 11, "bold")
)
lbl_instrucao.pack(anchor="w", pady=(0, 8))

# Campo de texto (Entry)
entrada_texto = ttk.Entry(container, width=40)
entrada_texto.pack(fill="x", pady=(0, 15))
entrada_texto.focus()

# Botão para exibir a mensagem
btn_exibir = ttk.Button(
    container,
    text="Exibir Mensagem",
    command=exibir_mensagem
)
btn_exibir.pack(fill="x", pady=(0, 15))

# Permite acionar pressionando a tecla Enter
janela.bind("<Return>", lambda event: exibir_mensagem())

# Rótulo para exibir o resultado também diretamente na interface
lbl_resultado = ttk.Label(
    container,
    text="",
    wraplength=380,
    justify="center",
    font=("Helvetica", 10, "italic")
)
lbl_resultado.pack(fill="x", pady=(5, 0))

if __name__ == "__main__":
    janela.mainloop()
