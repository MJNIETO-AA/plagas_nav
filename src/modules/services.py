import tkinter as tk
from tkinter import ttk, messagebox
from src.db.connection import get_connection


class ServicesWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Servicios / Pagos")
        self.geometry("980x540")
        self.resizable(False, False)

        self.selected_id = None
        self.clients_lookup = {}

        tk.Label(self, text="Módulo de Servicios / Pagos", font=("Arial", 14)).pack(pady=10)

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=8)

        form_frame = tk.LabelFrame(main_frame, text="Datos del Servicio", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        self.client_var = tk.StringVar(master=self)
        self.desc_var = tk.StringVar(master=self)
        self.date_var = tk.StringVar(master=self)
        self.amount_var = tk.StringVar(master=self)
        self.status_var = tk.StringVar(master=self, value="Pendiente")

        tk.Label(form_frame, text="Cliente:").grid(row=0, column=0, sticky="w")
        self.client_combo = ttk.Combobox(
            form_frame,
            textvariable=self.client_var,
            width=30,
            state="readonly"
        )
        self.client_combo.grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Descripción:").grid(row=1, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.desc_var, width=32).grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Fecha (YYYY-MM-DD):").grid(row=2, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.date_var, width=32).grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Monto ($):").grid(row=3, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.amount_var, width=32).grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Estado:").grid(row=4, column=0, sticky="w")
        self.status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            values=["Pendiente", "Pagado"],
            state="readonly",
            width=30
        )
        self.status_combo.grid(row=4, column=1, pady=5)

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(btn_frame, text="Guardar", command=self.save_service).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Actualizar", command=self.update_service).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_service).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        tk.Label(
            form_frame,
            text="Tip: selecciona un servicio de la tabla para editar o eliminar.",
            fg="gray"
        ).grid(row=6, column=0, columnspan=2, pady=(8, 0))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = tk.LabelFrame(right_frame, text="Buscar", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar(master=self)
        tk.Label(search_frame, text="Cliente o descripción:").grid(row=0, column=0, sticky="w")
        tk.Entry(search_frame, textvariable=self.search_var, width=40).grid(row=0, column=1, padx=6)
        ttk.Button(search_frame, text="Buscar", command=self.search_services).grid(row=0, column=2, padx=4)
        ttk.Button(search_frame, text="Ver todos", command=self.load_services).grid(row=0, column=3, padx=4)

        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("id", "client_id", "cliente", "descripcion", "fecha", "monto", "estado"),
            show="headings"
        )
        self.tree.heading("id", text="ID")
        self.tree.heading("client_id", text="Client ID")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("monto", text="Monto")
        self.tree.heading("estado", text="Estado")

        self.tree.column("id", width=50)
        self.tree.column("client_id", width=0, stretch=False)
        self.tree.column("cliente", width=160)
        self.tree.column("descripcion", width=220)
        self.tree.column("fecha", width=100)
        self.tree.column("monto", width=90)
        self.tree.column("estado", width=100)

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_clients_combo()
        self.load_services()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_form(self):
        self.selected_id = None
        self.client_var.set("")
        self.desc_var.set("")
        self.date_var.set("")
        self.amount_var.set("")
        self.status_var.set("Pendiente")

    def load_clients_combo(self):
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, full_name FROM clients ORDER BY full_name ASC")
            rows = cur.fetchall()
            cur.close()
            conn.close()

            values = []
            self.clients_lookup = {}
            for r in rows:
                client_id = str(r[0])
                full_name = r[1] or ""
                display = f"{client_id} - {full_name}"
                values.append(display)
                self.clients_lookup[client_id] = display

            self.client_combo["values"] = values

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def get_selected_client_id(self):
        val = self.client_var.get().strip()
        if not val:
            return None
        return val.split(" - ")[0].strip()

    def save_service(self):
        client_id = self.get_selected_client_id()
        desc = self.desc_var.get().strip()
        service_date = self.date_var.get().strip()
        amount_txt = self.amount_var.get().strip()
        status = self.status_var.get().strip()

        if not client_id:
            messagebox.showwarning("Validación", "Selecciona un cliente.")
            return
        if not desc:
            messagebox.showwarning("Validación", "La descripción es obligatoria.")
            return
        if not service_date:
            messagebox.showwarning("Validación", "La fecha es obligatoria.")
            return
        if not amount_txt:
            messagebox.showwarning("Validación", "El monto es obligatorio.")
            return

        try:
            amount = float(amount_txt)
        except ValueError:
            messagebox.showwarning("Validación", "El monto debe ser numérico.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO services (client_id, description, service_date, amount, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (client_id, desc, service_date, amount, status))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Servicio guardado.")
            self.clear_form()
            self.load_services()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_services(self):
        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT s.id, s.client_id, c.full_name, s.description, s.service_date, s.amount, s.status
                FROM services s
                JOIN clients c ON c.id = s.client_id
                ORDER BY s.id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                self.tree.insert("", "end", values=(
                    r[0],
                    r[1],
                    r[2] or "",
                    r[3] or "",
                    str(r[4]) if r[4] is not None else "",
                    f"{float(r[5]):.2f}" if r[5] is not None else "0.00",
                    r[6] or ""
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        vals = self.tree.item(selected[0], "values")
        self.selected_id = vals[0]

        client_id = str(vals[1])
        self.client_var.set(self.clients_lookup.get(client_id, ""))

        self.desc_var.set(vals[3])
        self.date_var.set(vals[4])
        self.amount_var.set(vals[5])
        self.status_var.set(vals[6])

    def update_service(self):
        if not self.selected_id:
            messagebox.showwarning("Validación", "Selecciona un servicio de la tabla.")
            return

        client_id = self.get_selected_client_id()
        desc = self.desc_var.get().strip()
        service_date = self.date_var.get().strip()
        amount_txt = self.amount_var.get().strip()
        status = self.status_var.get().strip()

        if not client_id or not desc or not service_date or not amount_txt:
            messagebox.showwarning("Validación", "Completa los campos requeridos.")
            return

        try:
            amount = float(amount_txt)
        except ValueError:
            messagebox.showwarning("Validación", "El monto debe ser numérico.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE services
                SET client_id=%s, description=%s, service_date=%s, amount=%s, status=%s
                WHERE id=%s
            """, (client_id, desc, service_date, amount, status, self.selected_id))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Servicio actualizado.")
            self.clear_form()
            self.load_services()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_service(self):
        if not self.selected_id:
            messagebox.showwarning("Validación", "Selecciona un servicio de la tabla.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este servicio?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM services WHERE id=%s", (self.selected_id,))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Servicio eliminado.")
            self.clear_form()
            self.load_services()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_services(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_services()
            return

        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            like = f"%{term}%"
            cur.execute("""
                SELECT s.id, s.client_id, c.full_name, s.description, s.service_date, s.amount, s.status
                FROM services s
                JOIN clients c ON c.id = s.client_id
                WHERE c.full_name LIKE %s OR s.description LIKE %s
                ORDER BY s.id DESC
            """, (like, like))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                self.tree.insert("", "end", values=(
                    r[0],
                    r[1],
                    r[2] or "",
                    r[3] or "",
                    str(r[4]) if r[4] is not None else "",
                    f"{float(r[5]):.2f}" if r[5] is not None else "0.00",
                    r[6] or ""
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))