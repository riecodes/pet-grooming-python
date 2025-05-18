import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime, timedelta
import os
from db_config import create_connection
from receipt_generator import generate_receipt
from tkcalendar import DateEntry
import tkinter.ttk as ttk

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
        
        # Initialize views
        self.create_sidebar()
        self.create_main_area()
        self.create_reservations_view()
        self.load_services()
        
        # Set initial view
        self.current_view = "home"
        self.reservations_frame.grid_remove()  # Hide reservations view initially

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, fg_color="#3b8ed0")
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        mascot = ctk.CTkLabel(self.sidebar, text="🐶", font=("Segoe UI", 48), fg_color="#3b8ed0")
        mascot.pack(pady=(30, 10))
        brand = ctk.CTkLabel(self.sidebar, text="PawBuddy", font=("Segoe UI", 22, "bold"), text_color="#f77f00", fg_color="#3b8ed0")
        brand.pack(pady=(0, 30))
        
        # Home button
        self.home_btn = ctk.CTkButton(
            self.sidebar, 
            text="🏠  Home", 
            corner_radius=20, 
            fg_color="#f7b267", 
            hover_color="#f9c784", 
            text_color="white",
            command=lambda: self.switch_view("home")
        )
        self.home_btn.pack(fill="x", pady=8, padx=30)
        
        # Reservations button
        self.reservations_btn = ctk.CTkButton(
            self.sidebar, 
            text="📅  Reservations", 
            corner_radius=20, 
            fg_color="#f7b267", 
            hover_color="#f9c784", 
            text_color="white",
            command=lambda: self.switch_view("reservations")
        )
        self.reservations_btn.pack(fill="x", pady=8, padx=30)
        
        # Generate PDF button
        self.pdf_btn = ctk.CTkButton(
            self.sidebar, 
            text="🧾  Generate PDF", 
            corner_radius=20, 
            fg_color="#f7b267", 
            hover_color="#f9c784", 
            text_color="white", 
            command=self.generate_receipt
        )
        self.pdf_btn.pack(fill="x", pady=8, padx=30)

    def switch_view(self, view):
        self.current_view = view
        if view == "home":
            self.main_frame.grid()
            self.reservations_frame.grid_remove()
        else:
            self.main_frame.grid_remove()
            self.reservations_frame.grid()
            self.load_reservations()  # Refresh reservations when switching to that view

    def create_reservations_view(self):
        if not hasattr(self, 'reservations_frame'):
            self.reservations_frame = ctk.CTkFrame(self, fg_color="#f9f9fb")
            self.reservations_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
            self.reservations_frame.grid_rowconfigure(1, weight=1)
            self.reservations_frame.grid_columnconfigure(0, weight=1)

            # Header
            header = ctk.CTkFrame(self.reservations_frame, fg_color="#f9f9fb")
            header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
            header.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                header, 
                text="Reservations", 
                font=("Segoe UI", 24, "bold"), 
                text_color="#222"
            ).grid(row=0, column=0, sticky="w", pady=(0, 20))

            # Reservations list
            self.reservations_tree = ttk.Treeview(
                self.reservations_frame,
                columns=("ID", "Customer", "Pet", "Date", "Services", "Total", "Status"),
                show="headings",
                style="Custom.Treeview"
            )
            
            # Configure columns
            self.reservations_tree.heading("ID", text="ID")
            self.reservations_tree.heading("Customer", text="Customer")
            self.reservations_tree.heading("Pet", text="Pet")
            self.reservations_tree.heading("Date", text="Date")
            self.reservations_tree.heading("Services", text="Services")
            self.reservations_tree.heading("Total", text="Total")
            self.reservations_tree.heading("Status", text="Status")

            self.reservations_tree.column("ID", width=50)
            self.reservations_tree.column("Customer", width=150)
            self.reservations_tree.column("Pet", width=100)
            self.reservations_tree.column("Date", width=150)
            self.reservations_tree.column("Services", width=200)
            self.reservations_tree.column("Total", width=100)
            self.reservations_tree.column("Status", width=100)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(
                self.reservations_frame,
                orient="vertical",
                command=self.reservations_tree.yview
            )
            self.reservations_tree.configure(yscrollcommand=scrollbar.set)

            # Grid the tree and scrollbar
            self.reservations_tree.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
            scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 20))

            # Add right-click menu for edit/delete
            self.reservation_menu = tk.Menu(self, tearoff=0)
            self.reservation_menu.add_command(label="Edit", command=self.edit_reservation)
            self.reservation_menu.add_command(label="Delete", command=self.delete_reservation)
            self.reservations_tree.bind("<Button-3>", self.show_reservation_menu)

        self.reservations_frame.grid()
        self.load_reservations()

    def show_reservation_menu(self, event):
        item = self.reservations_tree.identify_row(event.y)
        if item:
            self.reservations_tree.selection_set(item)
            self.reservation_menu.post(event.x_root, event.y_root)

    def show_reservation_dialog(self, edit_mode=False, booking_id=None):
        if edit_mode:
            self.show_edit_reservation_dialog(booking_id)
        else:
            self.show_new_reservation_dialog()

    def show_new_reservation_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("New Reservation")
        dialog.geometry("1000x600")
        dialog.grab_set()

        # Main container with padding
        main_container = ctk.CTkFrame(dialog, fg_color="#f9f9fb")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create two columns
        left_frame = ctk.CTkFrame(main_container, fg_color="#f9f9fb")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ctk.CTkFrame(main_container, fg_color="#f9f9fb")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Date and Time Selection
        date_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        date_frame.pack(fill="x", pady=(0, 15))
        
        date_label = ctk.CTkLabel(date_frame, text="Date:", font=("Segoe UI", 14))
        date_label.pack(side="left", padx=(0, 10))
        
        date_picker = DateEntry(date_frame, width=12, background='#f7b267', foreground='white', borderwidth=2)
        date_picker.pack(side="left", padx=(0, 20))
        
        time_label = ctk.CTkLabel(date_frame, text="Time:", font=("Segoe UI", 14))
        time_label.pack(side="left", padx=(0, 10))
        
        time_picker = ttk.Combobox(date_frame, values=[f"{h:02d}:{m:02d}" for h in range(9, 18) for m in (0, 30)], width=10)
        time_picker.pack(side="left")
        time_picker.set("09:00")

        # Customer Info Display
        customer_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        customer_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(customer_frame, text="Customer Information", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Display customer info from home view
        ctk.CTkLabel(customer_frame, text=f"Name: {self.customer_name.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        ctk.CTkLabel(customer_frame, text=f"Phone: {self.customer_phone.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        ctk.CTkLabel(customer_frame, text=f"Address: {self.customer_address.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)

        # Pet Info Display
        pet_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        pet_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(pet_frame, text="Pet Information", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Display pet info
        ctk.CTkLabel(pet_frame, text=f"Name: {self.pet_name.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        ctk.CTkLabel(pet_frame, text=f"Type: {self.pet_type.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        ctk.CTkLabel(pet_frame, text=f"Breed: {self.pet_breed.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        ctk.CTkLabel(pet_frame, text=f"Number of Pets: {self.pet_count.get()}", font=("Segoe UI", 14)).pack(anchor="w", padx=5)

        # Services Selection
        services_frame = ctk.CTkFrame(right_frame, fg_color="#f9f9fb")
        services_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(services_frame, text="Selected Services", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Display selected services
        services_list = ctk.CTkScrollableFrame(services_frame, width=300, height=400)
        services_list.pack(fill="both", expand=True, padx=5)
        
        for name, price in self.selected_services:
            service_frame = ctk.CTkFrame(services_list, fg_color="#ffe5d0", corner_radius=10)
            service_frame.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(
                service_frame,
                text=f"{SERVICE_ICONS.get(name, '🐾')} {name}",
                font=("Segoe UI", 12, "bold"),
                fg_color="#ffe5d0"
            ).pack(side="left", padx=10)
            
            ctk.CTkLabel(
                service_frame,
                text=f"P{price}",
                font=("Segoe UI", 12),
                fg_color="#ffe5d0"
            ).pack(side="right", padx=10)

        # Total amount display
        total_frame = ctk.CTkFrame(right_frame, fg_color="#f9f9fb")
        total_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(
            total_frame,
            text=f"Total Amount: P{self.total_amount:.2f}",
            font=("Segoe UI", 16, "bold"),
            text_color="#f77f00"
        ).pack(anchor="e", padx=10)

        def save_reservation():
            try:
                connection = create_connection()
                if connection:
                    cursor = connection.cursor()
                    
                    # Insert customer
                    cursor.execute(
                        "INSERT INTO customers (name, phone, address) VALUES (%s, %s, %s)",
                        (self.customer_name.get(), self.customer_phone.get(), self.customer_address.get())
                    )
                    customer_id = cursor.lastrowid
                    
                    # Insert pet
                    cursor.execute(
                        "INSERT INTO pets (customer_id, name, breed, num_pets) VALUES (%s, %s, %s, %s)",
                        (customer_id, self.pet_name.get(), self.pet_type.get(), int(self.pet_count.get() or 1))
                    )
                    pet_id = cursor.lastrowid
                    
                    # Insert booking
                    booking_date = datetime.combine(date_picker.get_date(), datetime.strptime(time_picker.get(), "%H:%M").time())
                    cursor.execute(
                        "INSERT INTO bookings (customer_id, pet_id, booking_date, total_amount, status) VALUES (%s, %s, %s, %s, %s)",
                        (customer_id, pet_id, booking_date, self.total_amount, "pending")
                    )
                    booking_id = cursor.lastrowid
                    
                    # Insert booking services
                    for service_name, price in self.selected_services:
                        cursor.execute(
                            "SELECT id FROM services WHERE name = %s",
                            (service_name,)
                        )
                        service_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO booking_services (booking_id, service_id, price) VALUES (%s, %s, %s)",
                            (booking_id, service_id, price)
                        )
                    
                    connection.commit()
                    messagebox.showinfo("Success", "Reservation saved successfully!")
                    dialog.destroy()
                    self.load_reservations()
                    
                    # Clear the home view fields after successful save
                    self.customer_name.delete(0, 'end')
                    self.customer_phone.delete(0, 'end')
                    self.customer_address.delete(0, 'end')
                    self.pet_name.delete(0, 'end')
                    self.pet_breed.delete(0, 'end')
                    self.pet_count.delete(0, 'end')
                    self.pet_type.set(COMMON_PET_TYPES[0])
                    self.selected_services.clear()
                    self.total_amount = 0.0
                    self.total_label.configure(text='Total: P0.00')
                    self.validate_reservation_fields()
                    
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error saving reservation: {err}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        # Save button
        ctk.CTkButton(
            main_container,
            text="Save Reservation",
            corner_radius=20,
            fg_color="#f7b267",
            hover_color="#f9c784",
            text_color="white",
            command=save_reservation,
            height=40
        ).pack(side="bottom", pady=(20, 0))

    def show_edit_reservation_dialog(self, booking_id):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Reservation")
        dialog.geometry("1000x600")
        dialog.grab_set()

        # Main container with padding
        main_container = ctk.CTkFrame(dialog, fg_color="#f9f9fb")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Create two columns
        left_frame = ctk.CTkFrame(main_container, fg_color="#f9f9fb")
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        right_frame = ctk.CTkFrame(main_container, fg_color="#f9f9fb")
        right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Date and Time Selection
        date_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        date_frame.pack(fill="x", pady=(0, 15))
        
        date_label = ctk.CTkLabel(date_frame, text="Date:", font=("Segoe UI", 14))
        date_label.pack(side="left", padx=(0, 10))
        
        date_picker = DateEntry(date_frame, width=12, background='#f7b267', foreground='white', borderwidth=2)
        date_picker.pack(side="left", padx=(0, 20))
        
        time_label = ctk.CTkLabel(date_frame, text="Time:", font=("Segoe UI", 14))
        time_label.pack(side="left", padx=(0, 10))
        
        time_picker = ttk.Combobox(date_frame, values=[f"{h:02d}:{m:02d}" for h in range(9, 18) for m in (0, 30)], width=10)
        time_picker.pack(side="left")
        time_picker.set("09:00")

        # Customer Info Frame
        customer_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        customer_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(customer_frame, text="Customer Information", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Customer fields
        customer_name_frame = ctk.CTkFrame(customer_frame, fg_color="#f9f9fb")
        customer_name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(customer_name_frame, text="Name:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        customer_name_entry = ctk.CTkEntry(customer_name_frame, width=300)
        customer_name_entry.pack(side="left", fill="x", expand=True)
        
        customer_phone_frame = ctk.CTkFrame(customer_frame, fg_color="#f9f9fb")
        customer_phone_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(customer_phone_frame, text="Phone:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        customer_phone_entry = ctk.CTkEntry(customer_phone_frame, width=300)
        customer_phone_entry.pack(side="left", fill="x", expand=True)
        
        customer_address_frame = ctk.CTkFrame(customer_frame, fg_color="#f9f9fb")
        customer_address_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(customer_address_frame, text="Address:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        customer_address_entry = ctk.CTkEntry(customer_address_frame, width=300)
        customer_address_entry.pack(side="left", fill="x", expand=True)

        # Pet Info Frame
        pet_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        pet_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(pet_frame, text="Pet Information", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Pet fields
        pet_name_frame = ctk.CTkFrame(pet_frame, fg_color="#f9f9fb")
        pet_name_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(pet_name_frame, text="Name:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        pet_name_entry = ctk.CTkEntry(pet_name_frame, width=300)
        pet_name_entry.pack(side="left", fill="x", expand=True)
        
        pet_type_frame = ctk.CTkFrame(pet_frame, fg_color="#f9f9fb")
        pet_type_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(pet_type_frame, text="Type:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        pet_type_entry = ctk.CTkOptionMenu(pet_type_frame, values=COMMON_PET_TYPES, width=300)
        pet_type_entry.pack(side="left", fill="x", expand=True)
        
        pet_breed_frame = ctk.CTkFrame(pet_frame, fg_color="#f9f9fb")
        pet_breed_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(pet_breed_frame, text="Breed:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        pet_breed_entry = ctk.CTkEntry(pet_breed_frame, width=300)
        pet_breed_entry.pack(side="left", fill="x", expand=True)
        
        pet_count_frame = ctk.CTkFrame(pet_frame, fg_color="#f9f9fb")
        pet_count_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(pet_count_frame, text="Number of Pets:", font=("Segoe UI", 14)).pack(side="left", padx=(0, 10))
        pet_count_entry = ctk.CTkEntry(pet_count_frame, width=300)
        pet_count_entry.pack(side="left", fill="x", expand=True)

        # Status dropdown
        status_frame = ctk.CTkFrame(left_frame, fg_color="#f9f9fb")
        status_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(status_frame, text="Status:", font=("Segoe UI", 14)).pack(anchor="w", padx=5)
        status_var = tk.StringVar(value="pending")
        status_dropdown = ctk.CTkOptionMenu(
            status_frame,
            values=["pending", "done"],
            variable=status_var,
            width=300,
            height=35
        )
        status_dropdown.pack(fill="x", padx=5)

        # Services Selection
        services_frame = ctk.CTkFrame(right_frame, fg_color="#f9f9fb")
        services_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        ctk.CTkLabel(services_frame, text="Services", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 10))
        
        # Services list with checkboxes
        services_list = ctk.CTkScrollableFrame(services_frame, width=300, height=400)
        services_list.pack(fill="both", expand=True, padx=5)
        
        # Dictionary to store service checkboxes
        service_vars = {}
        selected_services = set()
        total_amount = 0.0

        # Total amount display
        total_frame = ctk.CTkFrame(right_frame, fg_color="#f9f9fb")
        total_frame.pack(fill="x", pady=(0, 15))
        total_label = ctk.CTkLabel(
            total_frame,
            text=f"Total Amount: P{total_amount:.2f}",
            font=("Segoe UI", 16, "bold"),
            text_color="#f77f00"
        )
        total_label.pack(anchor="e", padx=10)

        def update_total(name, price, var):
            nonlocal total_amount, selected_services
            if var.get():
                selected_services.add((name, float(price)))
                total_amount += float(price)
            else:
                if (name, float(price)) in selected_services:
                    selected_services.remove((name, float(price)))
                    total_amount -= float(price)
            total_label.configure(text=f"Total Amount: P{total_amount:.2f}")

        # Load services from database
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT name, price FROM services ORDER BY name")
                services_data = cursor.fetchall()
                
                for name, price in services_data:
                    service_frame = ctk.CTkFrame(services_list, fg_color="#ffe5d0", corner_radius=10)
                    service_frame.pack(fill="x", pady=5, padx=5)
                    
                    var = tk.BooleanVar()
                    service_vars[name] = (var, price)
                    
                    ctk.CTkCheckBox(
                        service_frame,
                        text=f"{SERVICE_ICONS.get(name, '🐾')} {name} - P{price}",
                        variable=var,
                        font=("Segoe UI", 12, "bold"),
                        fg_color="#f7b267",
                        hover_color="#f9c784",
                        command=lambda n=name, p=price, v=var: update_total(n, p, v)
                    ).pack(fill="x", padx=10, pady=5)
                
                cursor.close()
                connection.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading services: {err}")

        # Load existing booking data
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                # Get booking details
                cursor.execute("""
                    SELECT b.booking_date, c.name, c.phone, c.address, p.name, p.breed, p.num_pets, b.status
                    FROM bookings b
                    JOIN customers c ON b.customer_id = c.id
                    JOIN pets p ON b.pet_id = p.id
                    WHERE b.id = %s
                """, (booking_id,))
                booking_data = cursor.fetchone()
                
                if booking_data:
                    booking_date, cust_name, cust_phone, cust_address, pet_name_val, pet_breed, num_pets, status = booking_data
                    date_picker.set_date(booking_date.date())
                    time_picker.set(booking_date.strftime("%H:%M"))
                    
                    # Set the values in the entry fields
                    customer_name_entry.insert(0, cust_name)
                    customer_phone_entry.insert(0, cust_phone)
                    customer_address_entry.insert(0, cust_address or '')
                    pet_name_entry.insert(0, pet_name_val)
                    pet_type_entry.set(pet_breed)
                    pet_breed_entry.insert(0, pet_breed)
                    pet_count_entry.insert(0, str(num_pets))
                    status_var.set(status)
                    
                    # Get selected services
                    cursor.execute("""
                        SELECT s.name, s.price
                        FROM booking_services bs
                        JOIN services s ON bs.service_id = s.id
                        WHERE bs.booking_id = %s
                    """, (booking_id,))
                    for name, price in cursor.fetchall():
                        if name in service_vars:
                            var, _ = service_vars[name]
                            var.set(True)
                            selected_services.add((name, float(price)))
                            total_amount += float(price)
                    total_label.configure(text=f"Total Amount: P{total_amount:.2f}")
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading booking details: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

        def save_reservation():
            try:
                connection = create_connection()
                if connection:
                    cursor = connection.cursor()
                    
                    # Update existing booking
                    cursor.execute("""
                        UPDATE bookings b
                        JOIN customers c ON b.customer_id = c.id
                        JOIN pets p ON b.pet_id = p.id
                        SET b.booking_date = %s,
                            c.name = %s,
                            c.phone = %s,
                            c.address = %s,
                            p.name = %s,
                            p.breed = %s,
                            p.num_pets = %s,
                            b.total_amount = %s,
                            b.status = %s
                        WHERE b.id = %s
                    """, (
                        datetime.combine(date_picker.get_date(), datetime.strptime(time_picker.get(), "%H:%M").time()),
                        customer_name_entry.get(),
                        customer_phone_entry.get(),
                        customer_address_entry.get(),
                        pet_name_entry.get(),
                        pet_type_entry.get(),
                        int(pet_count_entry.get() or 1),  # Default to 1 if empty
                        total_amount,
                        status_var.get(),
                        booking_id
                    ))
                    
                    # Delete existing booking services
                    cursor.execute("DELETE FROM booking_services WHERE booking_id = %s", (booking_id,))
                    
                    # Insert booking services
                    for service_name, price in selected_services:
                        cursor.execute(
                            "SELECT id FROM services WHERE name = %s",
                            (service_name,)
                        )
                        service_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO booking_services (booking_id, service_id, price) VALUES (%s, %s, %s)",
                            (booking_id, service_id, price)
                        )
                    
                    connection.commit()
                    messagebox.showinfo("Success", "Reservation updated successfully!")
                    dialog.destroy()
                    self.load_reservations()
                    
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error updating reservation: {err}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

        # Save button
        ctk.CTkButton(
            main_container,
            text="Save Changes",
            corner_radius=20,
            fg_color="#f7b267",
            hover_color="#f9c784",
            text_color="white",
            command=save_reservation,
            height=40
        ).pack(side="bottom", pady=(20, 0))

    def load_reservations(self):
        # Clear existing items
        for item in self.reservations_tree.get_children():
            self.reservations_tree.delete(item)
            
        try:
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT b.id, c.name, p.name, b.booking_date, b.total_amount, b.status,
                           GROUP_CONCAT(s.name SEPARATOR ', ') as services
                    FROM bookings b
                    JOIN customers c ON b.customer_id = c.id
                    JOIN pets p ON b.pet_id = p.id
                    JOIN booking_services bs ON b.id = bs.booking_id
                    JOIN services s ON bs.service_id = s.id
                    GROUP BY b.id
                    ORDER BY b.booking_date DESC
                """)
                
                for row in cursor.fetchall():
                    booking_id, customer_name, pet_name, booking_date, total, status, services = row
                    self.reservations_tree.insert(
                        "",
                        "end",
                        values=(
                            booking_id,
                            customer_name,
                            pet_name,
                            booking_date.strftime("%Y-%m-%d %H:%M"),
                            services,
                            f"P{total:.2f}",
                            status
                        )
                    )
                    
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Error loading reservations: {err}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def edit_reservation(self):
        selected_item = self.reservations_tree.selection()
        if not selected_item:
            return
            
        booking_id = self.reservations_tree.item(selected_item[0])['values'][0]
        self.show_reservation_dialog(edit_mode=True, booking_id=booking_id)

    def delete_reservation(self):
        selected_item = self.reservations_tree.selection()
        if not selected_item:
            return
            
        booking_id = self.reservations_tree.item(selected_item[0])['values'][0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this reservation?"):
            try:
                connection = create_connection()
                if connection:
                    cursor = connection.cursor()
                    
                    # Delete booking services first (due to foreign key constraint)
                    cursor.execute("DELETE FROM booking_services WHERE booking_id = %s", (booking_id,))
                    
                    # Delete the booking
                    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                    
                    connection.commit()
                    messagebox.showinfo("Success", "Reservation deleted successfully!")
                    self.load_reservations()
                    
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", f"Error deleting reservation: {err}")
            finally:
                if connection.is_connected():
                    cursor.close()
                    connection.close()

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#f9f9fb")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Header with New Reservation button
        header = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, 
            text="PawBuddy Grooming", 
            font=("Segoe UI", 24, "bold"), 
            text_color="#222"
        ).grid(row=0, column=0, sticky="w", pady=(0, 20))

        # Add New Reservation button (initially disabled)
        self.new_reservation_btn = ctk.CTkButton(
            header,
            text="➕ New Reservation",
            corner_radius=20,
            fg_color="#f7b267",
            hover_color="#f9c784",
            text_color="white",
            command=self.show_reservation_dialog,
            state="disabled"  # Initially disabled
        )
        self.new_reservation_btn.grid(row=0, column=1, sticky="e", pady=(0, 20))

        # Customer & Pet Info Section
        info_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        info_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 0))
        info_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        ctk.CTkLabel(info_frame, text="Customer Details", font=("Segoe UI", 18, "bold"), text_color="#222").grid(row=0, column=0, sticky="w", pady=(0, 10), columnspan=2)
        ctk.CTkLabel(info_frame, text="Pet Details", font=("Segoe UI", 18, "bold"), text_color="#222").grid(row=0, column=2, sticky="w", pady=(0, 10), columnspan=2)

        # Customer fields
        self.customer_name = ctk.CTkEntry(info_frame, placeholder_text="Customer Name", font=("Segoe UI", 13))
        self.customer_name.grid(row=1, column=0, padx=8, pady=5, sticky="ew")
        self.customer_name.bind('<KeyRelease>', self.validate_reservation_fields)
        
        self.customer_address = ctk.CTkEntry(info_frame, placeholder_text="Address", font=("Segoe UI", 13))
        self.customer_address.grid(row=1, column=1, padx=8, pady=5, sticky="ew")
        
        self.customer_phone = ctk.CTkEntry(info_frame, placeholder_text="Phone Number", font=("Segoe UI", 13))
        self.customer_phone.grid(row=2, column=0, padx=8, pady=5, sticky="ew")
        self.customer_phone.bind('<KeyRelease>', self.validate_reservation_fields)

        # Pet fields
        self.pet_type = ctk.CTkOptionMenu(info_frame, values=COMMON_PET_TYPES, font=("Segoe UI", 13), width=180)
        self.pet_type.set(COMMON_PET_TYPES[0])
        self.pet_type.grid(row=1, column=2, padx=8, pady=5, sticky="ew")
        self.pet_type.bind('<<ComboboxSelected>>', self.validate_reservation_fields)
        
        self.pet_name = ctk.CTkEntry(info_frame, placeholder_text="Pet Name", font=("Segoe UI", 13))
        self.pet_name.grid(row=1, column=3, padx=8, pady=5, sticky="ew")
        self.pet_name.bind('<KeyRelease>', self.validate_reservation_fields)
        
        self.pet_breed = ctk.CTkEntry(info_frame, placeholder_text="Breed", font=("Segoe UI", 13))
        self.pet_breed.grid(row=2, column=2, padx=8, pady=5, sticky="ew")
        
        self.pet_count = ctk.CTkEntry(info_frame, placeholder_text="Number of Pets", font=("Segoe UI", 13))
        self.pet_count.grid(row=2, column=3, padx=8, pady=5, sticky="ew")
        self.pet_count.bind('<KeyRelease>', self._validate_number_entry)

        # Search Bar with icon
        search_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        search_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 0))
        search_frame.grid_columnconfigure(1, weight=1)
        search_icon = ctk.CTkLabel(search_frame, text="🔍", font=("Segoe UI", 16), fg_color="#f9f9fb")
        search_icon.grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self.update_service_slider)
        self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, placeholder_text="Search services...", font=("Segoe UI", 13))
        self.search_entry.grid(row=0, column=1, sticky="ew", padx=0, pady=0)

        # Horizontal Scrollable Service Slider
        slider_frame = ctk.CTkFrame(self.main_frame, fg_color="#f9f9fb")
        slider_frame.grid(row=3, column=0, sticky="nsew", padx=30, pady=(10, 0))
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
        self.total_label.grid(row=4, column=0, sticky="e", pady=(20, 20), padx=(0, 40))

    def validate_reservation_fields(self, event=None):
        """Validate if all required fields are filled and at least one service is selected"""
        # Check required fields
        has_customer_name = bool(self.customer_name.get().strip())
        has_customer_phone = bool(self.customer_phone.get().strip())
        has_pet_name = bool(self.pet_name.get().strip())
        has_pet_type = bool(self.pet_type.get())
        has_selected_services = len(self.selected_services) > 0

        # Enable/disable the New Reservation button based on validation
        if all([has_customer_name, has_customer_phone, has_pet_name, has_pet_type, has_selected_services]):
            self.new_reservation_btn.configure(state="normal")
        else:
            self.new_reservation_btn.configure(state="disabled")

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
                self.selected_services.add((name, float(price)))
                self.total_amount += float(price)
        self.total_label.configure(text=f'Total: P{self.total_amount:.2f}')
        self.validate_reservation_fields()  # Validate fields after service selection changes

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