import tkinter as tk
from tkinter import ttk, messagebox
from src.db.connection import get_connection


class InventoryWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Inventario")
        self.geometry("1020x560")
        self.resizable(False, False)

        self.selected_id = None

        tk.Label(self, text="Módulo de Inventario", font=("Arial", 14)).pack(pady=10)

        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        form_frame = tk.LabelFrame(main_frame, text="Producto", padx=10, pady=10)
        form_frame.pack(side="left", fill="y", padx=(0, 10))

        self.product_var = tk.StringVar(master=self)
        self.unit_var = tk.StringVar(master=self)
        self.qty_var = tk.StringVar(master=self)
        self.min_var = tk.StringVar(master=self)
        self.cost_var = tk.StringVar(master=self)

        tk.Label(form_frame, text="Nombre del producto:").grid(row=0, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.product_var, width=32).grid(row=0, column=1, pady=5)

        tk.Label(form_frame, text="Unidad (ej: unidad, litro):").grid(row=1, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.unit_var, width=32).grid(row=1, column=1, pady=5)

        tk.Label(form_frame, text="Cantidad (stock):").grid(row=2, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.qty_var, width=32).grid(row=2, column=1, pady=5)

        tk.Label(form_frame, text="Stock mínimo:").grid(row=3, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.min_var, width=32).grid(row=3, column=1, pady=5)

        tk.Label(form_frame, text="Costo ($):").grid(row=4, column=0, sticky="w")
        tk.Entry(form_frame, textvariable=self.cost_var, width=32).grid(row=4, column=1, pady=5)

        tk.Label(form_frame, text="Notas:").grid(row=5, column=0, sticky="nw")
        self.notes_text = tk.Text(form_frame, width=30, height=5)
        self.notes_text.grid(row=5, column=1, pady=5)

        btn_frame = tk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=12)

        ttk.Button(btn_frame, text="Guardar", command=self.save_item).grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Actualizar", command=self.update_item).grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Eliminar", command=self.delete_item).grid(row=0, column=2, padx=4)
        ttk.Button(btn_frame, text="Limpiar", command=self.clear_form).grid(row=0, column=3, padx=4)

        tk.Label(
            form_frame,
            text="Alerta: si Cantidad <= Stock mínimo se mostrará como BAJO.",
            fg="gray"
        ).grid(row=7, column=0, columnspan=2, pady=(8, 0))

        right_frame = tk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        search_frame = tk.LabelFrame(right_frame, text="Buscar", padx=10, pady=10)
        search_frame.pack(fill="x", pady=(0, 10))

        self.search_var = tk.StringVar(master=self)
        tk.Label(search_frame, text="Producto:").grid(row=0, column=0, sticky="w")
        tk.Entry(search_frame, textvariable=self.search_var, width=40).grid(row=0, column=1, padx=6)
        ttk.Button(search_frame, text="Buscar", command=self.search_items).grid(row=0, column=2, padx=4)
        ttk.Button(search_frame, text="Ver todos", command=self.load_items).grid(row=0, column=3, padx=4)

        table_frame = tk.Frame(right_frame)
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "product_name", "unit", "quantity", "min_stock", "cost", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=18)

        self.tree.heading("id", text="ID")
        self.tree.heading("product_name", text="Producto")
        self.tree.heading("unit", text="Unidad")
        self.tree.heading("quantity", text="Cantidad")
        self.tree.heading("min_stock", text="Mínimo")
        self.tree.heading("cost", text="Costo")
        self.tree.heading("status", text="Estado")

        self.tree.column("id", width=50)
        self.tree.column("product_name", width=220)
        self.tree.column("unit", width=120)
        self.tree.column("quantity", width=90)
        self.tree.column("min_stock", width=90)
        self.tree.column("cost", width=90)
        self.tree.column("status", width=90)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        self.load_items()

    def clear_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

    def clear_form(self):
        self.selected_id = None
        self.product_var.set("")
        self.unit_var.set("")
        self.qty_var.set("")
        self.min_var.set("")
        self.cost_var.set("")
        self.notes_text.delete("1.0", "end")

    def load_items(self):
        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT id, product_name, unit, quantity, min_stock, cost, notes
                FROM inventory
                ORDER BY id DESC
            """)
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                qty = r[3] if r[3] is not None else 0
                min_s = r[4] if r[4] is not None else 0
                status = "BAJO" if qty <= min_s else "OK"
                cost = f"{float(r[5]):.2f}" if r[5] is not None else ""

                self.tree.insert("", "end", values=(
                    r[0],
                    r[1] or "",
                    r[2] or "",
                    qty,
                    min_s,
                    cost,
                    status
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def search_items(self):
        term = self.search_var.get().strip()
        if not term:
            self.load_items()
            return

        self.clear_table()
        try:
            conn = get_connection()
            cur = conn.cursor()
            like = f"%{term}%"
            cur.execute("""
                SELECT id, product_name, unit, quantity, min_stock, cost, notes
                FROM inventory
                WHERE product_name LIKE %s
                ORDER BY id DESC
            """, (like,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for r in rows:
                qty = r[3] if r[3] is not None else 0
                min_s = r[4] if r[4] is not None else 0
                status = "BAJO" if qty <= min_s else "OK"
                cost = f"{float(r[5]):.2f}" if r[5] is not None else ""

                self.tree.insert("", "end", values=(
                    r[0],
                    r[1] or "",
                    r[2] or "",
                    qty,
                    min_s,
                    cost,
                    status
                ))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def save_item(self):
        product = self.product_var.get().strip()
        unit = self.unit_var.get().strip()
        qty_txt = self.qty_var.get().strip()
        min_txt = self.min_var.get().strip()
        cost_txt = self.cost_var.get().strip()
        notes = self.notes_text.get("1.0", "end").strip()

        if not product:
            messagebox.showwarning("Validación", "El nombre del producto es obligatorio.")
            return
        if not unit:
            messagebox.showwarning("Validación", "La unidad es obligatoria.")
            return

        try:
            qty = int(qty_txt) if qty_txt else 0
            min_s = int(min_txt) if min_txt else 0
        except ValueError:
            messagebox.showwarning("Validación", "Cantidad y stock mínimo deben ser números enteros.")
            return

        cost = None
        if cost_txt:
            try:
                cost = float(cost_txt)
            except ValueError:
                messagebox.showwarning("Validación", "Costo debe ser numérico.")
                return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO inventory (product_name, unit, quantity, min_stock, cost, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (product, unit, qty, min_s, cost, notes or None))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Producto guardado.")
            self.clear_form()
            self.load_items()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_item(self):
        if not self.selected_id:
            messagebox.showwarning("Actualizar", "Selecciona un producto de la tabla primero.")
            return

        product = self.product_var.get().strip()
        unit = self.unit_var.get().strip()
        qty_txt = self.qty_var.get().strip()
        min_txt = self.min_var.get().strip()
        cost_txt = self.cost_var.get().strip()
        notes = self.notes_text.get("1.0", "end").strip()

        if not product:
            messagebox.showwarning("Validación", "El nombre del producto es obligatorio.")
            return
        if not unit:
            messagebox.showwarning("Validación", "La unidad es obligatoria.")
            return

        try:
            qty = int(qty_txt) if qty_txt else 0
            min_s = int(min_txt) if min_txt else 0
        except ValueError:
            messagebox.showwarning("Validación", "Cantidad y stock mínimo deben ser números enteros.")
            return

        cost = None
        if cost_txt:
            try:
                cost = float(cost_txt)
            except ValueError:
                messagebox.showwarning("Validación", "Costo debe ser numérico.")
                return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("""
                UPDATE inventory
                SET product_name=%s, unit=%s, quantity=%s, min_stock=%s, cost=%s, notes=%s
                WHERE id=%s
            """, (product, unit, qty, min_s, cost, notes or None, self.selected_id))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Producto actualizado.")
            self.clear_form()
            self.load_items()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_item(self):
        if not self.selected_id:
            messagebox.showwarning("Eliminar", "Selecciona un producto de la tabla primero.")
            return

        if not messagebox.askyesno("Confirmar", "¿Eliminar este producto del inventario?"):
            return

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM inventory WHERE id=%s", (self.selected_id,))
            conn.commit()
            cur.close()
            conn.close()

            messagebox.showinfo("OK", "Producto eliminado.")
            self.clear_form()
            self.load_items()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        values = self.tree.item(sel[0], "values")
        self.selected_id = int(values[0])

        self.product_var.set(values[1])
        self.unit_var.set(values[2])
        self.qty_var.set(values[3])
        self.min_var.set(values[4])
        self.cost_var.set(values[5])

        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT notes FROM inventory WHERE id=%s", (self.selected_id,))
            row = cur.fetchone()
            cur.close()
            conn.close()

            self.notes_text.delete("1.0", "end")
            self.notes_text.insert("1.0", row[0] if row and row[0] else "")

        except Exception as e:
            messagebox.showerror("Error", str(e))