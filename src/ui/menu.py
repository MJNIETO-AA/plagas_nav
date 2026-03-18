import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk

from src.db.connection import get_connection
from src.modules.employees import EmployeesWindow
from src.modules.clients import ClientsWindow
from src.modules.services import ServicesWindow
from src.modules.inventory import InventoryWindow
from src.reports.services_report import export_services_excel, export_services_pdf
from src.reports.general_reports import (
    export_clients_excel, export_clients_pdf,
    export_employees_excel, export_employees_pdf,
    export_inventory_excel, export_inventory_pdf
)
from src.db.backup_db import create_backup
from tkinter import messagebox


class MainMenu(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.user = user

        self.title("Plagas Navarro - Menú Principal")
        self.geometry("780x700")
        self.resizable(True, True)

        self.protocol("WM_DELETE_WINDOW", self.close_session)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        logo_path = os.path.join(base_path, "assets", "logo.jpg")
       

        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            img = img.resize((120, 120), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)

            logo_label = tk.Label(self.scrollable_frame, image=self.logo_img)
            logo_label.pack(pady=(15, 5))

        title = tk.Label(self.scrollable_frame, text="Menú Principal", font=("Arial", 18, "bold"))
        title.pack(pady=(10, 6))

        subtitle = tk.Label(
            self.scrollable_frame,
            text=f"Bienvenido, {self.user.get('username', 'Usuario')}",
            font=("Arial", 11)
        )
        subtitle.pack(pady=(0, 4))

        self.datetime_label = tk.Label(self.scrollable_frame, text="", font=("Arial", 10), fg="gray")
        self.datetime_label.pack(pady=(0, 12))

        dashboard_frame = tk.Frame(self.scrollable_frame)
        dashboard_frame.pack(pady=10)

        self.card_employees = self.create_card(dashboard_frame, "Empleados", "0", 0, 0)
        self.card_clients = self.create_card(dashboard_frame, "Clientes", "0", 0, 1)
        self.card_services = self.create_card(dashboard_frame, "Servicios", "0", 1, 0)
        self.card_low_stock = self.create_card(dashboard_frame, "Stock bajo", "0", 1, 1)

        btn_refresh = ttk.Button(self.scrollable_frame, text="Actualizar resumen", command=self.load_dashboard)
        btn_refresh.pack(pady=(4, 10))

        reports_frame = tk.LabelFrame(self.scrollable_frame, text="Reportes", padx=10, pady=10)
        reports_frame.pack(pady=(0, 14))

        ttk.Button(reports_frame, text="Servicios Excel", command=self.export_services_excel_ui).grid(row=0, column=0, padx=6, pady=4)
        ttk.Button(reports_frame, text="Servicios PDF", command=self.export_services_pdf_ui).grid(row=0, column=1, padx=6, pady=4)

        ttk.Button(reports_frame, text="Clientes Excel", command=self.export_clients_excel_ui).grid(row=1, column=0, padx=6, pady=4)
        ttk.Button(reports_frame, text="Clientes PDF", command=self.export_clients_pdf_ui).grid(row=1, column=1, padx=6, pady=4)

        ttk.Button(reports_frame, text="Empleados Excel", command=self.export_employees_excel_ui).grid(row=2, column=0, padx=6, pady=4)
        ttk.Button(reports_frame, text="Empleados PDF", command=self.export_employees_pdf_ui).grid(row=2, column=1, padx=6, pady=4)

        ttk.Button(reports_frame, text="Inventario Excel", command=self.export_inventory_excel_ui).grid(row=3, column=0, padx=6, pady=4)
        ttk.Button(reports_frame, text="Inventario PDF", command=self.export_inventory_pdf_ui).grid(row=3, column=1, padx=6, pady=4)

        menu_frame = tk.Frame(self.scrollable_frame)
        menu_frame.pack(pady=10)

        ttk.Button(menu_frame, text="Empleados", width=28, command=self.open_employees).pack(pady=6)
        ttk.Button(menu_frame, text="Clientes", width=28, command=self.open_clients).pack(pady=6)
        ttk.Button(menu_frame, text="Servicios / Pagos", width=28, command=self.open_services).pack(pady=6)
        ttk.Button(menu_frame, text="Inventario", width=28, command=self.open_inventory).pack(pady=6)
        ttk.Button(menu_frame, text="Cerrar sesión", width=28, command=self.close_session).pack(pady=20)

        btn_backup = tk.Button(
              self,
              text="Crear respaldo de base de datos",
              width=30,
              command=self.backup_database
        )

        btn_backup.pack(pady=5)

        self.load_dashboard()
        self.update_datetime()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def create_card(self, parent, title, value, row, col):
        frame = tk.LabelFrame(parent, text=title, padx=20, pady=16)
        frame.grid(row=row, column=col, padx=12, pady=10, sticky="nsew")

        value_label = tk.Label(frame, text=value, font=("Arial", 20, "bold"), width=10)
        value_label.pack()

        return value_label

    def update_datetime(self):
        now = datetime.now()
        formatted = now.strftime("%d/%m/%Y  %I:%M:%S %p")
        self.datetime_label.config(text=formatted)
        self.after(1000, self.update_datetime)

    def load_dashboard(self):
        try:
            conn = get_connection()
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM employees")
            employees_total = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM clients")
            clients_total = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM services")
            services_total = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= min_stock")
            low_stock_total = cur.fetchone()[0]

            cur.close()
            conn.close()

            self.card_employees.config(text=str(employees_total))
            self.card_clients.config(text=str(clients_total))
            self.card_services.config(text=str(services_total))
            self.card_low_stock.config(text=str(low_stock_total))

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_services_excel_ui(self):
        try:
            path = export_services_excel()
            messagebox.showinfo("Reporte generado", f"Excel generado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_services_pdf_ui(self):
        try:
            path = export_services_pdf()
            messagebox.showinfo("Reporte generado", f"PDF generado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_employees(self):
        EmployeesWindow(self)

    def open_clients(self):
        ClientsWindow(self)

    def open_services(self):
        ServicesWindow(self)

    def open_inventory(self):
        InventoryWindow(self)

    def export_clients_excel_ui(self):
        try:
            path = export_clients_excel()
            messagebox.showinfo("Reporte generado", f"Excel de clientes generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_clients_pdf_ui(self):
        try:
            path = export_clients_pdf()
            messagebox.showinfo("Reporte generado", f"PDF de clientes generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_employees_excel_ui(self):
        try:
            path = export_employees_excel()
            messagebox.showinfo("Reporte generado", f"Excel de empleados generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_employees_pdf_ui(self):
        try:
            path = export_employees_pdf()
            messagebox.showinfo("Reporte generado", f"PDF de empleados generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_inventory_excel_ui(self):
        try:
            path = export_inventory_excel()
            messagebox.showinfo("Reporte generado", f"Excel de inventario generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_inventory_pdf_ui(self):
        try:
            path = export_inventory_pdf()
            messagebox.showinfo("Reporte generado", f"PDF de inventario generado:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def backup_database(self):
        try:
            path = create_backup()
            messagebox.showinfo("Backup", f"Respaldo creado correctamente:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def close_session(self):
        self.destroy()
        if isinstance(self.master, tk.Tk):
            self.master.deiconify()