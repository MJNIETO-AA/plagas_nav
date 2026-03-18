import tkinter as tk
from tkinter import messagebox
from src.db.connection import get_connection
from src.ui.menu import MainMenu
from src.utils.security import verify_password


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plagas Navarro - Iniciar Sesión")
        self.geometry("380x240")
        self.resizable(False, False)

        tk.Label(self, text="Iniciar Sesión", font=("Arial", 16, "bold")).pack(pady=(20, 15))

        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Usuario:").grid(row=0, column=0, sticky="w", pady=6, padx=6)
        self.username_entry = tk.Entry(form_frame, width=28)
        self.username_entry.grid(row=0, column=1, pady=6, padx=6)

        tk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=6, padx=6)
        self.password_entry = tk.Entry(form_frame, width=28, show="*")
        self.password_entry.grid(row=1, column=1, pady=6, padx=6)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Ingresar", width=15, command=self.login).pack()

        self.username_entry.focus()
        self.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Validación", "Debes ingresar usuario y contraseña.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(
                "SELECT id, username, password_hash, role FROM users WHERE username=%s",
                (username,)
            )
            user = cur.fetchone()
            cur.close()
            conn.close()

            if not user:
                messagebox.showerror("Error", "Usuario no encontrado.")
                return

            if not verify_password(password, user["password_hash"]):
                messagebox.showerror("Error", "Contraseña incorrecta.")
                return

            self.withdraw()
            MainMenu(self, user)

        except Exception as e:
            messagebox.showerror("Error", str(e))

