import tkinter as tk
from tkinter import simpledialog

class MinimalDarkUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MCP Minimal UI")
        self.configure(bg="#18191a")
        self.geometry("640x400")
        self.resizable(False, False)

        # Colors for dark theme
        self.bg_dark = "#18191a"
        self.bg_panel = "#232526"
        self.bg_entry = "#1e1e1e"
        self.fg_entry = "#f7f7f7"
        self.fg_label = "#e0e0e0"
        self.button_gray = "#404247"
        self.button_highlight = "#3a86ff"
        self.panel_border = "#323232"

        # State of side panel
        self.panel_open = False

        # Side panel (hidden by default)
        self.side_panel = tk.Frame(self, bg=self.bg_panel, width=220, height=400, highlightbackground=self.panel_border, highlightthickness=1)
        self.side_panel.place(x=-220, y=0)
        self._build_side_panel()

        # "Burger" menu button
        self.burger_btn = tk.Button(self, text="≡", font=("Segoe UI", 18), fg=self.fg_label, bg=self.button_gray,
                                    activebackground=self.button_highlight, bd=0, width=2, command=self.toggle_panel)
        self.burger_btn.place(x=12, y=12)

        # Input box for user message (bottom)
        self.input_frame = tk.Frame(self, bg=self.bg_dark)
        self.input_frame.place(relx=0.18, rely=0.8, relwidth=0.8, height=50)

        self.input_entry = tk.Entry(self.input_frame, font=("Segoe UI", 14), bg=self.bg_entry, fg=self.fg_entry,
                                   insertbackground=self.fg_entry, bd=2, relief="flat")
        self.input_entry.pack(side="left", fill="both", expand=True, padx=(0, 8), pady=8)

        self.send_btn = tk.Button(self.input_frame, text="Enviar", bg=self.button_highlight, fg="#fff",
                                  font=("Segoe UI", 12, "bold"), bd=0, padx=16, pady=2, command=self.on_send)
        self.send_btn.pack(side="right", pady=8)

        # Focus on entry
        self.input_entry.focus_set()

    def _build_side_panel(self):
        # Title label
        tk.Label(self.side_panel, text="Configuración", font=("Segoe UI", 14, "bold"),
                 bg=self.bg_panel, fg="#fff").pack(pady=(20, 10))

        # Email config
        tk.Label(self.side_panel, text="Correo electrónico:", bg=self.bg_panel, fg=self.fg_label, anchor="w").pack(fill="x", padx=16)
        self.email_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.email_var, font=("Segoe UI", 12), bg=self.bg_entry, fg=self.fg_entry, relief="flat").pack(fill="x", padx=16, pady=(0,8))

        # User key config
        tk.Label(self.side_panel, text="User Key:", bg=self.bg_panel, fg=self.fg_label, anchor="w").pack(fill="x", padx=16)
        self.ukey_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.ukey_var, font=("Segoe UI", 12), bg=self.bg_entry, fg=self.fg_entry, relief="flat").pack(fill="x", padx=16, pady=(0,8))

        # Drive key config
        tk.Label(self.side_panel, text="Drive Key:", bg=self.bg_panel, fg=self.fg_label, anchor="w").pack(fill="x", padx=16)
        self.dkey_var = tk.StringVar(value="")
        tk.Entry(self.side_panel, textvariable=self.dkey_var, font=("Segoe UI", 12), bg=self.bg_entry, fg=self.fg_entry, relief="flat").pack(fill="x", padx=16, pady=(0,12))

        # Save button
        tk.Button(self.side_panel, text="Guardar", bg=self.button_highlight, fg="#fff",
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
        print("Email:", self.email_var.get())
        print("User Key:", self.ukey_var.get())
        print("Drive Key:", self.dkey_var.get())
        self.toggle_panel()

    def on_send(self):
        user_input = self.input_entry.get().strip()
        if user_input:
            # Aquí debes conectar con tu lógica de client.py para enviar el mensaje
            print("Mensaje enviado:", user_input)
            self.input_entry.delete(0, tk.END)

if __name__ == "__main__":
    app = MinimalDarkUI()
    app.mainloop()
