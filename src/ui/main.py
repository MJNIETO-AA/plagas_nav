import tkinter as tk
from tkinter import messagebox
from src.db.connection import get_connection


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema - Plagas Navarro(MVP)")
        self.geometry("520x260")
        self.resizable(False, False)

        tk.Label(self, text="Prueba 1: Tkinter + MySQL", font=("Arial", 14)).pack(pady=15)

        tk.Button(self, text="Probar conexion a MySQL", width=25, command=self.test_db).pack(pady=10)
        tk.Button( self, text="Salir", width=25, command=self.destroy).pack(pady=10)

    def test_db(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT DATABASE();")
            dbname = cur.fetchone()
            cur.close()
            conn.close()
            messagebox.showinfo("Ok", f"Connectado correctament a: {dbname}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()