import tkinter as tk
from tkinter import ttk, messagebox
from src.db.connection import get_connection


class ClientsWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Clientes")
        self.geometry("980x560")
        self.resizable(False, False)

        self.selected_id = None

        tk.Label(self, text="Módulo de Clientes", font=("Arial", 14)).pack(pady=10)

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        form_frame = tk.LabelFrame(main_frame, text="Datos del cliente", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        self.full_name_var = tk.StringVar(master=self)
        self.phone_var = tk.StringVar(master=self)
        self.email_var = tk.StringVar(master=self)
        self.search_var = tk.StringVar(master=self)

        tk.Label(form_frame, text="Nombre completo:").grid(row=0, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.full_name_var, width=30).grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Teléfono:").grid(row=1, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.phone_var, width=30).grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Correo electrónico:").grid(row=2, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.email_var, width=30).grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Dirección:").grid(row=3, column=0, sticky="nw")
        self.address_text = tk.Text(form_frame, width=30, height=5)
        self.address_text.grid(row=3, column=1, pady=5)

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=12)

        ttk.Button(btn_frame, text="Guardar", command=self.save_client).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Actualizar", command=self.update_client).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_client).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        tk.Label(
            form_frame,
            text="Tip: selecciona un cliente de la tabla para editar o eliminar.",
            fg="gray"
        ).grid(row=5, column=0, columnspan=2, pady=(8, 0))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = tk.LabelFrame(right_frame, text="Buscar", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Nombre o teléfono:").grid(row=0, column=0, sticky="w")
        tk.Entry(search_frame, textvariable=self.search_var, width=35).grid(row=0, column=1, padx=6)
        ttk.Button(search_frame, text="Buscar", command=self.search_clients).grid(row=0, column=2, padx=4)
        ttk.Button(search_frame, text="Ver todos", command=self.load_clients).grid(row=0, column=3, padx=4)

        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "full_name", "phone", "email", "address")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        self.tree.heading("id", text="ID")
        self.tree.heading("full_name", text="Nombre")
        self.tree.heading("phone", text="Teléfono")
        self.tree.heading("email", text="Correo")
        self.tree.heading("address", text="Dirección")

        self.tree.column("id", width=50)
        self.tree.column("full_name", width=220)
        self.tree.column("phone", width=120)
        self.tree.column("email", width=180)
        self.tree.column("address", width=260)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_clients()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_form(self):
        self.selected_id = None
        self.full_name_var.set("")
        self.phone_var.set("")
        self.email_var.set("")
        self.address_text.delete("1.0", "end")

    def load_clients(self):
        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, full_name, phone, email, address
                FROM clients
                ORDER BY id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                self.tree.insert("", "end", values=(
                    r[0],
                    r[1] or "",
                    r[2] or "",
                    r[3] or "",
                    r[4] or ""
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_clients(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_clients()
            return

        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            like = f"%{term}%"
            cur.execute("""
                SELECT id, full_name, phone, email, address
                FROM clients
                WHERE full_name LIKE %s OR phone LIKE %s
                ORDER BY id DESC
            """, (like, like))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                self.tree.insert("", "end", values=(
                    r[0],
                    r[1] or "",
                    r[2] or "",
                    r[3] or "",
                    r[4] or ""
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_client(self):
        full_name = self.full_name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_text.get("1.0", "end").strip()

        if not full_name:
            messagebox.showwarning("Validación", "El nombre completo es obligatorio.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO clients (full_name, phone, email, address)
                VALUES (%s, %s, %s, %s)
            """, (full_name, phone or None, email or None, address or None))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Cliente guardado.")
            self.clear_form()
            self.load_clients()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_client(self):
        if not self.selected_id:
            messagebox.showwarning("Actualizar", "Selecciona un cliente de la tabla primero.")
            return

        full_name = self.full_name_var.get().strip()
        phone = self.phone_var.get().strip()
        email = self.email_var.get().strip()
        address = self.address_text.get("1.0", "end").strip()

        if not full_name:
            messagebox.showwarning("Validación", "El nombre completo es obligatorio.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE clients
                SET full_name=%s, phone=%s, email=%s, address=%s
                WHERE id=%s
            """, (full_name, phone or None, email or None, address or None, self.selected_id))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Cliente actualizado.")
            self.clear_form()
            self.load_clients()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_client(self):
        if not self.selected_id:
            messagebox.showwarning("Eliminar", "Selecciona un cliente de la tabla primero.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este cliente?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM clients WHERE id=%s", (self.selected_id,))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Cliente eliminado.")
            self.clear_form()
            self.load_clients()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])

        self.full_name_var.set(values[1])
        self.phone_var.set(values[2])
        self.email_var.set(values[3])

        self.address_text.delete("1.0", "end")
        self.address_text.insert("1.0", values[4])