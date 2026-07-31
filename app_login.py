import os
import sys
import time
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

# Safe import for Database Connection
try:
    from Scripts.database import conn, cursor
except ImportError:
    try:
        from database import conn, cursor
    except ImportError as e:
        print(f"Database import error in login: {e}")
        conn, cursor = None, None

# Safe import for Theater Selection
try:
    from Scripts.theaterselection import select_theater
except ImportError:
    try:
        from theaterselection import select_theater
    except ImportError as e:
        print(f"Theater selection import error: {e}")
        def select_theater(parent_window, customer_id, movie_id):
            print(f"Selecting theater for Customer ID: {customer_id}, Movie ID: {movie_id}")


def save_customer(customer_window, parent_window, name_entry, email_entry, phone_entry, movie_id):
    name = name_entry.get().strip()
    email = email_entry.get().strip()
    phone = phone_entry.get().strip()

    if not name or not email or not phone:
        messagebox.showerror("Missing Information", "Please fill out all fields before proceeding.")
        return

    if cursor and conn:
        try:
            sql = "INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, email, phone))
            conn.commit()

            customer_id = cursor.lastrowid

            # Destroy current customer login window before launching theater selection
            customer_window.destroy()

            # Advance to Theater Selection
            select_theater(parent_window, customer_id, movie_id)

        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed to save customer details:\n{e}")
    else:
        # Fallback if DB is offline for testing
        customer_window.destroy()
        select_theater(parent_window, 1, movie_id)


def customer_window(parent, movie_id):
    # ------------------ Dynamic Directory Setup ------------------
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    # Helper function to locate assets across directory paths
    def find_file(filenames):
        """Utility to locate image files across root and script subfolders."""
        for name in filenames:
            p1 = os.path.join(script_dir, name)
            p2 = os.path.join(project_root, name)
            if os.path.exists(p1):
                return p1
            elif os.path.exists(p2):
                return p2
        return None

    # Locate Background & Logo paths
    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

    # ------------------ Create Window ------------------
    customer = Toplevel(parent)
    customer.title("Customer Information - AA Cinema")
    customer.configure(bg="#0f0f0f")

    # Image garbage collection tracking list
    image_refs = []
    customer.image_refs = image_refs

    # Get Screen Dimensions
    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    # Match monitor resolution and maximize window
    customer.geometry(f"{screen_w}x{screen_h}+0+0")
    try:
        customer.state('zoomed')
    except Exception:
        pass

    customer.deiconify()
    customer.lift()
    customer.focus_force()

    # Bind 'Esc' key to return to previous screen
    customer.bind("<Escape>", lambda e: customer.destroy())

    # ------------------ Cinematic Fullscreen Background ------------------
    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)

            # Darken to 30% brightness for contrast
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=customer)
            image_refs.append(bg_photo)

            bg_label = Label(customer, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in login: {e}")

    # ------------------ Top Date & Time Header Bar ------------------
    header_top_bar = Frame(customer, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(customer, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar,
        text="🍿 AA CINEMA - GUEST CHECKOUT",
        font=("Segoe UI", 10, "bold"),
        fg="#FFD700",
        bg="#121212",
        padx=20,
        pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(
        datetime_frame,
        font=("Segoe UI", 9, "bold"),
        fg="#cccccc",
        bg="#121212"
    )
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(
        datetime_frame,
        font=("Segoe UI", 10, "bold"),
        fg="#FFD700",
        bg="#121212"
    )
    lbl_time.pack(side="left")

    def update_datetime():
        """Live updater for time and current date on top header."""
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if customer.winfo_exists():
            customer.after(1000, update_datetime)

    update_datetime()

    # ------------------ Load Logo Icons ------------------
    card_logo_img = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)

            # Window Titlebar Icon
            window_logo = ImageTk.PhotoImage(logo_raw, master=customer)
            customer.iconphoto(False, window_logo)
            image_refs.append(window_logo)

            # Resized Logo for Top of Details Card
            logo_resized = logo_raw.resize((60, 60), Image.LANCZOS)
            card_logo_img = ImageTk.PhotoImage(logo_resized, master=customer)
            customer.card_logo_img = card_logo_img  # Prevent GC
            image_refs.append(card_logo_img)
        except Exception as e:
            print(f"Could not load logo icon in login: {e}")

    # ------------------ Centered Main Container ------------------
    center_frame = Frame(customer, bg="#0f0f0f")
    center_frame.place(relx=0.5, rely=0.52, anchor="center")

    # Elevated Dark Card Frame
    card = Frame(
        center_frame,
        bg="#1c1c1c",
        bd=1,
        relief="solid",
        highlightbackground="#FFD700",
        highlightthickness=1,
        padx=35,
        pady=25
    )
    card.pack()

    # ------------------ Header & Logo ------------------
    if card_logo_img:
        logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
        logo_lbl.image = card_logo_img
        logo_lbl.pack(pady=(0, 8))

    Label(
        card,
        text="GUEST CHECKOUT",
        font=("Segoe UI", 10, "bold"),
        fg="#FFD700",
        bg="#1c1c1c"
    ).pack(pady=(0, 2))

    Label(
        card,
        text="Enter Your Details",
        font=("Segoe UI", 18, "bold"),
        fg="white",
        bg="#1c1c1c"
    ).pack(pady=(0, 4))

    Label(
        card,
        text="Please enter valid contact details for your ticket confirmation.",
        font=("Segoe UI", 9),
        fg="#aaaaaa",
        bg="#1c1c1c"
    ).pack(pady=(0, 15))

    # ------------------ Form Fields ------------------
    fields_frame = Frame(card, bg="#1c1c1c")
    fields_frame.pack(fill="x", pady=2)

    # Field: Name
    Label(
        fields_frame,
        text="FULL NAME",
        font=("Segoe UI", 8, "bold"),
        fg="#dddddd",
        bg="#1c1c1c",
        anchor="w"
    ).pack(fill="x", pady=(4, 2))

    name_entry = Entry(
        fields_frame,
        font=("Segoe UI", 11),
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        bd=0,
        highlightbackground="#444444",
        highlightthickness=1,
        relief="flat"
    )
    name_entry.pack(fill="x", ipady=7, pady=(0, 10))
    name_entry.focus_set()

    # Field: Email Address
    Label(
        fields_frame,
        text="EMAIL ADDRESS",
        font=("Segoe UI", 8, "bold"),
        fg="#dddddd",
        bg="#1c1c1c",
        anchor="w"
    ).pack(fill="x", pady=(4, 2))

    email_entry = Entry(
        fields_frame,
        font=("Segoe UI", 11),
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        bd=0,
        highlightbackground="#444444",
        highlightthickness=1,
        relief="flat"
    )
    email_entry.pack(fill="x", ipady=7, pady=(0, 10))

    # Field: Contact Number
    Label(
        fields_frame,
        text="PHONE NUMBER",
        font=("Segoe UI", 8, "bold"),
        fg="#dddddd",
        bg="#1c1c1c",
        anchor="w"
    ).pack(fill="x", pady=(4, 2))

    phone_entry = Entry(
        fields_frame,
        font=("Segoe UI", 11),
        bg="#2b2b2b",
        fg="white",
        insertbackground="white",
        bd=0,
        highlightbackground="#444444",
        highlightthickness=1,
        relief="flat"
    )
    phone_entry.pack(fill="x", ipady=7, pady=(0, 15))

    # ------------------ Action Buttons ------------------
    button_frame = Frame(card, bg="#1c1c1c")
    button_frame.pack(fill="x", pady=(5, 0))

    # Back Button
    btn_back = Button(
        button_frame,
        text="Back",
        bg="#E53935",
        fg="white",
        activebackground="#d32f2f",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        width=12,
        cursor="hand2",
        bd=0,
        command=customer.destroy
    )
    btn_back.pack(side="left", ipady=5, padx=(0, 6))

    # Submit / Next Button
    btn_next = Button(
        button_frame,
        text="Proceed to Theater  ➜",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        width=20,
        cursor="hand2",
        bd=0,
        command=lambda: save_customer(customer, parent, name_entry, email_entry, phone_entry, movie_id)
    )
    btn_next.pack(side="right", ipady=5, padx=(6, 0))

    # Bind Enter key to trigger submission
    customer.bind(
        "<Return>",
        lambda e: save_customer(customer, parent, name_entry, email_entry, phone_entry, movie_id)
    )