import tkinter as tk
from tkinter import ttk, messagebox
from src.db.connection import get_connection


class EmployeesWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Empleados")
        self.geometry("980x560")
        self.resizable(False, False)

        self.selected_id = None

        tk.Label(self, text="Módulo de Empleados", font=("Arial", 14)).pack(pady=10)

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        form_frame = tk.LabelFrame(main_frame, text="Datos del empleado", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        self.full_name_var = tk.StringVar(master=self)
        self.dui_var = tk.StringVar(master=self)
        self.phone_var = tk.StringVar(master=self)
        self.position_var = tk.StringVar(master=self)
        self.salary_var = tk.StringVar(master=self)
        self.search_var = tk.StringVar(master=self)
        self.active_var = tk.IntVar(master=self, value=1)

        tk.Label(form_frame, text="Nombre completo:").grid(row=0, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.full_name_var, width=30).grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="DUI:").grid(row=1, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.dui_var, width=30).grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Teléfono:").grid(row=2, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.phone_var, width=30).grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Cargo/Puesto:").grid(row=3, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.position_var, width=30).grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Salario ($):").grid(row=4, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.salary_var, width=30).grid(row=4, column=1, pady=5)

        tk.Checkbutton(form_frame, text="Activo", variable=self.active_var).grid(row=5, column=1, sticky="w", pady=(8, 4))

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)

        ttk.Button(btn_frame, text="Guardar", command=self.save_employee).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Actualizar", command=self.update_employee).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_employee).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        tk.Label(
            form_frame,
            text="Tip: selecciona un empleado de la tabla para editar o eliminar.",
            fg="gray"
        ).grid(row=7, column=0, columnspan=2, pady=(8, 0))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = tk.LabelFrame(right_frame, text="Buscar", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="Nombre o DUI:").grid(row=0, column=0, sticky="w")
        tk.Entry(search_frame, textvariable=self.search_var, width=35).grid(row=0, column=1, padx=6)
        ttk.Button(search_frame, text="Buscar", command=self.search_employees).grid(row=0, column=2, padx=4)
        ttk.Button(search_frame, text="Ver todos", command=self.load_employees).grid(row=0, column=3, padx=4)

        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "full_name", "dui", "phone", "position", "salary", "active")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        self.tree.heading("id", text="ID")
        self.tree.heading("full_name", text="Nombre")
        self.tree.heading("dui", text="DUI")
        self.tree.heading("phone", text="Teléfono")
        self.tree.heading("position", text="Cargo")
        self.tree.heading("salary", text="Salario")
        self.tree.heading("active", text="Activo")

        self.tree.column("id", width=50)
        self.tree.column("full_name", width=220)
        self.tree.column("dui", width=120)
        self.tree.column("phone", width=120)
        self.tree.column("position", width=160)
        self.tree.column("salary", width=90)
        self.tree.column("active", width=80)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_employees()

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def clear_form(self):
        self.selected_id = None
        self.full_name_var.set("")
        self.dui_var.set("")
        self.phone_var.set("")
        self.position_var.set("")
        self.salary_var.set("")
        self.active_var.set(1)

    def load_employees(self):
        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, full_name, dui, phone, position, salary, active
                FROM employees
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
                    r[4] or "",
                    f"{float(r[5]):.2f}" if r[5] is not None else "0.00",
                    "Sí" if r[6] else "No"
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_employees(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_employees()
            return

        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            like = f"%{term}%"
            cur.execute("""
                SELECT id, full_name, dui, phone, position, salary, active
                FROM employees
                WHERE full_name LIKE %s OR dui LIKE %s
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
                    r[4] or "",
                    f"{float(r[5]):.2f}" if r[5] is not None else "0.00",
                    "Sí" if r[6] else "No"
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_employee(self):
        full_name = self.full_name_var.get().strip()
        dui = self.dui_var.get().strip()
        phone = self.phone_var.get().strip()
        position = self.position_var.get().strip()
        salary_txt = self.salary_var.get().strip()
        active = self.active_var.get()

        if not full_name:
            messagebox.showwarning("Validación", "El nombre completo es obligatorio.")
            return

        try:
            salary = float(salary_txt) if salary_txt else 0.0
        except ValueError:
            messagebox.showwarning("Validación", "El salario debe ser numérico.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO employees (full_name, dui, phone, position, salary, active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (full_name, dui or None, phone or None, position or None, salary, active))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Empleado guardado.")
            self.clear_form()
            self.load_employees()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_employee(self):
        if not self.selected_id:
            messagebox.showwarning("Actualizar", "Selecciona un empleado de la tabla primero.")
            return

        full_name = self.full_name_var.get().strip()
        dui = self.dui_var.get().strip()
        phone = self.phone_var.get().strip()
        position = self.position_var.get().strip()
        salary_txt = self.salary_var.get().strip()
        active = self.active_var.get()

        if not full_name:
            messagebox.showwarning("Validación", "El nombre completo es obligatorio.")
            return

        try:
            salary = float(salary_txt) if salary_txt else 0.0
        except ValueError:
            messagebox.showwarning("Validación", "El salario debe ser numérico.")
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE employees
                SET full_name=%s, dui=%s, phone=%s, position=%s, salary=%s, active=%s
                WHERE id=%s
            """, (full_name, dui or None, phone or None, position or None, salary, active, self.selected_id))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Empleado actualizado.")
            self.clear_form()
            self.load_employees()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_employee(self):
        if not self.selected_id:
            messagebox.showwarning("Eliminar", "Selecciona un empleado de la tabla primero.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este empleado?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM employees WHERE id=%s", (self.selected_id,))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Empleado eliminado.")
            self.clear_form()
            self.load_employees()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])

        self.full_name_var.set(values[1])
        self.dui_var.set(values[2])
        self.phone_var.set(values[3])
        self.position_var.set(values[4])
        self.salary_var.set(values[5])
        self.active_var.set(1 if values[6] == "Sí" else 0)