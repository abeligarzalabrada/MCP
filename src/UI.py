import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import asyncio
import threading
from client import geminis_peticion

class MinimalDarkUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MCP Minimal UI")
        self.configure(bg="#18191a")
        self.geometry("640x450")
        self.resizable(False, False)

        # Conversación (parte superior)
        self.conversation = ScrolledText(self, state='disabled', wrap='word', font=("Segoe UI", 12),
                                         bg="#232526", fg="#f7f7f7", bd=0, relief="flat", height=16)
        self.conversation.pack(padx=16, pady=(16,8), fill=tk.BOTH, expand=True)

        # "Burger" menu button
        self.burger_btn = tk.Button(self, text="≡", font=("Segoe UI", 18), fg="#e0e0e0", bg="#404247",
                                    activebackground="#3a86ff", bd=0, width=2, command=self.toggle_panel)
        self.burger_btn.place(x=12, y=12)

        # Input box for user message (bottom)
        self.input_frame = tk.Frame(self, bg="#18191a")
        self.input_frame.pack(fill=tk.X, padx=16, pady=(0, 16), side=tk.BOTTOM)

        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self.input_frame, font=("Segoe UI", 14), bg="#1e1e1e", fg="#f7f7f7",
                                   insertbackground="#f7f7f7", bd=2, relief="flat", textvariable=self.input_var)
        self.input_entry.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)
        self.input_entry.bind("<Return>", self.on_send)

        self.send_btn = tk.Button(self.input_frame, text="Enviar", bg="#3a86ff", fg="#fff",
                                  font=("Segoe UI", 12, "bold"), bd=0, padx=16, pady=2, command=self.on_send)
        self.send_btn.pack(side="right", pady=8)

        self.input_entry.focus_set()

        # Side panel (hidden by default)
        self.bg_panel = "#232526"
        self.panel_border = "#323232"
        self.panel_open = False
        self.side_panel = tk.Frame(self, bg=self.bg_panel, width=220, height=450, highlightbackground=self.panel_border, highlightthickness=1)
        self.side_panel.place(x=-220, y=0)
        self._build_side_panel()

        # Asyncio loop en hilo separado
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.start_loop, daemon=True).start()

    def _build_side_panel(self):
        tk.Label(self.side_panel, text="Configuración", font=("Segoe UI", 14, "bold"),
                 bg=self.bg_panel, fg="#fff").pack(pady=(20, 10))

        tk.Label(self.side_panel, text="Correo electrónico:", bg=self.bg_panel, fg="#e0e0e0", anchor="w").pack(fill="x", padx=16)
        self.email_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.email_var, font=("Segoe UI", 12), bg="#1e1e1e", fg="#f7f7f7", relief="flat").pack(fill="x", padx=16, pady=(0,8))

        tk.Label(self.side_panel, text="User Key:", bg=self.bg_panel, fg="#e0e0e0", anchor="w").pack(fill="x", padx=16)
        self.ukey_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.ukey_var, font=("Segoe UI", 12), bg="#1e1e1e", fg="#f7f7f7", relief="flat").pack(fill="x", padx=16, pady=(0,8))

        tk.Label(self.side_panel, text="Drive Key:", bg=self.bg_panel, fg="#e0e0e0", anchor="w").pack(fill="x", padx=16)
        self.dkey_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.dkey_var, font=("Segoe UI", 12), bg="#1e1e1e", fg="#f7f7f7", relief="flat").pack(fill="x", padx=16, pady=(0,12))

        tk.Button(self.side_panel, text="Guardar", bg="#3a86ff", fg="#fff",
                  font=("Segoe UI", 12, "bold"), relief="flat", command=self.save_config).pack(pady=12)

    def toggle_panel(self):
        if not self.panel_open:
            self.side_panel.place(x=0, y=0)
            self.panel_open = True
        else:
            self.side_panel.place(x=-220, y=0)
            self.panel_open = False

    def save_config(self):
        # Aquí puedes guardar los valores donde lo necesites
        self.toggle_panel()

    def start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_send(self, event=None):
        msg = self.input_var.get().strip()
        if not msg:
            return
        self.input_var.set("")
        self.append_message("Tú", msg)
        self.loop.call_soon_threadsafe(self.loop.create_task, self.handle_bot_response(msg))

    def append_message(self, sender, message):
        self.conversation.config(state='normal')
        self.conversation.insert(tk.END, f"{sender}: {message}\n")
        self.conversation.yview(tk.END)
        self.conversation.config(state='disabled')

    async def handle_bot_response(self, user_message):
        # Puedes personalizar el prompt según tu flujo
        tools_info_promt = (
            "## Gemini Instructions (MCP)\n"
            "Puedes formatear tu prompt aquí según lo que espera tu client.py.\n"
        )
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: geminis_peticion(user_message, tools_info_promt)
            )
            answer = response.text if isinstance(response.text, str) else str(response.text)
        except Exception as e:
            answer = f"[Error en la respuesta: {e}]"
        self.append_message("Gemini", answer)

if __name__ == "__main__":
    app = MinimalDarkUI()
    app.mainloop()
