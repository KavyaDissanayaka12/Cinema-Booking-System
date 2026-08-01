import os
import sys
import importlib
import time
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import Button, Label, Frame, Entry, StringVar, Radiobutton, Toplevel, Canvas, Scrollbar, ttk, CENTER, \
    messagebox
from PIL import Image, ImageTk

# ReportLab Imports for PDF Ticket Generation
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
except ImportError:
    pass

# ------------------ Set Search Paths BEFORE Imports ------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
BASE_DIR = script_dir
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.path.exists(SCRIPTS_DIR) and SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# ------------------ Database Safe Import & Fallbacks ------------------
cursor = None
conn = None

try:
    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="cinema"
    )
    cursor = conn.cursor()
    print("Connected successfully!")
except Exception as e:
    print(f"Direct MySQL Connection Info: {e}")

try:
    from Scripts.database import cursor as d_cursor, conn as d_conn

    cursor, conn = d_cursor, d_conn
except ImportError:
    try:
        from database import cursor as d_cursor, conn as d_conn

        cursor, conn = d_cursor, d_conn
    except ImportError as e:
        print(f"Database module import notice: {e}")

IS_SQLITE = False
PH = "%s"


def get_sql_param():
    return PH


image_refs = []


def find_file(filenames):
    """Utility to locate image files across root, scripts, and posters subfolders."""
    if isinstance(filenames, str):
        filenames = [filenames]

    for name in filenames:
        candidates = [
            os.path.join(BASE_DIR, name),
            os.path.join(SCRIPTS_DIR, name),
            os.path.join(project_root, name),
            os.path.join(BASE_DIR, "posters", name),
            os.path.join(project_root, "posters", name),
            os.path.join(os.getcwd(), "posters", name),
            os.path.join(os.getcwd(), name)
        ]
        for path in candidates:
            if os.path.exists(path):
                return path
    return None


def resolve_poster_path(poster_filename):
    """Resolves image paths stored inside the 'posters' subfolder safely across environments."""
    if not poster_filename:
        return None
    clean_filename = str(poster_filename).strip().strip("'\"")
    return find_file([clean_filename, os.path.join("posters", clean_filename)])


RESAMPLE_FILTER = getattr(Image, 'Resampling', Image).LANCZOS

LOGO_PATH = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
BACKGROUND_IMAGE_PATH = find_file(
    ["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG", "bg.jpg"]
)


def load_cinema_logo(size=(32, 32)):
    """Helper to load and resize the cinema logo safely."""
    try:
        path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
        if path and os.path.exists(path):
            img = Image.open(path)
            img = img.resize(size, RESAMPLE_FILTER)
            return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"Could not load logo: {e}")
    return None


# ------------------ Initialize Main Window ------------------
root = tk.Tk()
root.title("AA Cinema - Premium Ticket Booking")
root.configure(bg="#0d0d0d")

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
root.geometry(f"{screen_w}x{screen_h}+0+0")

try:
    root.state('zoomed')
except Exception:
    pass

root.bind("<Escape>", lambda e: root.state('normal'))
root.image_refs = image_refs

if LOGO_PATH:
    try:
        icon_img = Image.open(LOGO_PATH)
        icon_photo = ImageTk.PhotoImage(icon_img, master=root)
        root.iconphoto(False, icon_photo)
        image_refs.append(icon_photo)
    except Exception as e:
        print(f"Window icon error: {e}")

if BACKGROUND_IMAGE_PATH:
    try:
        raw_bg = Image.open(BACKGROUND_IMAGE_PATH)
        bg_scaled = raw_bg.resize((screen_w, screen_h), RESAMPLE_FILTER)
        bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.35))
        bg_photo = ImageTk.PhotoImage(bg_darkened, master=root)

        image_refs.append(bg_photo)

        bg_label = Label(root, image=bg_photo, bg="#0d0d0d")
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print(f"Error rendering background image: {e}")

# ------------------ Top Navigation Bar (With Live Clock) ------------------
top_header = Frame(root, bg="#121212", bd=0)
top_header.pack(side="top", fill="x")

header_border = Frame(root, bg="#D4AF37", height=1)
header_border.pack(side="top", fill="x")

header_brand = Label(
    top_header,
    text="🍿 AA CINEMA TICKETING SYSTEM",
    font=("Segoe UI", 10, "bold"),
    fg="#FFD700",
    bg="#121212",
    padx=20,
    pady=8
)
header_brand.pack(side="left")

datetime_frame = Frame(top_header, bg="#121212")
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
    current_time = time.strftime("%I:%M:%S %p")
    current_date = time.strftime("%A, %B %d, %Y")
    lbl_time.config(text=f"🕒 {current_time}")
    lbl_date.config(text=f"📅 {current_date}")
    root.after(1000, update_datetime)


update_datetime()

# ------------------ Centered Main UI Box ------------------
center_wrapper = Frame(root, bg="")
center_wrapper.place(relx=0.5, rely=0.53, anchor="center")

card_frame = Frame(
    center_wrapper,
    bg="#161616",
    bd=1,
    relief="solid",
    highlightbackground="#D4AF37",
    highlightthickness=1,
    padx=50,
    pady=30
)
card_frame.pack()

if LOGO_PATH:
    try:
        logo_raw = Image.open(LOGO_PATH)
        logo_resized = logo_raw.resize((110, 110), RESAMPLE_FILTER)
        logo_photo = ImageTk.PhotoImage(logo_resized, master=root)
        image_refs.append(logo_photo)

        logo_label = Label(card_frame, image=logo_photo, bg="#161616")
        logo_label.image = logo_photo
        logo_label.pack(pady=(5, 10))
    except Exception as e:
        print(f"Logo image error: {e}")

Label(
    card_frame,
    text="AA CINEMA",
    font=("Segoe UI", 28, "bold"),
    fg="#FFD700",
    bg="#161616"
).pack(pady=(0, 2))

Label(
    card_frame,
    text="PREMIUM MOVIE TICKETING",
    font=("Segoe UI", 9, "bold"),
    fg="#888888",
    bg="#161616"
).pack(pady=(0, 10))

Label(
    card_frame,
    text="Book your favorite movies in seconds.",
    font=("Segoe UI", 11),
    fg="#cccccc",
    bg="#161616"
).pack(pady=(0, 20))


def add_hover_effect(btn, normal_bg, hover_bg, normal_fg="white", hover_fg="white"):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, fg=hover_fg))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg, fg=normal_fg))


def open_showing_movies(root_window):
    view_movies(root_window)


def view_movies(root):
    cursor_loc = cursor
    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

    movie_window = Toplevel(root)
    movie_window.title("Available Movies - AA Cinema")
    movie_window.configure(bg="#0f0f0f")

    image_refs = []
    movie_window.image_refs = image_refs

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    movie_window.geometry(f"{screen_w}x{screen_h}+0+0")

    try:
        movie_window.state('zoomed')
    except Exception:
        pass

    movie_window.bind("<Escape>", lambda e: movie_window.state('normal'))
    movie_window.deiconify()
    movie_window.lift()
    movie_window.focus_force()

    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=movie_window)
            image_refs.append(bg_photo)

            bg_label = Label(movie_window, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in movies: {e}")

    window_logo_img = None
    fallback_logo_img = None
    header_logo_img = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo_img = ImageTk.PhotoImage(logo_raw, master=movie_window)
            movie_window.iconphoto(False, window_logo_img)
            image_refs.append(window_logo_img)

            header_logo_resized = logo_raw.resize((35, 35), Image.LANCZOS)
            header_logo_img = ImageTk.PhotoImage(header_logo_resized, master=movie_window)
            image_refs.append(header_logo_img)

            fallback_logo_resized = logo_raw.resize((120, 120), Image.LANCZOS)
            fallback_logo_img = ImageTk.PhotoImage(fallback_logo_resized, master=movie_window)
            image_refs.append(fallback_logo_img)
        except Exception as e:
            print(f"Could not load cinema logo image in movies: {e}")

    header_top_bar = Frame(movie_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(movie_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar,
        text="🍿 AA CINEMA - NOW SHOWING",
        font=("Segoe UI", 10, "bold"),
        fg="#FFD700",
        bg="#121212",
        padx=20,
        pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_datetime_m():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if movie_window.winfo_exists():
            movie_window.after(1000, update_datetime_m)

    update_datetime_m()

    hero_frame = Frame(movie_window, bg="#1a1a1a", bd=1, relief="solid", highlightbackground="#D4AF37",
                       highlightthickness=1)
    hero_frame.pack(fill="x", padx=20, pady=(10, 10))

    Label(hero_frame, text="✦ NOW SHOWING ✦", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#1a1a1a").pack(
        pady=(12, 2))

    title_box = Frame(hero_frame, bg="#1a1a1a")
    title_box.pack(pady=(0, 2))

    if header_logo_img:
        hdr_logo_lbl = Label(title_box, image=header_logo_img, bg="#1a1a1a")
        hdr_logo_lbl.image = header_logo_img
        hdr_logo_lbl.pack(side="left", padx=(0, 10))

    Label(title_box, text="AVAILABLE MOVIES AT AA CINEMA", font=("Segoe UI", 22, "bold"), fg="white",
          bg="#1a1a1a").pack(side="left")
    Label(hero_frame, text="Press 'ESC' key on your keyboard to exit full screen mode.", font=("Segoe UI", 9, "italic"),
          fg="#aaaaaa", bg="#1a1a1a").pack(pady=(0, 10))

    canvas = Canvas(movie_window, bg="#0f0f0f", highlightthickness=0)
    scrollbar = Scrollbar(movie_window, orient="vertical", command=canvas.yview)

    container = Frame(canvas, bg="#0f0f0f")
    container_window = canvas.create_window((screen_w // 2, 0), window=container, anchor="n")

    container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    def _on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    container.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    container.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    movies = []
    if cursor_loc:
        try:
            cursor_loc.execute("""
                SELECT movie_id, title, genre, duration, language, release_date, poster
                FROM movies
            """)
            movies = cursor_loc.fetchall()
        except Exception as db_err:
            print(f"Database query error in movies: {db_err}")

    columns = max(3, screen_w // 250)

    for index, movie in enumerate(movies):
        movie_id, title, genre, duration, language, release, poster_filename = movie

        card = Frame(container, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#333333", highlightthickness=1)
        row = index // columns
        col = index % columns
        card.grid(row=row, column=col, padx=14, pady=16, sticky="n")

        poster_frame = Frame(card, bg="#0d0d0d", bd=1, relief="solid", width=175, height=250)
        poster_frame.pack_propagate(False)
        poster_frame.pack(padx=10, pady=(10, 6))

        poster_loaded = False
        poster_path = resolve_poster_path(poster_filename)

        if poster_path and os.path.exists(poster_path):
            try:
                raw_img = Image.open(poster_path)
                resized_img = raw_img.resize((175, 250), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img, master=movie_window)
                image_refs.append(photo)

                img_label = Label(poster_frame, image=photo, bg="#0d0d0d")
                img_label.image = photo
                img_label.pack(fill="both", expand=True)
                poster_loaded = True
            except Exception as img_err:
                print(f"Error rendering {poster_path}: {img_err}")

        if not poster_loaded:
            fallback_box = Frame(poster_frame, bg="#181818")
            fallback_box.pack(fill="both", expand=True)

            if fallback_logo_img:
                logo_lbl = Label(fallback_box, image=fallback_logo_img, bg="#181818")
                logo_lbl.image = fallback_logo_img
                logo_lbl.pack(expand=True, pady=(15, 0))

            Label(fallback_box, text="AA CINEMA", font=("Segoe UI", 9, "bold"), bg="#181818", fg="#888888").pack(
                pady=(0, 15))

        info_frame = Frame(card, bg="#1c1c1c")
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        Label(info_frame, text=title, font=("Segoe UI", 10, "bold"), fg="white", bg="#1c1c1c", wraplength=165,
              justify=CENTER).pack(pady=(4, 4))
        Label(info_frame, text=f"🎭 {genre}", font=("Segoe UI", 8), fg="#cccccc", bg="#1c1c1c").pack(pady=(0, 2))
        Label(info_frame, text=f"⏱ {duration} • 🌐 {language}", font=("Segoe UI", 8), fg="#aaaaaa", bg="#1c1c1c").pack(
            pady=(0, 4))
        Label(info_frame, text=f"📅 {release}", font=("Segoe UI", 8), fg="#888888", bg="#1c1c1c").pack(pady=(0, 8))

        def save_customer(customer_window, parent_window, name_entry, email_entry, phone_entry, m_id):
            name = name_entry.get().strip()
            email = email_entry.get().strip()
            phone = phone_entry.get().strip()

            if not name or not email or not phone:
                messagebox.showerror("Missing Information", "Please fill out all fields before proceeding.")
                return

            if cursor and conn:
                try:
                    sql = f"INSERT INTO customers (name, email, phone) VALUES ({PH}, {PH}, {PH})"
                    cursor.execute(sql, (name, email, phone))
                    conn.commit()
                    customer_id = getattr(cursor, 'lastrowid', 1)
                    customer_window.destroy()
                    select_theater(parent_window, customer_id, m_id)
                except Exception as e:
                    if hasattr(conn, "rollback"):
                        conn.rollback()
                    messagebox.showerror("Database Error", f"Failed to save customer details:\n{e}")
            else:
                customer_window.destroy()
                select_theater(parent_window, 1, m_id)

        def customer_window(parent, m_id):
            bg_p = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
            logo_p = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

            customer = Toplevel(parent)
            customer.title("Customer Information - AA Cinema")
            customer.configure(bg="#0f0f0f")

            image_refs_c = []
            customer.image_refs = image_refs_c

            s_w = parent.winfo_screenwidth()
            s_h = parent.winfo_screenheight()
            customer.geometry(f"{s_w}x{s_h}+0+0")
            try:
                customer.state('zoomed')
            except Exception:
                pass

            customer.deiconify()
            customer.lift()
            customer.focus_force()
            customer.bind("<Escape>", lambda e: customer.destroy())

            if bg_p and os.path.exists(bg_p):
                try:
                    raw_bg = Image.open(bg_p)
                    bg_scaled = raw_bg.resize((s_w, s_h), Image.LANCZOS)
                    bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
                    bg_photo = ImageTk.PhotoImage(bg_darkened, master=customer)
                    image_refs_c.append(bg_photo)

                    bg_label = Label(customer, image=bg_photo, bg="#0f0f0f")
                    bg_label.image = bg_photo
                    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                except Exception as e:
                    print(f"Error loading background image in login: {e}")

            header_top_bar = Frame(customer, bg="#121212")
            header_top_bar.pack(side="top", fill="x")

            header_border = Frame(customer, bg="#D4AF37", height=1)
            header_border.pack(side="top", fill="x")

            header_brand = Label(
                header_top_bar, text="🍿 AA CINEMA - GUEST CHECKOUT",
                font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=6
            )
            header_brand.pack(side="left")

            datetime_frame = Frame(header_top_bar, bg="#121212")
            datetime_frame.pack(side="right", padx=20, pady=5)

            lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
            lbl_date.pack(side="left", padx=(0, 10))

            lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
            lbl_time.pack(side="left")

            def update_datetime_c():
                current_time = time.strftime("%I:%M:%S %p")
                current_date = time.strftime("%A, %B %d, %Y")
                lbl_time.config(text=f"🕒 {current_time}")
                lbl_date.config(text=f"📅 {current_date}")
                if customer.winfo_exists():
                    customer.after(1000, update_datetime_c)

            update_datetime_c()

            card_logo_img = None
            if logo_p and os.path.exists(logo_p):
                try:
                    logo_raw = Image.open(logo_p)
                    window_logo = ImageTk.PhotoImage(logo_raw, master=customer)
                    customer.iconphoto(False, window_logo)
                    image_refs_c.append(window_logo)

                    logo_resized = logo_raw.resize((60, 60), Image.LANCZOS)
                    card_logo_img = ImageTk.PhotoImage(logo_resized, master=customer)
                    customer.card_logo_img = card_logo_img
                    image_refs_c.append(card_logo_img)
                except Exception as e:
                    print(f"Could not load logo icon in login: {e}")

            center_frame = Frame(customer, bg="#0f0f0f")
            center_frame.place(relx=0.5, rely=0.52, anchor="center")

            card = Frame(center_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#FFD700",
                         highlightthickness=1, padx=35, pady=25)
            card.pack()

            if card_logo_img:
                logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
                logo_lbl.image = card_logo_img
                logo_lbl.pack(pady=(0, 8))

            Label(card, text="GUEST CHECKOUT", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#1c1c1c").pack(
                pady=(0, 2))
            Label(card, text="Enter Your Details", font=("Segoe UI", 18, "bold"), fg="white", bg="#1c1c1c").pack(
                pady=(0, 4))
            Label(card, text="Please enter valid contact details for your ticket confirmation.", font=("Segoe UI", 9),
                  fg="#aaaaaa", bg="#1c1c1c").pack(pady=(0, 15))

            fields_frame = Frame(card, bg="#1c1c1c")
            fields_frame.pack(fill="x", pady=2)

            Label(fields_frame, text="FULL NAME", font=("Segoe UI", 8, "bold"), fg="#dddddd", bg="#1c1c1c",
                  anchor="w").pack(fill="x", pady=(4, 2))
            name_entry = Entry(fields_frame, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", insertbackground="white",
                               bd=0, highlightbackground="#444444", highlightthickness=1, relief="flat")
            name_entry.pack(fill="x", ipady=7, pady=(0, 10))
            name_entry.focus_set()

            Label(fields_frame, text="EMAIL ADDRESS", font=("Segoe UI", 8, "bold"), fg="#dddddd", bg="#1c1c1c",
                  anchor="w").pack(fill="x", pady=(4, 2))
            email_entry = Entry(fields_frame, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", insertbackground="white",
                                bd=0, highlightbackground="#444444", highlightthickness=1, relief="flat")
            email_entry.pack(fill="x", ipady=7, pady=(0, 10))

            Label(fields_frame, text="PHONE NUMBER", font=("Segoe UI", 8, "bold"), fg="#dddddd", bg="#1c1c1c",
                  anchor="w").pack(fill="x", pady=(4, 2))
            phone_entry = Entry(fields_frame, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", insertbackground="white",
                                bd=0, highlightbackground="#444444", highlightthickness=1, relief="flat")
            phone_entry.pack(fill="x", ipady=7, pady=(0, 15))

            button_frame = Frame(card, bg="#1c1c1c")
            button_frame.pack(fill="x", pady=(5, 0))

            btn_back = Button(
                button_frame, text="Back", bg="#E53935", fg="white", activebackground="#d32f2f",
                activeforeground="white",
                font=("Segoe UI", 10, "bold"), width=12, cursor="hand2", bd=0, command=customer.destroy
            )
            btn_back.pack(side="left", ipady=5, padx=(0, 6))

            btn_next = Button(
                button_frame, text="Proceed to Theater  ➜", bg="#4CAF50", fg="white", activebackground="#45a049",
                activeforeground="white", font=("Segoe UI", 10, "bold"), width=20, cursor="hand2", bd=0,
                command=lambda: save_customer(customer, parent, name_entry, email_entry, phone_entry, m_id)
            )
            btn_next.pack(side="right", ipady=5, padx=(6, 0))

            customer.bind("<Return>",
                          lambda e: save_customer(customer, parent, name_entry, email_entry, phone_entry, m_id))

        btn_book = Button(
            info_frame, text="🎟 Book Ticket", bg="#FFD700", fg="black", font=("Segoe UI", 9, "bold"),
            cursor="hand2", bd=0, activebackground="#E6C200", activeforeground="black",
            command=lambda m_id=movie_id: customer_window(movie_window, m_id)
        )
        btn_book.pack(fill="x", ipady=3)

        def on_enter(e, b=btn_book):
            b.config(bg="#FFF066")

        def on_leave(e, b=btn_book):
            b.config(bg="#FFD700")

        btn_book.bind("<Enter>", on_enter)
        btn_book.bind("<Leave>", on_leave)

    movie_window.images = image_refs
    movie_window.header_logo_img = header_logo_img
    movie_window.fallback_logo_img = fallback_logo_img


def select_theater(parent, customer_id, movie_id):
    window = Toplevel(parent)
    window.title("Select Theater & Showtime - AA Cinema")
    window.configure(bg="#0f0f0f")

    image_refs_t = []
    window.image_refs = image_refs_t

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    window.geometry(f"{screen_w}x{screen_h}+0+0")
    try:
        window.state('zoomed')
    except Exception:
        pass

    window.deiconify()
    window.lift()
    window.focus_force()
    window.bind("<Escape>", lambda e: window.destroy())

    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=window)
            image_refs_t.append(bg_photo)

            bg_label = Label(window, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in theater selection: {e}")

    header_top_bar = Frame(window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar, text="🍿 AA CINEMA - THEATER SELECTION",
        font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_datetime_t():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if window.winfo_exists():
            window.after(1000, update_datetime_t)

    update_datetime_t()

    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
    card_logo_img = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo = ImageTk.PhotoImage(logo_raw, master=window)
            window.iconphoto(False, window_logo)
            image_refs_t.append(window_logo)

            logo_resized = logo_raw.resize((50, 50), Image.LANCZOS)
            card_logo_img = ImageTk.PhotoImage(logo_resized, master=window)
            image_refs_t.append(card_logo_img)
        except Exception as e:
            print(f"Could not load icon in theater selection: {e}")

    theater_img_path = find_file(["theater2.JPEG", "theater2.jpeg", "theater2.jpg", "theater2.png"])
    banner_tk_img = None
    if theater_img_path and os.path.exists(theater_img_path):
        try:
            th_raw = Image.open(theater_img_path)
            th_resized = th_raw.resize((420, 150), Image.LANCZOS)
            banner_tk_img = ImageTk.PhotoImage(th_resized, master=window)
            image_refs_t.append(banner_tk_img)
        except Exception as e:
            print(f"Could not load theater2 image from '{theater_img_path}': {e}")

    center_frame = Frame(window, bg="")
    center_frame.place(relx=0.5, rely=0.52, anchor="center")

    card = Frame(center_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#D4AF37", highlightthickness=1,
                 padx=40, pady=25)
    card.pack()

    if card_logo_img:
        logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
        logo_lbl.image = card_logo_img
        logo_lbl.pack(pady=(0, 5))

    Label(card, text="SHOWTIME & LOCATION", font=("Segoe UI", 9, "bold"), fg="#FFD700", bg="#1c1c1c").pack(pady=(0, 2))
    Label(card, text="Select Theater & Showtime", font=("Segoe UI", 18, "bold"), fg="white", bg="#1c1c1c").pack(
        pady=(0, 10))

    if banner_tk_img:
        banner_frame = Frame(card, bg="#FFD700", bd=1, relief="solid")
        banner_frame.pack(pady=(0, 15))

        banner_lbl = Label(banner_frame, image=banner_tk_img, bg="#1c1c1c")
        banner_lbl.image = banner_tk_img
        banner_lbl.pack()

        overlay_badge = Label(banner_lbl, text=" 🎬 PREVIEW YOUR EXPERIENCE ", font=("Segoe UI", 8, "bold"),
                              fg="#121212", bg="#FFD700")
        overlay_badge.place(relx=0.03, rely=0.78)

    style = ttk.Style()
    style.theme_use('default')

    style.configure(
        "DarkText.TCombobox",
        fieldbackground="#e0e0e0",
        background="#333333",
        foreground="#1c1c1c",
        darkcolor="#2b2b2b",
        lightcolor="#2b2b2b",
        selectbackground="#FFD700",
        selectforeground="#1c1c1c",
        arrowcolor="white",
        padding=6
    )

    window.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10, "bold"))
    window.option_add("*TCombobox*Listbox.background", "#e0e0e0")
    window.option_add("*TCombobox*Listbox.foreground", "#1c1c1c")
    window.option_add("*TCombobox*Listbox.selectBackground", "#FFD700")
    window.option_add("*TCombobox*Listbox.selectForeground", "#1c1c1c")

    fields_frame = Frame(card, bg="#1c1c1c")
    fields_frame.pack(fill="x", pady=0)

    Label(fields_frame, text="THEATER & LOCATION", font=("Segoe UI", 9, "bold"), fg="#dddddd", bg="#1c1c1c",
          anchor="w").pack(fill="x", pady=(2, 2))

    theater_combo = ttk.Combobox(fields_frame, style="DarkText.TCombobox", state="readonly",
                                 font=("Segoe UI", 10, "bold"), width=36)
    theater_combo.pack(fill="x", pady=(0, 10))

    Label(fields_frame, text="AVAILABLE SHOWTIME", font=("Segoe UI", 9, "bold"), fg="#dddddd", bg="#1c1c1c",
          anchor="w").pack(fill="x", pady=(2, 2))

    showtime_combo = ttk.Combobox(fields_frame, style="DarkText.TCombobox", state="readonly",
                                  font=("Segoe UI", 10, "bold"), width=36)
    showtime_combo.pack(fill="x", pady=(0, 18))

    theater_ids = {}
    theaters = []
    if cursor:
        queries = [
            (f"SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN shows s ON t.theater_id = s.theater_id WHERE s.movie_id = {PH} ORDER BY t.theater_name",
             (movie_id,)),
            (f"SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN showtimes s ON t.theater_id = s.theater_id WHERE s.movie_id = {PH} ORDER BY t.theater_name",
             (movie_id,))
        ]
        for query, params in queries:
            try:
                cursor.execute(query, params)
                theaters = cursor.fetchall()
                if theaters:
                    break
            except Exception:
                continue

    theater_options = []
    for theater in theaters:
        t_id, t_name = theater[0], theater[1]
        t_location = theater[2] if len(theater) > 2 and theater[2] else "Main Hall"
        display_name = f"{t_name} ({t_location})"
        theater_ids[display_name] = t_id
        theater_options.append(display_name)

    theater_combo["values"] = theater_options

    def load_showtimes(event=None):
        selected_theater_str = theater_combo.get()
        if not selected_theater_str or selected_theater_str not in theater_ids:
            showtime_combo["values"] = []
            return

        theater_id = theater_ids[selected_theater_str]
        times = []

        if cursor:
            st_queries = [
                (f"SELECT show_date, show_time FROM shows WHERE movie_id = {PH} AND theater_id = {PH} ORDER BY show_date, show_time",
                 (movie_id, theater_id)),
                (f"SELECT show_date, show_time FROM showtimes WHERE movie_id = {PH} AND theater_id = {PH} ORDER BY show_date, show_time",
                 (movie_id, theater_id))
            ]
            for query, params in st_queries:
                try:
                    cursor.execute(query, params)
                    times = cursor.fetchall()
                    if times:
                        break
                except Exception:
                    continue

        showtime_options = [f"{row[0]}  |  {row[1]}" for row in times]
        showtime_combo["values"] = showtime_options

        if showtime_options:
            showtime_combo.current(0)
        else:
            showtime_combo.set("No showtimes available")

    theater_combo.bind("<<ComboboxSelected>>", load_showtimes)

    if theater_options:
        theater_combo.current(0)
        load_showtimes()
    else:
        theater_combo.set("No theaters showing this movie")

    def proceed_to_seats():
        selected_theater_str = theater_combo.get()
        selected_showtime = showtime_combo.get()

        if not selected_theater_str or not selected_showtime or "No showtimes" in selected_showtime or "No theaters" in selected_theater_str:
            messagebox.showerror("Selection Error", "Please select a valid theater and showtime.")
            return

        theater_id = theater_ids[selected_theater_str]
        window.destroy()
        select_seats(parent, customer_id, movie_id, theater_id, selected_showtime)

    button_frame = Frame(card, bg="#1c1c1c")
    button_frame.pack(fill="x", pady=(5, 0))

    btn_back = Button(
        button_frame, text="Back", bg="#E53935", fg="white", activebackground="#d32f2f", activeforeground="white",
        font=("Segoe UI", 10, "bold"), width=12, cursor="hand2", bd=0, command=window.destroy
    )
    btn_back.pack(side="left", ipady=6, padx=(0, 8))

    btn_next = Button(
        button_frame, text="Select Seats  ➜", bg="#4CAF50", fg="white", activebackground="#45a049",
        activeforeground="white", font=("Segoe UI", 10, "bold"), width=20, cursor="hand2", bd=0,
        command=proceed_to_seats
    )
    btn_next.pack(side="right", ipady=6, padx=(8, 0))

    window.bind("<Return>", lambda e: proceed_to_seats())


def select_seats(parent, customer_id, movie_id, theater_id, showtime):
    param = get_sql_param()

    seat_window = Toplevel(parent)
    seat_window.title("Select Seats - AA Cinema")
    seat_window.configure(bg="#0f0f0f")

    image_refs_s = []
    seat_window.image_refs = image_refs_s

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    seat_window.geometry(f"{screen_w}x{screen_h}+0+0")
    try:
        seat_window.state('zoomed')
    except Exception:
        pass

    seat_window.deiconify()
    seat_window.lift()
    seat_window.focus_force()
    seat_window.bind("<Escape>", lambda e: seat_window.destroy())

    header_top_bar = Frame(seat_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(seat_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar, text="🍿 AA CINEMA - SEAT SELECTION",
        font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_datetime_s():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if seat_window.winfo_exists():
            seat_window.after(1000, update_datetime_s)

    update_datetime_s()

    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
    header_logo_img = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo = ImageTk.PhotoImage(logo_raw, master=seat_window)
            seat_window.iconphoto(False, window_logo)
            image_refs_s.append(window_logo)

            logo_resized = logo_raw.resize((35, 35), Image.LANCZOS)
            header_logo_img = ImageTk.PhotoImage(logo_resized, master=seat_window)
            seat_window.header_logo_img = header_logo_img
            image_refs_s.append(header_logo_img)
        except Exception as e:
            print(f"Could not load logo icon in seat selection: {e}")

    theater1_path = find_file(["theater1.JPEG", "theater1.jpeg", "theater1.jpg", "theater1.png"])
    theater_banner_img = None
    if theater1_path and os.path.exists(theater1_path):
        try:
            raw_banner = Image.open(theater1_path)
            resized_banner = raw_banner.resize((340, 150), Image.LANCZOS)
            theater_banner_img = ImageTk.PhotoImage(resized_banner, master=seat_window)
            seat_window.theater_banner_img = theater_banner_img
            image_refs_s.append(theater_banner_img)
        except Exception as e:
            print(f"Error loading theater1 image: {e}")

    hero_frame = Frame(seat_window, bg="#1a1a1a", bd=2, relief="groove")
    hero_frame.pack(fill="x", padx=20, pady=(12, 6))

    title_box = Frame(hero_frame, bg="#1a1a1a")
    title_box.pack(pady=(10, 4))

    if header_logo_img:
        hdr_logo_lbl = Label(title_box, image=header_logo_img, bg="#1a1a1a")
        hdr_logo_lbl.image = header_logo_img
        hdr_logo_lbl.pack(side="left", padx=(0, 10))

    Label(title_box, text="AUDITORIUM SEATING PLAN", font=("Segoe UI", 18, "bold"), fg="white", bg="#1a1a1a").pack(
        side="left")
    Label(title_box, text=" • CHOOSE YOUR SEATS", font=("Segoe UI", 18, "bold"), fg="#FFD700", bg="#1a1a1a").pack(
        side="left")

    if theater_banner_img:
        banner_container = Frame(hero_frame, bg="#FFD700", bd=1, relief="solid")
        banner_container.pack(pady=(6, 10), anchor="center")

        banner_lbl = Label(banner_container, image=theater_banner_img, bg="#1a1a1a")
        banner_lbl.image = theater_banner_img
        banner_lbl.pack()

        badge_tag = Label(banner_lbl, text=" 🍿 PREMIUM CINEMA HALL EXPERIENCE 🍿 ", font=("Segoe UI", 8, "bold"),
                          fg="#121212", bg="#FFD700", bd=0)
        badge_tag.place(relx=0.03, rely=0.70)
    else:
        Label(hero_frame, text="Press 'ESC' key on your keyboard to exit seat selection.",
              font=("Segoe UI", 9, "italic"), fg="#aaaaaa", bg="#1a1a1a").pack(pady=(0, 8))

    screen_box = Frame(seat_window, bg="#0f0f0f")
    screen_box.pack(fill="x", padx=100, pady=(2, 6))
    Frame(screen_box, bg="#FFD700", height=4).pack(fill="x", pady=(0, 2))
    Label(screen_box, text="🎬 ALL EYES THIS WAY • CINEMA SCREEN", font=("Segoe UI", 9, "bold"), fg="#888888",
          bg="#0f0f0f").pack()

    canvas = Canvas(seat_window, bg="#0f0f0f", highlightthickness=0)
    scrollbar = Scrollbar(seat_window, orient="vertical", command=canvas.yview)

    grid_frame = Frame(canvas, bg="#0f0f0f")
    container_window = canvas.create_window((screen_w // 2, 0), window=grid_frame, anchor="n")

    grid_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=2)
    scrollbar.pack(side="right", fill="y", pady=2)

    def _on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    grid_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    grid_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    all_seats = []
    if cursor:
        try:
            cursor.execute(f"SELECT seat_id, seat_number FROM seats WHERE theater_id = {param} ORDER BY seat_id",
                           (theater_id,))
            all_seats = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error querying seats: {e}")
            seat_window.destroy()
            return

    if not all_seats:
        messagebox.showinfo("No Seats", "No seating layout registered for this theater.")
        seat_window.destroy()
        return

    show_id = None
    if cursor:
        try:
            cursor.execute(f"SELECT show_id FROM showtimes WHERE movie_id = {param} AND theater_id = {param} LIMIT 1",
                           (movie_id, theater_id))
            show_row = cursor.fetchone()
            if show_row:
                show_id = show_row[0]
        except Exception:
            try:
                cursor.execute(f"SELECT show_id FROM shows WHERE movie_id = {param} AND theater_id = {param} LIMIT 1",
                               (movie_id, theater_id))
                show_row = cursor.fetchone()
                if show_row:
                    show_id = show_row[0]
            except Exception as e:
                print(f"Notice: Could not resolve show ID: {e}")

    odc_price = 1000.00
    balcony_price = 1500.00

    if cursor:
        try:
            cursor.execute("SELECT price, seat_type FROM ticket")
            ticket_rows = cursor.fetchall()
            for row in ticket_rows:
                price = float(row[0]) if row[0] is not None else 0.0
                seat_type = str(row[1] or "").upper()
                if "ODC" in seat_type:
                    odc_price = price
                elif "BALCONY" in seat_type:
                    balcony_price = price
        except Exception as e:
            print(f"Notice: Ticket price query error: {e}")

    booked_seat_ids = set()
    if cursor:
        try:
            if show_id:
                try:
                    cursor.execute(f"SELECT seat_id FROM bookings WHERE show_id = {param}", (show_id,))
                    booked_seat_rows = cursor.fetchall()
                    booked_seat_ids = {row[0] for row in booked_seat_rows}
                except Exception:
                    cursor.execute(f"SELECT seat_id FROM bookings WHERE showtime_id = {param}", (show_id,))
                    booked_seat_rows = cursor.fetchall()
                    booked_seat_ids = {row[0] for row in booked_seat_rows}
            else:
                cursor.execute(
                    f"SELECT b.seat_id FROM bookings b JOIN seats st ON b.seat_id = st.seat_id WHERE st.theater_id = {param}",
                    (theater_id,))
                booked_seat_rows = cursor.fetchall()
                booked_seat_ids = {row[0] for row in booked_seat_rows}
        except Exception as e:
            print(f"Notice: Error fetching booked seats: {e}")

    odc_seats = all_seats[:10]
    balcony_seats = all_seats[10:20] if len(all_seats) > 10 else []

    odc_seat_ids = {s[0] for s in odc_seats}
    balcony_seat_ids = {s[0] for s in balcony_seats}

    selected_seat_ids = []
    seat_buttons = {}

    def calculate_total_price():
        total = 0.0
        for sid in selected_seat_ids:
            if sid in odc_seat_ids:
                total += odc_price
            elif sid in balcony_seat_ids:
                total += balcony_price
        return total

    def update_summary_label():
        total_amount = calculate_total_price()
        count = len(selected_seat_ids)
        summary_lbl.config(text=f"Selected: {count} Seat(s)   |   Total Amount: Rs. {total_amount:.2f}")

    def toggle_seat(s_id, btn):
        if s_id in selected_seat_ids:
            selected_seat_ids.remove(s_id)
            btn.config(bg="#4CAF50", fg="white")
        else:
            selected_seat_ids.append(s_id)
            btn.config(bg="#FFD700", fg="black")

        update_summary_label()

    columns_per_row = 5

    def render_section(section_title, section_seats, start_row_num, badge_color):
        if not section_seats:
            return

        section_frame = Frame(grid_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#333333",
                              highlightthickness=1)
        section_frame.pack(anchor="center", pady=10, padx=20)

        header_frame = Frame(section_frame, bg="#262626")
        header_frame.pack(fill="x")

        Label(header_frame, text=section_title, font=("Segoe UI", 10, "bold"), fg=badge_color, bg="#262626", padx=15,
              pady=5).pack()

        grid_inner = Frame(section_frame, bg="#1c1c1c", padx=20, pady=12)
        grid_inner.pack()

        for idx, seat in enumerate(section_seats):
            s_id, s_num = seat[0], str(seat[1])
            r_idx = idx // columns_per_row
            c_idx = idx % columns_per_row

            if c_idx == 0:
                Label(grid_inner, text=f"Row {start_row_num + r_idx}", font=("Segoe UI", 9, "bold"), fg="#888888",
                      bg="#1c1c1c", width=6).grid(row=r_idx, column=0, padx=(0, 10), pady=5)

            if s_id in booked_seat_ids:
                btn = Button(grid_inner, text=s_num, width=6, height=2, font=("Segoe UI", 10, "bold"), bg="#E53935",
                             fg="white", state="disabled", bd=0)
            else:
                btn = Button(grid_inner, text=s_num, width=6, height=2, font=("Segoe UI", 10, "bold"), bg="#4CAF50",
                             fg="white", cursor="hand2", bd=0)
                btn.config(command=lambda sid=s_id, b=btn: toggle_seat(sid, b))

            btn.grid(row=r_idx, column=c_idx + 1, padx=6, pady=5)
            seat_buttons[s_id] = btn

    render_section(f"ODC SECTION  •  Rs. {odc_price:.2f} per seat", odc_seats, start_row_num=1, badge_color="#00E676")
    render_section(f"BALCONY SECTION  •  Rs. {balcony_price:.2f} per seat", balcony_seats, start_row_num=3,
                   badge_color="#FFD700")

    bottom_panel = Frame(seat_window, bg="#1a1a1a", bd=1, relief="groove")
    bottom_panel.pack(side="bottom", fill="x", ipady=8)

    legend_frame = Frame(bottom_panel, bg="#1a1a1a")
    legend_frame.pack(pady=(4, 4))

    Label(legend_frame, text="■ Available", fg="#4CAF50", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left",
                                                                                                            padx=15)
    Label(legend_frame, text="■ Selected", fg="#FFD700", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left",
                                                                                                           padx=15)
    Label(legend_frame, text="■ Booked", fg="#E53935", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left",
                                                                                                         padx=15)

    summary_lbl = Label(bottom_panel, text="Selected: 0 Seat(s)   |   Total Amount: Rs. 0.00",
                        font=("Segoe UI", 11, "bold"), fg="white", bg="#2b2b2b", padx=16, pady=5, bd=1, relief="solid")
    summary_lbl.pack(pady=(0, 8))

    def confirm_booking():
        if not selected_seat_ids:
            messagebox.showwarning("Warning", "Please select at least one seat before proceeding.")
            return

        final_amount = calculate_total_price()
        now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if conn and cursor:
            try:
                for s_id in selected_seat_ids:
                    if show_id:
                        cursor.execute(
                            f"INSERT INTO bookings (customer_id, show_id, seat_id, booking_date) VALUES ({param}, {param}, {param}, {param})",
                            (customer_id, show_id, s_id, now_timestamp))
                    else:
                        cursor.execute(
                            f"INSERT INTO bookings (customer_id, seat_id, booking_date) VALUES ({param}, {param}, {param})",
                            (customer_id, s_id, now_timestamp))

                conn.commit()
                seat_window.destroy()

                try:
                    show_payment_window(parent, customer_id, final_amount)
                except TypeError:
                    show_payment_window(parent, customer_id)

            except Exception as e:
                if hasattr(conn, "rollback"):
                    conn.rollback()
                messagebox.showerror("Database Error", f"Booking failed:\n{e}")
        else:
            seat_window.destroy()
            try:
                show_payment_window(parent, customer_id, final_amount)
            except TypeError:
                show_payment_window(parent, customer_id)

    btn_container = Frame(bottom_panel, bg="#1a1a1a")
    btn_container.pack(pady=(2, 4))

    btn_back = Button(
        btn_container, text="Cancel", bg="#E53935", fg="white", activebackground="#d32f2f", activeforeground="white",
        font=("Segoe UI", 11, "bold"), width=12, cursor="hand2", bd=0, command=seat_window.destroy
    )
    btn_back.pack(side="left", ipady=5, padx=(0, 10))

    btn_confirm = Button(
        btn_container, text="Proceed to Payment  💳", bg="#4CAF50", fg="white", activebackground="#45a049",
        activeforeground="white", font=("Segoe UI", 11, "bold"), width=24, cursor="hand2", bd=0, command=confirm_booking
    )
    btn_confirm.pack(side="right", ipady=5, padx=(10, 0))


def generate_pdf_ticket(booking_id, customer_id, payment_id, total_amount, payment_method):
    try:
        tickets_dir = os.path.join(project_root, "Tickets")
        os.makedirs(tickets_dir, exist_ok=True)

        pdf_filename = os.path.join(tickets_dir, f"Ticket_Booking_{booking_id}.pdf")

        movie_title = "AA Cinema Movie"
        screen_name = "Screen 1"
        theater_location = "Main Branch"
        seats_str = "Standard"
        seat_id_val = "N/A"
        customer_name = f"Customer #{customer_id}"

        if cursor:
            try:
                q_cust = f"SELECT name FROM customers WHERE customer_id = {PH}"
                cursor.execute(q_cust, (customer_id,))
                c_row = cursor.fetchone()
                if c_row:
                    customer_name = c_row[0] if isinstance(c_row, (tuple, list)) else c_row.get('name', customer_name)

                if IS_SQLITE:
                    seat_num_concat = "GROUP_CONCAT(DISTINCT s.seat_number || ' (' || COALESCE(s.seat_type, 'Standard') || ')')"
                    seat_id_concat = "GROUP_CONCAT(DISTINCT b.seat_id)"
                else:
                    seat_num_concat = "GROUP_CONCAT(DISTINCT CONCAT(s.seat_number, ' (', COALESCE(s.seat_type, 'Standard'), ')'))"
                    seat_id_concat = "GROUP_CONCAT(DISTINCT b.seat_id)"

                q_det = f"""
                    SELECT 
                        m.title AS movie_title,
                        t.theater_name AS hall_name,
                        t.location AS hall_location,
                        {seat_num_concat} AS seats_with_types,
                        {seat_id_concat} AS seat_ids
                    FROM bookings b
                    LEFT JOIN showtimes sh ON b.show_id = sh.show_id
                    LEFT JOIN movies m ON sh.movie_id = m.movie_id
                    LEFT JOIN theaters t ON sh.theater_id = t.theater_id
                    LEFT JOIN seats s ON b.seat_id = s.seat_id
                    WHERE b.customer_id = {PH} 
                      AND b.show_id = (SELECT show_id FROM bookings WHERE booking_id = {PH} LIMIT 1)
                    GROUP BY m.title, t.theater_name, t.location
                """
                cursor.execute(q_det, (customer_id, booking_id))
                row = cursor.fetchone()

                if not row or not (row[0] if isinstance(row, (tuple, list)) else row.get('movie_title')):
                    q_fallback = f"""
                        SELECT 
                            m.title AS movie_title,
                            t.theater_name AS hall_name,
                            t.location AS hall_location,
                            {seat_num_concat} AS seats_with_types,
                            {seat_id_concat} AS seat_ids
                        FROM bookings b
                        LEFT JOIN showtimes sh ON b.show_id = sh.show_id
                        LEFT JOIN movies m ON sh.movie_id = m.movie_id
                        LEFT JOIN theaters t ON sh.theater_id = t.theater_id
                        LEFT JOIN seats s ON b.seat_id = s.seat_id
                        WHERE b.customer_id = {PH}
                        GROUP BY m.title, t.theater_name, t.location
                        ORDER BY MAX(b.booking_id) DESC
                        LIMIT 1
                    """
                    cursor.execute(q_fallback, (customer_id,))
                    row = cursor.fetchone()

                if row:
                    if isinstance(row, dict):
                        movie_title = str(row.get('movie_title') or movie_title)
                        screen_name = str(row.get('hall_name') or screen_name)
                        theater_location = str(row.get('hall_location') or theater_location)
                        seats_str = str(row.get('seats_with_types') or seats_str)
                        seat_id_val = str(row.get('seat_ids') or seat_id_val)
                    else:
                        movie_title = str(row[0]) if row[0] else movie_title
                        screen_name = str(row[1]) if row[1] else screen_name
                        theater_location = str(row[2]) if row[2] else theater_location
                        seats_str = str(row[3]) if row[3] else seats_str
                        seat_id_val = str(row[4]) if row[4] else seat_id_val

            except Exception as db_err:
                print(f"Notice: Ticket query database error: {db_err}")

        seats_str = seats_str.replace(",", ", ")
        seat_id_val = seat_id_val.replace(",", ", ")

        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )

        styles = getSampleStyleSheet()

        GOLD = colors.HexColor("#D4AF37")
        DARK_BG = colors.HexColor("#1A1A1A")
        LIGHT_BG = colors.HexColor("#FAFAFA")
        TEXT_DARK = colors.HexColor("#222222")
        TEXT_MUTED = colors.HexColor("#666666")

        title_style = ParagraphStyle('HeaderTitle', fontName='Helvetica-Bold', fontSize=18, textColor=GOLD, leading=22)
        subtitle_style = ParagraphStyle('HeaderSub', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white,
                                        leading=10)
        movie_style = ParagraphStyle('MovieTitle', fontName='Helvetica-Bold', fontSize=15, textColor=DARK_BG,
                                     leading=19)
        label_style = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, leading=10)
        val_style = ParagraphStyle('Value', fontName='Helvetica-Bold', fontSize=10, textColor=TEXT_DARK, leading=13)
        ref_badge_style = ParagraphStyle('RefBadge', fontName='Helvetica-Bold', fontSize=9, textColor=GOLD, alignment=1)
        price_badge_style = ParagraphStyle('PriceBadge', fontName='Helvetica-Bold', fontSize=11,
                                           textColor=colors.HexColor("#2E7D32"), alignment=1)

        elements = []

        logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

        header_text = [
            Paragraph("AA CINEMA", title_style),
            Spacer(1, 2),
            Paragraph("OFFICIAL E-TICKET & PASS", subtitle_style)
        ]

        if logo_path and os.path.exists(logo_path):
            logo_img = RLImage(logo_path, width=0.75 * inch, height=0.75 * inch)
            header_data = [[logo_img, header_text]]
        else:
            logo_fallback = Paragraph("🍿", ParagraphStyle('LogoFallback', fontSize=28, alignment=1))
            header_data = [[logo_fallback, header_text]]

        header_table = Table(header_data, colWidths=[0.9 * inch, 5.3 * inch])
        header_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(header_table)

        ref_box = Table([[Paragraph(f"#BK-{booking_id}", ref_badge_style)]], colWidths=[1.4 * inch])
        ref_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), DARK_BG),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        top_info_data = [
            [
                [Paragraph("MOVIE", label_style), Spacer(1, 2), Paragraph(movie_title, movie_style)],
                [Paragraph("BOOKING REF", label_style), Spacer(1, 4), ref_box]
            ]
        ]
        top_info_table = Table(top_info_data, colWidths=[3.9 * inch, 1.9 * inch])
        top_info_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        grid_data = [
            [Paragraph("PASSENGER / CUSTOMER", label_style), Paragraph("CINEMA HALL", label_style)],
            [Paragraph(customer_name, val_style), Paragraph(screen_name, val_style)],
            [Spacer(1, 6), Spacer(1, 6)],
            [Paragraph("THEATER LOCATION", label_style), Paragraph("SEAT NUMBER / TYPE", label_style)],
            [Paragraph(theater_location, val_style), Paragraph(seats_str, val_style)],
            [Spacer(1, 6), Spacer(1, 6)],
            [Paragraph("SEAT ID(S)", label_style), Paragraph("PAYMENT METHOD", label_style)],
            [Paragraph(seat_id_val, val_style), Paragraph(payment_method, val_style)]
        ]
        grid_table = Table(grid_data, colWidths=[2.9 * inch, 2.9 * inch])
        grid_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 1),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ]))

        dashed_line = HRFlowable(
            width="100%", thickness=1, color=colors.HexColor("#CCCCCC"),
            spaceBefore=8, spaceAfter=8, hAlign='CENTER', vAlign='MIDDLE', dash=[4, 4]
        )

        price_box = Table([[Paragraph(f"Rs. {total_amount:.2f}", price_badge_style)]], colWidths=[1.5 * inch])
        price_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#E8F5E9")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#A5D6A7")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))

        stub_data = [
            [
                [Paragraph("ENTRY PASS REQUIREMENT", label_style), Spacer(1, 2),
                 Paragraph("Present this PDF pass at the entry gate.", val_style)],
                [Paragraph("TOTAL PAID", label_style), Spacer(1, 4), price_box]
            ]
        ]
        stub_table = Table(stub_data, colWidths=[3.9 * inch, 1.9 * inch])
        stub_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))

        ticket_body_data = [
            [top_info_table],
            [Spacer(1, 8)],
            [grid_table],
            [dashed_line],
            [stub_table]
        ]

        ticket_body = Table(ticket_body_data, colWidths=[6.2 * inch])
        ticket_body.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
            ('BOX', (0, 0), (-1, -1), 1.5, GOLD),
            ('TOPPADDING', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
            ('LEFTPADDING', (0, 0), (-1, -1), 14),
            ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ]))

        elements.append(ticket_body)
        elements.append(Spacer(1, 0.25 * inch))

        footer_style = ParagraphStyle('FooterText', fontName='Helvetica-Oblique', fontSize=8, textColor=TEXT_MUTED,
                                      alignment=1)
        elements.append(Paragraph("Thank you for choosing AA Cinema. Enjoy your movie!", footer_style))

        doc.build(elements)
        webbrowser.open(f"file://{os.path.abspath(pdf_filename)}")
        return pdf_filename

    except Exception as e:
        print(f"Error generating PDF ticket: {e}")
        return None


def show_payment_window(parent, customer_id, total_amount=0.0):
    pay_window = Toplevel(parent)
    pay_window.title("Checkout & Payment - AA Cinema")
    pay_window.configure(bg="#0f0f0f")

    image_refs_p = []
    pay_window.image_refs = image_refs_p

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    pay_window.geometry(f"{screen_w}x{screen_h}+0+0")
    pay_window.deiconify()
    try:
        pay_window.state('zoomed')
    except Exception:
        pass

    pay_window.lift()
    pay_window.focus_force()
    pay_window.bind("<Escape>", lambda e: pay_window.destroy())

    header_top_bar = Frame(pay_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(pay_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar, text="🍿 AA CINEMA - CHECKOUT & PAYMENT",
        font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_datetime_p():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if pay_window.winfo_exists():
            pay_window.after(1000, update_datetime_p)

    update_datetime_p()

    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
    card_logo_img = None
    window_logo = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo = ImageTk.PhotoImage(logo_raw, master=pay_window)
            pay_window.iconphoto(False, window_logo)
            image_refs_p.append(window_logo)

            logo_resized = logo_raw.resize((55, 55), Image.LANCZOS)
            card_logo_img = ImageTk.PhotoImage(logo_resized, master=pay_window)
            pay_window.card_logo_img = card_logo_img
            image_refs_p.append(card_logo_img)
        except Exception as e:
            print(f"Could not load logo in pay.py: {e}")

    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.PNG", "background.png"])
    bg_raw_img = None

    if bg_path and os.path.exists(bg_path):
        try:
            bg_raw_img = Image.open(bg_path)
        except Exception as e:
            print(f"Could not load background image in pay.py: {e}")

    recent_bookings = []
    booked_count = 0

    if cursor:
        try:
            query_rec = f"SELECT booking_id, seat_id FROM bookings WHERE customer_id = {PH} ORDER BY booking_id DESC LIMIT 10"
            cursor.execute(query_rec, (customer_id,))
            recent_bookings = cursor.fetchall()
            booked_count = len(recent_bookings)

            if total_amount <= 0.0 and recent_bookings:
                try:
                    q_price = f"SELECT t.price FROM bookings b JOIN seats s ON b.seat_id = s.seat_id JOIN ticket t ON UPPER(s.seat_type) = UPPER(t.seat_type) WHERE b.customer_id = {PH}"
                    cursor.execute(q_price, (customer_id,))
                    price_rows = cursor.fetchall()

                    if price_rows:
                        total_amount = sum(float(p[0]) for p in price_rows if p[0] is not None)
                    else:
                        total_amount = booked_count * 1000.0
                except Exception as e:
                    print(f"Notice: Price calculation fallback in pay.py: {e}")
                    total_amount = booked_count * 1000.0
        except Exception as e:
            print(f"Notice: Error retrieving booking details in pay.py: {e}")

    outer_container = Frame(pay_window, bg="#0f0f0f")
    outer_container.pack(side="top", fill="both", expand=True)

    canvas = Canvas(outer_container, bg="#0f0f0f", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(outer_container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    center_frame = Frame(canvas, bg="#0f0f0f")
    canvas_window = canvas.create_window((screen_w // 2, 20), window=center_frame, anchor="n")

    current_bg_photo = None

    def reconfigure_canvas(event=None):
        nonlocal current_bg_photo
        cw = max(canvas.winfo_width(), screen_w)
        ch = max(canvas.winfo_height(), screen_h)

        if bg_raw_img:
            try:
                resized_bg = bg_raw_img.resize((cw, ch), Image.LANCZOS)
                current_bg_photo = ImageTk.PhotoImage(resized_bg, master=pay_window)
                canvas.delete("bg_image")
                canvas.create_image(0, 0, image=current_bg_photo, anchor="nw", tags="bg_image")
                canvas.tag_lower("bg_image")
                image_refs_p.append(current_bg_photo)
            except Exception as e:
                print(f"Error rendering background frame: {e}")

        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.coords(canvas_window, cw // 2, 20)

    center_frame.bind("<Configure>", reconfigure_canvas)
    canvas.bind("<Configure>", reconfigure_canvas)

    def _on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    center_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    center_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    card = Frame(center_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#333333", highlightthickness=1,
                 padx=45, pady=30)
    card.pack(anchor="center", pady=20)

    if card_logo_img:
        logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
        logo_lbl.image = card_logo_img
        logo_lbl.pack(pady=(0, 8))

    Label(card, text="CHECKOUT & BILLING", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#1c1c1c").pack(pady=(0, 2))
    Label(card, text="Payment & Checkout", font=("Segoe UI", 20, "bold"), fg="white", bg="#1c1c1c").pack(pady=(0, 15))

    summary_frame = Frame(card, bg="#262626", bd=1, relief="solid", highlightbackground="#3d3d3d", highlightthickness=1)
    summary_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=5)

    Label(summary_frame, text="ORDER SUMMARY", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#262626").pack(
        anchor="w", padx=15, pady=(10, 4))
    Label(summary_frame, text=f"Total Seats Selected: {booked_count}", font=("Segoe UI", 10), fg="#dddddd",
          bg="#262626").pack(anchor="w", padx=15, pady=2)
    Label(summary_frame, text=f"Total Amount Due: Rs. {total_amount:.2f}", font=("Segoe UI", 12, "bold"), fg="#00E676",
          bg="#262626").pack(anchor="w", padx=15, pady=(2, 10))

    Label(card, text="SELECT PAYMENT METHOD", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#1c1c1c",
          anchor="w").pack(fill="x", pady=(0, 8))

    payment_method_var = StringVar(value="Credit / Debit Card")

    methods = [
        ("💳 Credit / Debit Card", "Credit / Debit Card"),
        ("📱 Mobile Wallet (Apple Pay / Google Pay)", "Mobile Wallet"),
        ("💵 Pay at Counter", "Pay at Counter")
    ]

    for label_text, value_text in methods:
        Radiobutton(
            card, text=label_text, variable=payment_method_var, value=value_text,
            font=("Segoe UI", 10, "bold"), fg="white", bg="#1c1c1c", selectcolor="#2b2b2b",
            activebackground="#1c1c1c", activeforeground="#FFD700", cursor="hand2"
        ).pack(anchor="w", padx=10, pady=3)

    card_frame = Frame(card, bg="#1c1c1c")
    Label(card_frame, text="Cardholder Name", font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w",
                                                                                                             pady=(8,
                                                                                                                   2))
    card_name_entry = Entry(card_frame, font=("Segoe UI", 10), bg="#2b2b2b", fg="white", insertbackground="white", bd=1,
                            relief="solid")
    card_name_entry.pack(fill="x", pady=(0, 8), ipady=5)

    Label(card_frame, text="Card Number", font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w",
                                                                                                         pady=(2, 2))
    card_num_entry = Entry(card_frame, font=("Segoe UI", 10), bg="#2b2b2b", fg="white", insertbackground="white", bd=1,
                           relief="solid")
    card_num_entry.pack(fill="x", pady=(0, 5), ipady=5)

    wallet_frame = Frame(card, bg="#1c1c1c")
    Label(wallet_frame, text="Click below to complete authorization on your wallet platform:", font=("Segoe UI", 9),
          fg="#aaaaaa", bg="#1c1c1c").pack(anchor="w", pady=(10, 8))

    btn_subframe = Frame(wallet_frame, bg="#1c1c1c")
    btn_subframe.pack(fill="x")

    Button(
        btn_subframe, text="🍎 Open Apple Pay", bg="#2b2b2b", fg="white", activebackground="#3d3d3d",
        activeforeground="white", font=("Segoe UI", 9, "bold"), cursor="hand2", bd=0,
        command=lambda: webbrowser.open("https://www.apple.com/apple-pay/")
    ).pack(side="left", padx=(0, 6), expand=True, fill="x", ipady=5)

    Button(
        btn_subframe, text="🌐 Open Google Pay", bg="#2b2b2b", fg="white", activebackground="#3d3d3d",
        activeforeground="white", font=("Segoe UI", 9, "bold"), cursor="hand2", bd=0,
        command=lambda: webbrowser.open("https://pay.google.com/")
    ).pack(side="left", expand=True, fill="x", ipady=5)

    def on_method_change(*args):
        selected = payment_method_var.get()
        if selected == "Credit / Debit Card":
            wallet_frame.pack_forget()
            card_frame.pack(fill="x", pady=10)
        elif selected == "Mobile Wallet":
            card_frame.pack_forget()
            wallet_frame.pack(fill="x", pady=10)
        else:
            card_frame.pack_forget()
            wallet_frame.pack_forget()

    payment_method_var.trace_add("write", on_method_change)
    on_method_change()

    def show_card_success_modal(amount):
        dlg = Toplevel(pay_window)
        dlg.title("Payment Successful - AA Cinema")
        dlg.configure(bg="#1c1c1c")
        dlg.transient(pay_window)
        dlg.grab_set()

        if window_logo:
            try:
                dlg.iconphoto(False, window_logo)
            except Exception as e:
                print(f"Could not set modal title icon: {e}")

        dw, dh = 400, 350
        sx = (pay_window.winfo_screenwidth() - dw) // 2
        sy = (pay_window.winfo_screenheight() - dh) // 2
        dlg.geometry(f"{dw}x{dh}+{sx}+{sy}")
        dlg.resizable(False, False)

        main_frame = Frame(dlg, bg="#1c1c1c", padx=20, pady=15)
        main_frame.pack(fill="both", expand=True)

        target_filename = "Paymentsuccess.PNG"
        success_img_path = find_file([target_filename, "paymentsuccess.png"])

        if success_img_path and os.path.exists(success_img_path):
            try:
                raw_img = Image.open(success_img_path)
                resized = raw_img.resize((150, 100), RESAMPLE_FILTER)
                ph = ImageTk.PhotoImage(resized, master=dlg)

                img_lbl = Label(main_frame, image=ph, bg="#1c1c1c")
                img_lbl.image = ph
                dlg.ph = ph
                img_lbl.pack(pady=(5, 10))
            except Exception as e:
                print(f"Error loading success image: {e}")

        Label(
            main_frame,
            text="Card Payment Successful! 💳",
            font=("Segoe UI", 12, "bold"),
            fg="#00E676",
            bg="#1c1c1c"
        ).pack(pady=(0, 8))

        try:
            amt_val = float(amount)
            amt_str = f"{amt_val:.2f}"
        except (ValueError, TypeError):
            amt_str = str(amount)

        msg_text = (
            f"Payment of Rs. {amt_str} via Credit / Debit Card\n"
            f"was processed successfully!\n\n"
            f"Your PDF ticket pass has been generated."
        )

        Label(
            main_frame,
            text=msg_text,
            font=("Segoe UI", 9),
            fg="#dddddd",
            bg="#1c1c1c",
            justify="center"
        ).pack(pady=(0, 15))

        btn_close = Button(
            main_frame,
            text="OK",
            bg="#00E676",
            fg="black",
            activebackground="#00c853",
            activeforeground="black",
            font=("Segoe UI", 10, "bold"),
            width=12,
            bd=0,
            cursor="hand2",
            command=dlg.destroy
        )
        btn_close.pack(pady=(0, 5), ipady=3)

        dlg.wait_window()

    def process_payment():
        method = payment_method_var.get()
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if method == "Credit / Debit Card":
            c_name = card_name_entry.get().strip()
            c_num = card_num_entry.get().strip()
            if not c_name or not c_num:
                messagebox.showerror("Input Error", "Please enter valid card details.")
                return
            status_val = 'Completed'
        elif method == "Pay at Counter":
            status_val = 'Pending Counter Payment'
        else:
            status_val = 'Completed'

        inserted_booking_id = 1001
        inserted_payment_id = 5001

        if conn and cursor:
            try:
                if recent_bookings:
                    primary_booking_id = recent_bookings[0][0]
                    q_pay = f"INSERT INTO payments (booking_id, customer_id, amount, payment_date, payment_method, payment_status) VALUES ({PH}, {PH}, {PH}, {PH}, {PH}, {PH})"
                    cursor.execute(q_pay,
                                   (primary_booking_id, customer_id, total_amount, payment_date, method, status_val))
                    inserted_booking_id = primary_booking_id
                else:
                    q_pay = f"INSERT INTO payments (customer_id, amount, payment_date, payment_method, payment_status) VALUES ({PH}, {PH}, {PH}, {PH}, {PH})"
                    cursor.execute(q_pay, (customer_id, total_amount, payment_date, method, status_val))
                    inserted_booking_id = 1001

                last_id = getattr(cursor, 'lastrowid', None)
                inserted_payment_id = last_id if last_id else 5001
                conn.commit()
            except Exception as e:
                if hasattr(conn, 'rollback'):
                    conn.rollback()
                print(f"Database error during payment: {e}")
                messagebox.showerror("Database Error", f"Payment processing error:\n{e}")
                return

        generate_pdf_ticket(
            booking_id=inserted_booking_id,
            customer_id=customer_id,
            payment_id=inserted_payment_id,
            total_amount=total_amount,
            payment_method=method
        )

        if method == "Credit / Debit Card":
            show_card_success_modal(total_amount)
        elif method == "Mobile Wallet":
            messagebox.showinfo(
                "Wallet Payment Successful! 📱",
                f"Payment of Rs. {total_amount:.2f} via Mobile Wallet was verified!\n\nYour PDF ticket pass has been saved to 'Tickets/'."
            )
        elif method == "Pay at Counter":
            messagebox.showinfo(
                "Seats Reserved! 💵",
                f"Your seats have been successfully reserved!\n\nTotal Amount Due: Rs. {total_amount:.2f}\nYour printable reservation voucher has been created."
            )

        pay_window.destroy()
        if parent:
            parent.deiconify()
            parent.lift()
            parent.focus_force()

    action_frame = Frame(card, bg="#1c1c1c")
    action_frame.pack(fill="x", pady=(20, 0))

    btn_back = Button(
        action_frame, text="Cancel", bg="#E53935", fg="white", activebackground="#d32f2f", activeforeground="white",
        font=("Segoe UI", 11, "bold"), width=12, cursor="hand2", bd=0, command=pay_window.destroy
    )
    btn_back.pack(side="left", ipady=6, padx=(0, 8))

    btn_confirm = Button(
        action_frame, text="Confirm & Pay 🎟️", bg="#4CAF50", fg="white", activebackground="#45a049",
        activeforeground="white", font=("Segoe UI", 11, "bold"), width=20, cursor="hand2", bd=0, command=process_payment
    )
    btn_confirm.pack(side="right", ipady=6, padx=(8, 0))


# ------------------ Main UI Action Buttons ------------------
btn_showing = Button(
    card_frame,
    text="🎬   Now Showing Movies",
    font=("Segoe UI", 12, "bold"),
    bg="#FFD700",
    fg="#121212",
    activebackground="#E6C200",
    activeforeground="#121212",
    width=26,
    height=1,
    cursor="hand2",
    bd=0,
    command=lambda: open_showing_movies(root)
)
btn_showing.pack(pady=7, ipady=5)
add_hover_effect(btn_showing, "#FFD700", "#FFF066", "#121212", "#121212")


def view_movies1(root):
    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

    movie_window = Toplevel(root)
    movie_window.title("Upcoming Movies - AA Cinema")
    movie_window.configure(bg="#0f0f0f")

    image_refs = []
    movie_window.image_refs = image_refs

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    movie_window.geometry(f"{screen_w}x{screen_h}+0+0")

    try:
        movie_window.state('zoomed')
    except Exception:
        pass

    movie_window.bind("<Escape>", lambda e: movie_window.state('normal'))
    movie_window.deiconify()
    movie_window.lift()
    movie_window.focus_force()

    header_top_bar = Frame(movie_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(movie_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar, text="🍿 AA CINEMA - UPCOMING MOVIES",
        font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=6
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=5)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_datetime_u():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if movie_window.winfo_exists():
            movie_window.after(1000, update_datetime_u)

    update_datetime_u()

    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=movie_window)
            image_refs.append(bg_photo)

            bg_label = Label(movie_window, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in upcoming movies: {e}")

    window_logo_img = None
    fallback_logo_img = None
    header_logo_img = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo_img = ImageTk.PhotoImage(logo_raw, master=movie_window)
            movie_window.iconphoto(False, window_logo_img)
            image_refs.append(window_logo_img)

            header_logo_resized = logo_raw.resize((35, 35), Image.LANCZOS)
            header_logo_img = ImageTk.PhotoImage(header_logo_resized, master=movie_window)
            image_refs.append(header_logo_img)

            fallback_logo_resized = logo_raw.resize((120, 120), Image.LANCZOS)
            fallback_logo_img = ImageTk.PhotoImage(fallback_logo_resized, master=movie_window)
            image_refs.append(fallback_logo_img)
        except Exception as e:
            print(f"Could not load cinema logo image: {e}")

    hero_frame = Frame(movie_window, bg="#1a1a1a", bd=1, relief="solid", highlightbackground="#D4AF37",
                       highlightthickness=1)
    hero_frame.pack(fill="x", padx=20, pady=(15, 10))

    Label(hero_frame, text="✦ EXCLUSIVE FIRST LOOK ✦", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#1a1a1a").pack(
        pady=(12, 2))

    title_box = Frame(hero_frame, bg="#1a1a1a")
    title_box.pack(pady=(0, 2))

    if header_logo_img:
        hdr_logo_lbl = Label(title_box, image=header_logo_img, bg="#1a1a1a")
        hdr_logo_lbl.image = header_logo_img
        hdr_logo_lbl.pack(side="left", padx=(0, 10))

    Label(title_box, text="COMING SOON TO AA CINEMA", font=("Segoe UI", 22, "bold"), fg="white", bg="#1a1a1a").pack(
        side="left")
    Label(hero_frame, text="Press 'ESC' key on your keyboard to exit full screen mode.", font=("Segoe UI", 9, "italic"),
          fg="#aaaaaa", bg="#1a1a1a").pack(pady=(0, 10))

    canvas = Canvas(movie_window, bg="#0f0f0f", highlightthickness=0)
    scrollbar = Scrollbar(movie_window, orient="vertical", command=canvas.yview)

    container = Frame(canvas, bg="#0f0f0f")
    container_window = canvas.create_window((screen_w // 2, 0), window=container, anchor="n")

    container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    def _on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    container.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    container.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    movies = []
    if cursor:
        try:
            cursor.execute("""
                SELECT title, duration, language, release_date, poster
                FROM upcomingmovies
            """)
            movies = cursor.fetchall()
        except Exception as db_err:
            print(f"Database query error in upcomingmovies: {db_err}")

    columns = max(3, screen_w // 250)

    for index, movie in enumerate(movies):
        title, duration, language, release, poster_filename = movie

        card = Frame(container, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#333333", highlightthickness=1)
        row = index // columns
        col = index % columns
        card.grid(row=row, column=col, padx=14, pady=16, sticky="n")

        poster_frame = Frame(card, bg="#0d0d0d", bd=1, relief="solid", width=175, height=250)
        poster_frame.pack_propagate(False)
        poster_frame.pack(padx=10, pady=(10, 6))

        poster_loaded = False
        poster_path = resolve_poster_path(poster_filename)

        if poster_path and os.path.exists(poster_path):
            try:
                raw_img = Image.open(poster_path)
                resized_img = raw_img.resize((175, 250), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized_img, master=movie_window)
                image_refs.append(photo)

                img_label = Label(poster_frame, image=photo, bg="#0d0d0d")
                img_label.image = photo
                img_label.pack(fill="both", expand=True)
                poster_loaded = True
            except Exception as img_err:
                print(f"Error rendering {poster_path}: {img_err}")

        if not poster_loaded:
            fallback_box = Frame(poster_frame, bg="#181818")
            fallback_box.pack(fill="both", expand=True)

            if fallback_logo_img:
                logo_lbl = Label(fallback_box, image=fallback_logo_img, bg="#181818")
                logo_lbl.image = fallback_logo_img
                logo_lbl.pack(expand=True, pady=(15, 0))

            Label(fallback_box, text="AA CINEMA", font=("Segoe UI", 9, "bold"), bg="#181818", fg="#888888").pack(
                pady=(0, 15))

        info_frame = Frame(card, bg="#1c1c1c")
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        Label(info_frame, text=title, font=("Segoe UI", 10, "bold"), fg="white", bg="#1c1c1c", wraplength=165,
              justify=CENTER).pack(pady=(4, 4))
        Label(info_frame, text=f"⏱ {duration} • 🌐 {language}", font=("Segoe UI", 8), fg="#aaaaaa", bg="#1c1c1c").pack(
            pady=(0, 6))

        badge = Frame(info_frame, bg="#332200", bd=1, relief="solid")
        badge.pack(fill="x", pady=(2, 6))
        Label(badge, text=f"🗓 Coming: {release}", font=("Segoe UI", 8, "bold"), fg="#FFD700", bg="#332200").pack(pady=3)


btn_upcoming = Button(
    card_frame,
    text="📅   Upcoming Releases",
    font=("Segoe UI", 12, "bold"),
    bg="#FF9800",
    fg="#121212",
    activebackground="#e68a00",
    activeforeground="#121212",
    width=26,
    height=1,
    cursor="hand2",
    bd=0,
    command=lambda: view_movies1(root)
)
btn_upcoming.pack(pady=7, ipady=5)
add_hover_effect(btn_upcoming, "#262626", "#333333", "#ffffff", "#FFD700")


def verify_admin_credentials(admin_id, password):
    if not cursor:
        messagebox.showerror("Database Error", "Database connection is not available.")
        return False

    try:
        query = "SELECT * FROM admin WHERE admin_id = %s AND password = %s"
        cursor.execute(query, (admin_id, password))
        result = cursor.fetchone()
        return result is not None
    except Exception as e:
        messagebox.showerror("Query Error", f"Failed to authenticate admin: {e}")
        return False


def show_login_window(parent):
    login_win = Toplevel(parent)
    login_win.title("Admin Authentication - AA Cinema")
    login_win.configure(bg="#0f0f0f")
    login_win.resizable(False, False)
    login_win.transient(parent)

    app_icon = load_cinema_logo(size=(32, 32))
    if app_icon:
        login_win.icon_photo_ref = app_icon
        login_win.iconphoto(False, login_win.icon_photo_ref)

    w, h = 380, 450
    sw = parent.winfo_screenwidth()
    sh = parent.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    login_win.geometry(f"{w}x{h}+{x}+{y}")

    header_top_bar = Frame(login_win, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(login_win, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    lbl_time = Label(header_top_bar, font=("Segoe UI", 8, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="right", padx=10, pady=4)

    lbl_date = Label(header_top_bar, font=("Segoe UI", 8, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="right", padx=(10, 0), pady=4)

    def update_login_datetime():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%a, %b %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if login_win.winfo_exists():
            login_win.after(1000, update_login_datetime)

    update_login_datetime()

    logo_img = load_cinema_logo(size=(60, 60))
    if logo_img:
        login_win.logo_ref = logo_img
        Label(login_win, image=logo_img, bg="#0f0f0f").pack(pady=(15, 5))

    Label(login_win, text="ADMIN LOGIN", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(pady=(0, 15))

    form_frame = Frame(login_win, bg="#1c1c1c", padx=25, pady=20, bd=1, relief="solid")
    form_frame.pack(fill="x", padx=30)

    Label(form_frame, text="Admin ID:", font=("Segoe UI", 10, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w",
                                                                                                        pady=(0, 2))
    entry_id = Entry(form_frame, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", insertbackground="white", bd=1,
                     relief="solid")
    entry_id.pack(fill="x", pady=(0, 12))

    Label(form_frame, text="Password:", font=("Segoe UI", 10, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w",
                                                                                                        pady=(0, 2))
    entry_pass = Entry(form_frame, font=("Segoe UI", 11), show="•", bg="#2b2b2b", fg="white", insertbackground="white",
                       bd=1, relief="solid")
    entry_pass.pack(fill="x", pady=(0, 15))

    def attempt_login(event=None):
        admin_id = entry_id.get().strip()
        password = entry_pass.get().strip()

        if not admin_id or not password:
            messagebox.showwarning("Input Required", "Please enter both Admin ID and Password.", parent=login_win)
            return

        if verify_admin_credentials(admin_id, password):
            login_win.grab_release()
            login_win.destroy()
            show_admin_panel(parent)
        else:
            messagebox.showerror("Access Denied", "Invalid Admin ID or Password.", parent=login_win)
            entry_pass.delete(0, tk.END)

    btn_login = Button(
        form_frame, text="LOG IN", font=("Segoe UI", 10, "bold"),
        bg="#FFD700", fg="#000000", activebackground="#e6c200", activeforeground="#000000",
        bd=0, pady=7, cursor="hand2", command=attempt_login
    )
    btn_login.pack(fill="x")

    login_win.bind("<Return>", attempt_login)
    login_win.grab_set()
    entry_id.focus_set()


def show_admin_panel(parent):
    admin_window = Toplevel(parent)
    admin_window.title("Admin Panel - AA Cinema Management System")
    admin_window.configure(bg="#0f0f0f")
    admin_window.transient(parent)

    app_icon = load_cinema_logo(size=(32, 32))
    if app_icon:
        admin_window.icon_photo_ref = app_icon
        admin_window.iconphoto(False, admin_window.icon_photo_ref)

    admin_window.image_refs = []

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()
    admin_window.geometry(f"{screen_w}x{screen_h}+0+0")

    try:
        admin_window.state('zoomed')
    except Exception:
        pass

    admin_window.deiconify()
    admin_window.lift()
    admin_window.focus_force()

    Label(admin_window, text="Welcome to Admin Panel", font=("Segoe UI", 18, "bold"), fg="#FFD700", bg="#0f0f0f").pack(
        pady=50)


btn_admin = Button(
    card_frame,
    text="⚙️   Admin Control Panel",
    font=("Segoe UI", 12, "bold"),
    bg="#333333",
    fg="#FFFFFF",
    activebackground="#444444",
    activeforeground="#FFFFFF",
    width=26,
    height=1,
    cursor="hand2",
    bd=0,
    command=lambda: show_login_window(root)
)
btn_admin.pack(pady=7, ipady=5)
add_hover_effect(btn_admin, "#333333", "#555555", "#ffffff", "#FFD700")

# Launch Main Tkinter Application Loop
if __name__ == "__main__":
    root.mainloop()