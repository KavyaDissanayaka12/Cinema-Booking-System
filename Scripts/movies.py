import os
import sys
import time

# Ensure local script & project root directories take precedence over site-packages
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

for path in (script_dir, project_root):
    if path in sys.path:
        sys.path.remove(path)
    sys.path.insert(0, path)

from tkinter import *
from PIL import Image, ImageTk

# Safe import for customer_window or select_theater from app_login
customer_window = None
select_theater = None

try:
    from Scripts.app_login import customer_window, select_theater
except ImportError:
    try:
        from app_login import customer_window, select_theater
    except ImportError as e:
        print(f"Login module import error: {e}")

# Fallback wrapper if customer_window isn't explicitly defined in app_login
if customer_window is None:
    def customer_window(parent, m_id, customer_id=1):
        """Wrapper bridging movie selection to theater selection."""
        if select_theater:
            select_theater(parent, customer_id, m_id)
        else:
            print(f"Opening booking window for Movie ID: {m_id}, Customer ID: {customer_id}")


def view_movies(root):
    # ------------------ Database Safe Import ------------------
    cursor = None
    try:
        from Scripts.database import cursor
    except ImportError:
        try:
            from database import cursor
        except ImportError as e:
            print(f"Database import error in movies: {e}")

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

    # ------------------ Create Toplevel Window ------------------
    movie_window = Toplevel(root)
    movie_window.title("Available Movies - AA Cinema")
    movie_window.configure(bg="#0f0f0f")

    # Image garbage collection list
    image_refs = []
    movie_window.image_refs = image_refs

    # Get monitor resolution directly from root window
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    # Force geometry to match screen resolution exactly
    movie_window.geometry(f"{screen_w}x{screen_h}+0+0")

    try:
        movie_window.state('zoomed')
    except Exception:
        pass

    # Bind 'Esc' key to return to normal size
    movie_window.bind("<Escape>", lambda e: movie_window.state('normal'))

    movie_window.deiconify()
    movie_window.lift()
    movie_window.focus_force()

    # ------------------ Fullscreen Background Image ------------------
    if bg_path and os.path.exists(bg_path):
        try:
            raw_bg = Image.open(bg_path)
            bg_scaled = raw_bg.resize((screen_w, screen_h), Image.LANCZOS)

            # Darken to 30% brightness so cards and text stand out clearly
            bg_darkened = Image.eval(bg_scaled, lambda p: int(p * 0.30))
            bg_photo = ImageTk.PhotoImage(bg_darkened, master=movie_window)
            image_refs.append(bg_photo)

            bg_label = Label(movie_window, image=bg_photo, bg="#0f0f0f")
            bg_label.image = bg_photo
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background image in movies: {e}")

    # ------------------ Locate Logo Path & App Icon ------------------
    window_logo_img = None
    fallback_logo_img = None
    header_logo_img = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)

            # Window Titlebar Icon
            window_logo_img = ImageTk.PhotoImage(logo_raw, master=movie_window)
            movie_window.iconphoto(False, window_logo_img)
            image_refs.append(window_logo_img)

            # Resized Logo for Header
            header_logo_resized = logo_raw.resize((35, 35), Image.LANCZOS)
            header_logo_img = ImageTk.PhotoImage(header_logo_resized, master=movie_window)
            image_refs.append(header_logo_img)

            # Resized Logo for Poster Fallback
            fallback_logo_resized = logo_raw.resize((120, 120), Image.LANCZOS)
            fallback_logo_img = ImageTk.PhotoImage(fallback_logo_resized, master=movie_window)
            image_refs.append(fallback_logo_img)
        except Exception as e:
            print(f"Could not load cinema logo image in movies: {e}")

    # ------------------ Top Date & Time Header Bar ------------------
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
        if movie_window.winfo_exists():
            movie_window.after(1000, update_datetime)

    update_datetime()

    # ------------------ Hero Header ------------------
    hero_frame = Frame(movie_window, bg="#1a1a1a", bd=1, relief="solid", highlightbackground="#D4AF37",
                       highlightthickness=1)
    hero_frame.pack(fill="x", padx=20, pady=(10, 10))

    Label(
        hero_frame,
        text="✦ NOW SHOWING ✦",
        font=("Segoe UI", 10, "bold"),
        fg="#FFD700",
        bg="#1a1a1a"
    ).pack(pady=(12, 2))

    # Header Title Box (Logo + Text)
    title_box = Frame(hero_frame, bg="#1a1a1a")
    title_box.pack(pady=(0, 2))

    if header_logo_img:
        hdr_logo_lbl = Label(title_box, image=header_logo_img, bg="#1a1a1a")
        hdr_logo_lbl.image = header_logo_img
        hdr_logo_lbl.pack(side="left", padx=(0, 10))

    Label(
        title_box,
        text="AVAILABLE MOVIES AT AA CINEMA",
        font=("Segoe UI", 22, "bold"),
        fg="white",
        bg="#1a1a1a"
    ).pack(side="left")
    Label(
        hero_frame,
        text="Press 'ESC' key on your keyboard to exit full screen mode.",
        font=("Segoe UI", 9, "italic"),
        fg="#aaaaaa",
        bg="#1a1a1a"
    ).pack(pady=(0, 10))

    # ------------------ Scrollable Frame Setup ------------------
    canvas = Canvas(movie_window, bg="#0f0f0f", highlightthickness=0)
    scrollbar = Scrollbar(movie_window, orient="vertical", command=canvas.yview)

    container = Frame(canvas, bg="#0f0f0f")
    container_window = canvas.create_window((screen_w // 2, 0), window=container, anchor="n")

    container.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", pady=10)

    # Mousewheel Scrolling
    def _on_mousewheel(event):
        try:
            if canvas.winfo_exists():
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except Exception:
            pass

    container.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    container.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    # ------------------ Locate Posters Directory ------------------
    cwd_posters = os.path.abspath("posters")
    root_posters = os.path.join(project_root, "posters")

    if os.path.exists(cwd_posters):
        posters_dir = cwd_posters
    elif os.path.exists(root_posters):
        posters_dir = root_posters
    else:
        posters_dir = cwd_posters

    # ------------------ Database Lookup ------------------
    movies = []
    if cursor:
        try:
            cursor.execute("""
                SELECT movie_id, title, genre, duration, language, release_date, poster
                FROM movies
            """)
            movies = cursor.fetchall()
        except Exception as db_err:
            print(f"Database query error in movies: {db_err}")

    # ------------------ Display Cards Grid ------------------
    columns = max(3, screen_w // 250)

    for index, movie in enumerate(movies):
        movie_id, title, genre, duration, language, release, poster_filename = movie

        card = Frame(
            container,
            bg="#1c1c1c",
            bd=1,
            relief="solid",
            highlightbackground="#333333",
            highlightthickness=1
        )

        row = index // columns
        col = index % columns

        card.grid(row=row, column=col, padx=14, pady=16, sticky="n")

        # Poster Container Frame
        poster_frame = Frame(card, bg="#0d0d0d", bd=1, relief="solid", width=175, height=250)
        poster_frame.pack_propagate(False)
        poster_frame.pack(padx=10, pady=(10, 6))

        poster_loaded = False
        if poster_filename:
            clean_filename = str(poster_filename).strip().strip("'\"")
            poster_path = os.path.join(posters_dir, clean_filename)

            if os.path.exists(poster_path):
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

        # Fallback UI displaying Cinema Logo Icon when poster is missing
        if not poster_loaded:
            fallback_box = Frame(poster_frame, bg="#181818")
            fallback_box.pack(fill="both", expand=True)

            if fallback_logo_img:
                logo_lbl = Label(fallback_box, image=fallback_logo_img, bg="#181818")
                logo_lbl.image = fallback_logo_img
                logo_lbl.pack(expand=True, pady=(15, 0))

            Label(
                fallback_box,
                text="AA CINEMA",
                font=("Segoe UI", 9, "bold"),
                bg="#181818",
                fg="#888888"
            ).pack(pady=(0, 15))

        # Text Metadata Container
        info_frame = Frame(card, bg="#1c1c1c")
        info_frame.pack(fill="x", padx=10, pady=(0, 10))

        Label(
            info_frame,
            text=title,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#1c1c1c",
            wraplength=165,
            justify=CENTER
        ).pack(pady=(4, 4))

        Label(
            info_frame,
            text=f"🎭 {genre}",
            font=("Segoe UI", 8),
            fg="#cccccc",
            bg="#1c1c1c"
        ).pack(pady=(0, 2))

        Label(
            info_frame,
            text=f"⏱ {duration} • 🌐 {language}",
            font=("Segoe UI", 8),
            fg="#aaaaaa",
            bg="#1c1c1c"
        ).pack(pady=(0, 4))

        Label(
            info_frame,
            text=f"📅 {release}",
            font=("Segoe UI", 8),
            fg="#888888",
            bg="#1c1c1c"
        ).pack(pady=(0, 8))

        # Action Button
        btn_book = Button(
            info_frame,
            text="🎟 Book Ticket",
            bg="#FFD700",
            fg="black",
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
            bd=0,
            activebackground="#E6C200",
            activeforeground="black",
            command=lambda m_id=movie_id: customer_window(movie_window, m_id)
        )
        btn_book.pack(fill="x", ipady=3)

        # Hover effect on buttons
        def on_enter(e, b=btn_book):
            b.config(bg="#FFF066")

        def on_leave(e, b=btn_book):
            b.config(bg="#FFD700")

        btn_book.bind("<Enter>", on_enter)
        btn_book.bind("<Leave>", on_leave)

    # Retain image object references to prevent garbage collection
    movie_window.images = image_refs
    movie_window.header_logo_img = header_logo_img
    movie_window.fallback_logo_img = fallback_logo_img