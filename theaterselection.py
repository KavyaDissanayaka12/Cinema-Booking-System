import sys
import os
import time
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Dynamic directory configuration
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

for path in (script_dir, project_root):
    if path not in sys.path:
        sys.path.append(path)

# Safe imports
cursor = None
try:
    from Scripts.database import cursor
except ImportError:
    try:
        from database import cursor
    except ImportError as e:
        print(f"Database import error in theaterselection: {e}")

try:
    from Scripts.seatselection import select_seats
except ImportError:
    try:
        from seatselection import select_seats
    except ImportError as e:
        print(f"Error loading seatselection: {e}")

        # Corrected fallback signature matching actual call
        def select_seats(parent, c_id, m_id, t_id, s_time):
            print(f"Navigating to seats for Cust: {c_id}, Movie: {m_id}, Theater: {t_id}, Showtime: {s_time}")


def select_theater(parent, customer_id, movie_id):
    # ------------------ Create Window ------------------
    window = Toplevel(parent)
    window.title("Select Theater & Showtime - AA Cinema")
    window.configure(bg="#0f0f0f")

    # Image garbage collection list
    image_refs = []
    window.image_refs = image_refs

    # Screen resolution detection & Fullscreen mode
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

    # Bind 'Esc' key to destroy or return
    window.bind("<Escape>", lambda e: window.destroy())

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

    # ------------------ Fullscreen Background Image ------------------
    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG"])
    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)

            # Darken to 30% brightness so the card content stands out
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=window)

            image_refs.append(bg_photo)

            bg_label = Label(window, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in theater selection: {e}")

    # ------------------ Top Date & Time Header Bar ------------------
    header_top_bar = Frame(window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar,
        text="🍿 AA CINEMA - THEATER SELECTION",
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
        """Live updater for clock and current date on top header."""
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if window.winfo_exists():
            window.after(1000, update_datetime)

    update_datetime()

    # ------------------ Locate Icons & Images ------------------
    # 1. Title Logo
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])

    card_logo_img = None
    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)
            window_logo = ImageTk.PhotoImage(logo_raw, master=window)
            window.iconphoto(False, window_logo)
            image_refs.append(window_logo)

            logo_resized = logo_raw.resize((50, 50), Image.LANCZOS)
            card_logo_img = ImageTk.PhotoImage(logo_resized, master=window)
            image_refs.append(card_logo_img)
        except Exception as e:
            print(f"Could not load icon in theater selection: {e}")

    # 2. Robust Search for theater2 Image
    theater_img_path = find_file(["theater2.JPEG", "theater2.jpeg", "theater2.jpg", "theater2.png"])

    banner_tk_img = None
    if theater_img_path and os.path.exists(theater_img_path):
        try:
            th_raw = Image.open(theater_img_path)
            th_resized = th_raw.resize((420, 150), Image.LANCZOS)
            banner_tk_img = ImageTk.PhotoImage(th_resized, master=window)
            image_refs.append(banner_tk_img)
        except Exception as e:
            print(f"Could not load theater2 image from '{theater_img_path}': {e}")

    # ------------------ Centered Main Card Layout ------------------
    center_frame = Frame(window, bg="")
    center_frame.place(relx=0.5, rely=0.52, anchor="center")

    card = Frame(
        center_frame,
        bg="#1c1c1c",
        bd=1,
        relief="solid",
        highlightbackground="#D4AF37",
        highlightthickness=1,
        padx=40,
        pady=25
    )
    card.pack()

    # Header section
    if card_logo_img:
        logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
        logo_lbl.image = card_logo_img
        logo_lbl.pack(pady=(0, 5))

    Label(
        card,
        text="SHOWTIME & LOCATION",
        font=("Segoe UI", 9, "bold"),
        fg="#FFD700",
        bg="#1c1c1c"
    ).pack(pady=(0, 2))

    Label(
        card,
        text="Select Theater & Showtime",
        font=("Segoe UI", 18, "bold"),
        fg="white",
        bg="#1c1c1c"
    ).pack(pady=(0, 10))

    # ------------------ Creative Theater Image Display ------------------
    if banner_tk_img:
        banner_frame = Frame(
            card,
            bg="#FFD700",
            bd=1,
            relief="solid"
        )
        banner_frame.pack(pady=(0, 15))

        banner_lbl = Label(
            banner_frame,
            image=banner_tk_img,
            bg="#1c1c1c"
        )
        banner_lbl.image = banner_tk_img
        banner_lbl.pack()

        overlay_badge = Label(
            banner_lbl,
            text=" 🎬 PREVIEW YOUR EXPERIENCE ",
            font=("Segoe UI", 8, "bold"),
            fg="#121212",
            bg="#FFD700"
        )
        overlay_badge.place(relx=0.03, rely=0.78)

    # ------------------ TTK Combobox Custom Styling ------------------
    style = ttk.Style()
    style.theme_use('default')

    style.configure(
        "DarkText.TCombobox",
        fieldbackground="#e0e0e0",
        background="#333333",
        foreground="#1c1c1c",  # Dark text color for dropdown selection
        darkcolor="#2b2b2b",
        lightcolor="#2b2b2b",
        selectbackground="#FFD700",
        selectforeground="#1c1c1c",
        arrowcolor="white",
        padding=6
    )

    # Configure dropdown pop-up listbox colors
    window.option_add("*TCombobox*Listbox.font", ("Segoe UI", 10, "bold"))
    window.option_add("*TCombobox*Listbox.background", "#e0e0e0")
    window.option_add("*TCombobox*Listbox.foreground", "#1c1c1c")
    window.option_add("*TCombobox*Listbox.selectBackground", "#FFD700")
    window.option_add("*TCombobox*Listbox.selectForeground", "#1c1c1c")

    # ------------------ Dropdowns ------------------
    fields_frame = Frame(card, bg="#1c1c1c")
    fields_frame.pack(fill="x", pady=0)

    # Theater Dropdown Label
    Label(
        fields_frame,
        text="THEATER & LOCATION",
        font=("Segoe UI", 9, "bold"),
        fg="#dddddd",
        bg="#1c1c1c",
        anchor="w"
    ).pack(fill="x", pady=(2, 2))

    theater_combo = ttk.Combobox(
        fields_frame,
        style="DarkText.TCombobox",
        state="readonly",
        font=("Segoe UI", 10, "bold"),
        width=36
    )
    theater_combo.pack(fill="x", pady=(0, 10))

    # Showtime Dropdown Label
    Label(
        fields_frame,
        text="AVAILABLE SHOWTIME",
        font=("Segoe UI", 9, "bold"),
        fg="#dddddd",
        bg="#1c1c1c",
        anchor="w"
    ).pack(fill="x", pady=(2, 2))

    showtime_combo = ttk.Combobox(
        fields_frame,
        style="DarkText.TCombobox",
        state="readonly",
        font=("Segoe UI", 10, "bold"),
        width=36
    )
    showtime_combo.pack(fill="x", pady=(0, 18))

    theater_ids = {}

    # Query Available Theaters from DB
    theaters = []
    if cursor:
        queries = [
            ("SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN shows s ON t.theater_id = s.theater_id WHERE s.movie_id = %s ORDER BY t.theater_name", (movie_id,)),
            ("SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN shows s ON t.theater_id = s.theater_id WHERE s.movie_id = ? ORDER BY t.theater_name", (movie_id,)),
            ("SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN showtimes s ON t.theater_id = s.theater_id WHERE s.movie_id = %s ORDER BY t.theater_name", (movie_id,)),
            ("SELECT DISTINCT t.theater_id, t.theater_name, t.location FROM theaters t JOIN showtimes s ON t.theater_id = s.theater_id WHERE s.movie_id = ? ORDER BY t.theater_name", (movie_id,))
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
                ("SELECT show_date, show_time FROM shows WHERE movie_id = %s AND theater_id = %s ORDER BY show_date, show_time", (movie_id, theater_id)),
                ("SELECT show_date, show_time FROM shows WHERE movie_id = ? AND theater_id = ? ORDER BY show_date, show_time", (movie_id, theater_id)),
                ("SELECT show_date, show_time FROM showtimes WHERE movie_id = %s AND theater_id = %s ORDER BY show_date, show_time", (movie_id, theater_id)),
                ("SELECT show_date, show_time FROM showtimes WHERE movie_id = ? AND theater_id = ? ORDER BY show_date, show_time", (movie_id, theater_id))
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

        # Advance to Seat Selection
        select_seats(parent, customer_id, movie_id, theater_id, selected_showtime)

    # ------------------ Action Buttons ------------------
    button_frame = Frame(card, bg="#1c1c1c")
    button_frame.pack(fill="x", pady=(5, 0))

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
        command=window.destroy
    )
    btn_back.pack(side="left", ipady=6, padx=(0, 8))

    btn_next = Button(
        button_frame,
        text="Select Seats  ➜",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        font=("Segoe UI", 10, "bold"),
        width=20,
        cursor="hand2",
        bd=0,
        command=proceed_to_seats
    )
    btn_next.pack(side="right", ipady=6, padx=(8, 0))

    window.bind("<Return>", lambda e: proceed_to_seats())