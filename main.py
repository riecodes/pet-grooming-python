import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import mysql.connector
from datetime import datetime
import os
from db_config import create_connection
from receipt_generator import generate_receipt

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Emoji icons for services
SERVICE_ICONS = {
    'Nail Trim and Filing': '🐾',
    'Teeth Brushing': '🪥',
    'Eye Wash': '👁️',
    'Ear Cleaning': '👂',
    'Frontline Application': '💧',
    'Anal Drain': '🐶',
    'Facial Trimming': '✂️',
    'Paw Shaving / Poodle Foot': '🐕',
    'Butt & Belly Shaving': '🐩',
    'Dematting (Small Breed)': '🦴',
    'Dematting (Medium Breed)': '🦴',
    'Dematting (Large Breed)': '🦴',
    'Dematting (X-Large Breed)': '🦴',
}

COMMON_PET_TYPES = ["Dog", "Cat"]

PASTEL_BLUE = '#e3f0fc'
PASTEL_PEACH = '#ffe5d0'
PASTEL_WHITE = '#f9f9fb'
PASTEL_ACCENT = '#f7b267'
SIDEBAR_WIDTH = 200

class PawBuddyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PawBuddy Grooming Services")
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.selected_services = set()
        self.service_vars = {}
        self.services_data = []
        self.total_amount = 0.0
        self.configure(bg="#e3f0fc")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.create_sidebar()
        self.create_main_area()
        self.load_services()

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#3b8ed0")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        mascot = ctk.CTkLabel(self.sidebar, text="🐶", font=("Segoe UI", 48), fg_color="#3b8ed0")
        mascot.pack(pady=(30, 10))
        brand = ctk.CTkLabel(self.sidebar, text="PawBuddy", font=("Segoe UI", 22, "bold"), text_color="#f77f00", fg_color="#3b8ed0")
        brand.pack(pady=(0, 30))
        ctk.CTkButton(self.sidebar, text="🏠  Home", corner_radius=20, fg_color="#f7b267", hover_color="#f9c784", text_color="white").pack(fill="x", pady=8, padx=30)
        ctk.CTkButton(self.sidebar, text="🧾  Generate PDF", corner_radius=20, fg_color="#f7b267", hover_color="#f9c784", text_color="white", command=self.generate_receipt).pack(fill="x", pady=8, padx=30)

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#f9f9fb")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Customer & Pet Info Section
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        info_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
        info_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(info_frame, text="Customer Details", font=("Segoe UI", 18, "bold"), text_color="#222").grid(row=0, column=0, sticky="w", pady=(0, 10), columnspan=2)
        ctk.CTkLabel(info_frame, text="Pet Details", font=("Segoe UI", 18, "bold"), text_color="#222").grid(row=0, column=2, sticky="w", pady=(0, 10), columnspan=2)

        # Customer fields
        self.customer_name = ctk.CTkEntry(info_frame, placeholder_text="Customer Name", font=("Segoe UI", 13))
        self.customer_name.grid(row=1, column=0, padx=8, pady=5, sticky="ew")
        self.customer_address = ctk.CTkEntry(info_frame, placeholder_text="Address", font=("Segoe UI", 13))
        self.customer_address.grid(row=1, column=1, padx=8, pady=5, sticky="ew")
        self.customer_phone = ctk.CTkEntry(info_frame, placeholder_text="Phone Number", font=("Segoe UI", 13))
        self.customer_phone.grid(row=2, column=0, padx=8, pady=5, sticky="ew")

        # Pet fields
        self.pet_type = ctk.CTkOptionMenu(info_frame, values=COMMON_PET_TYPES, font=("Segoe UI", 13), width=180)
        self.pet_type.set(COMMON_PET_TYPES[0])
        self.pet_type.grid(row=1, column=2, padx=8, pady=5, sticky="ew")
        self.pet_name = ctk.CTkEntry(info_frame, placeholder_text="Pet Name", font=("Segoe UI", 13))
        self.pet_name.grid(row=1, column=3, padx=8, pady=5, sticky="ew")
        self.pet_breed = ctk.CTkEntry(info_frame, placeholder_text="Breed", font=("Segoe UI", 13))
        self.pet_breed.grid(row=2, column=2, padx=8, pady=5, sticky="ew")
        self.pet_count = ctk.CTkEntry(info_frame, placeholder_text="Number of Pets", font=("Segoe UI", 13))
        self.pet_count.grid(row=2, column=3, padx=8, pady=5, sticky="ew")
        self.pet_count.bind('<KeyRelease>', self._validate_number_entry)

        # Search Bar with icon
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        search_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(10, 0))
        search_frame.grid_columnconfigure(1, weight=1)
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 16), fg_color="#f9f9fb")
        search_icon.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.update_service_slider)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Search services...", font=("Segoe UI", 13))
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=0, pady=0)

        # Horizontal Scrollable Service Slider
        slider_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        slider_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 0))
        slider_frame.grid_rowconfigure(0, weight=1)
        slider_frame.grid_columnconfigure(0, weight=1)
        self.services_canvas = tk.Canvas(slider_frame, bg="#f9f9fb", highlightthickness=0, height=320)
        self.services_canvas.grid(row=0, column=0, sticky="nsew")
        self.h_scrollbar = ctk.CTkScrollbar(slider_frame, orientation="horizontal", command=self.services_canvas.xview)
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        self.services_canvas.configure(xscrollcommand=self.h_scrollbar.set)
        self.services_frame = ctk.CTkFrame(self.services_canvas, fg_color="#f9f9fb")
        self.services_window = self.services_canvas.create_window((0, 0), window=self.services_frame, anchor="nw")
        self.services_frame.bind("<Configure>", self._on_frame_configure_slider)
        self.services_canvas.bind('<Configure>', self._on_canvas_configure_slider)

        # Running Total
        self.total_label = ctk.CTkLabel(self.main_frame, text="Total: P0.00", font=("Segoe UI", 16, "bold"), text_color="#f77f00")
        self.total_label.grid(row=3, column=0, sticky="e", pady=(20, 20), padx=(0, 40))

    def _validate_number_entry(self, event):
        value = self.pet_count.get()
        if not value.isdigit():
            self.pet_count.delete(0, 'end')
            self.pet_count.insert(0, ''.join(filter(str.isdigit, value)))

    def _on_frame_configure_slider(self, event):
        self.services_canvas.configure(scrollregion=self.services_canvas.bbox("all"))
        self.services_canvas.itemconfig(self.services_window, height=self.services_canvas.winfo_height())

    def _on_canvas_configure_slider(self, event):
        self.services_canvas.itemconfig(self.services_window, height=event.height)

    def load_services(self):
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT name, price FROM services ORDER BY name")
                self.services_data = cursor.fetchall()
                cursor.close()
                connection.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading services: {err}")
        self.update_service_slider()

    def update_service_slider(self, *args):
        for widget in self.services_frame.winfo_children():
            widget.destroy()
        self.service_vars.clear()
        self.selected_services.clear()
        self.total_amount = 0.0
        self.total_label.configure(text='Total: P0.00')
        search = self.search_var.get().lower()
        filtered_services = [s for s in self.services_data if search in s[0].lower()]
        card_width = 220
        for idx, (name, price) in enumerate(filtered_services):
            card = ctk.CTkFrame(self.services_frame, fg_color="#ffe5d0", corner_radius=18, width=card_width, height=280)
            card.grid(row=0, column=idx, padx=12, pady=12, sticky="n")
            card.grid_propagate(False)
            icon = ctk.CTkLabel(card, text=SERVICE_ICONS.get(name, '🐾'), font=("Segoe UI", 28), fg_color="#ffe5d0")
            icon.pack(pady=(0, 5))
            label = ctk.CTkLabel(card, text=name.replace(' / ', '\n'), font=("Segoe UI", 13, "bold"), fg_color="#ffe5d0")
            label.pack()
            price_label = ctk.CTkLabel(card, text=f'P{int(price)}', font=("Segoe UI", 13), fg_color="#ffe5d0")
            price_label.pack()
            var = tk.BooleanVar()
            chk = ctk.CTkCheckBox(card, variable=var, text="Select", font=("Segoe UI", 12, "bold"), fg_color="#f7b267", hover_color="#f9c784", border_width=2, corner_radius=10, command=self.update_total)
            chk.pack(pady=5)
            self.service_vars[name] = (var, price)
        self.services_canvas.update_idletasks()
        self.services_canvas.configure(scrollregion=self.services_canvas.bbox("all"))

    def update_total(self):
        self.selected_services.clear()
        self.total_amount = 0.0
        for name, (var, price) in self.service_vars.items():
            if var.get():
                self.selected_services.add((name, price))
                self.total_amount += float(price)
        self.total_label.configure(text=f'Total: P{self.total_amount:.2f}')

    def generate_receipt(self):
        if not self.selected_services:
            messagebox.showwarning("Warning", "Please select at least one service")
            return
        if not self.customer_name.get():
            messagebox.showwarning("Warning", "Please enter customer name")
            return
        if not os.path.exists("receipts"):
            os.makedirs("receipts")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"receipts/receipt_{timestamp}.pdf"
        try:
            generate_receipt(
                self.customer_name.get(),
                list(self.selected_services),
                self.total_amount,
                filename,
                address=self.customer_address.get(),
                phone=self.customer_phone.get(),
                pet_name=self.pet_name.get(),
                pet_type=self.pet_type.get() if hasattr(self.pet_type, 'get') else self.pet_type,
                breed=self.pet_breed.get(),
                num_pets=self.pet_count.get()
            )
            messagebox.showinfo("Success", f"Receipt generated successfully!\nSaved as: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating receipt: {str(e)}")

if __name__ == "__main__":
    app = PawBuddyApp()
    app.mainloop() 