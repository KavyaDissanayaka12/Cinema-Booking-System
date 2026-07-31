import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, Frame, Label, Entry, Button, Toplevel
from PIL import Image, ImageTk

# ------------------ Dynamic Search Path Setup ------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

for path in (script_dir, project_root):
    if path not in sys.path:
        sys.path.append(path)

# ------------------ Database Connection ------------------
conn = None
cursor = None
try:
    from Scripts.database import conn, cursor
except ImportError:
    try:
        from database import conn, cursor
    except ImportError as e:
        print(f"Database import error in admin.py: {e}")


def load_cinema_logo(size=(40, 40)):
    """Finds and resizes the cinema logo from potential project directories."""
    possible_paths = [
        os.path.join(script_dir, "logo_converted.png"),
        os.path.join(project_root, "logo_converted.png"),
        os.path.join(script_dir, "Assets", "logo_converted.png"),
        os.path.join(project_root, "Assets", "logo_converted.png"),
        os.path.join(script_dir, "logo.png"),
        os.path.join(project_root, "logo.png")
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                img = Image.open(path)
                resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
                img = img.resize(size, resample_filter)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading logo from {path}: {e}")
    return None


# ------------------ Admin Authentication & Login Window ------------------
def verify_admin_credentials(admin_id, password):
    """Validates entered credentials against the 'admin' database table."""
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
    """Displays the admin authentication dialog."""
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

    Label(form_frame, text="Admin ID:", font=("Segoe UI", 10, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w", pady=(0, 2))
    entry_id = Entry(form_frame, font=("Segoe UI", 11), bg="#2b2b2b", fg="white", insertbackground="white", bd=1, relief="solid")
    entry_id.pack(fill="x", pady=(0, 12))

    Label(form_frame, text="Password:", font=("Segoe UI", 10, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w", pady=(0, 2))
    entry_pass = Entry(form_frame, font=("Segoe UI", 11), show="•", bg="#2b2b2b", fg="white", insertbackground="white", bd=1, relief="solid")
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


# ------------------ Main Admin Panel ------------------
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
    admin_window.attributes('-topmost', True)
    admin_window.after_idle(admin_window.attributes, '-topmost', False)
    admin_window.focus_force()

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#1c1c1c", foreground="white", fieldbackground="#1c1c1c", rowheight=28)
    style.configure("Treeview.Heading", background="#2b2b2b", foreground="#FFD700", font=("Segoe UI", 9, "bold"))
    style.map("Treeview", background=[("selected", "#00E676")], foreground=[("selected", "#000000")])

    header_top_bar = Frame(admin_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(admin_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar, text="🍿 AA CINEMA - ADMIN SYSTEM",
        font=("Segoe UI", 9, "bold"), fg="#FFD700", bg="#121212", padx=20, pady=5
    )
    header_brand.pack(side="left")

    datetime_frame = Frame(header_top_bar, bg="#121212")
    datetime_frame.pack(side="right", padx=20, pady=4)

    lbl_date = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
    lbl_date.pack(side="left", padx=(0, 10))

    lbl_time = Label(datetime_frame, font=("Segoe UI", 9, "bold"), fg="#FFD700", bg="#121212")
    lbl_time.pack(side="left")

    def update_panel_datetime():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if admin_window.winfo_exists():
            admin_window.after(1000, update_panel_datetime)

    update_panel_datetime()

    header_frame = Frame(admin_window, bg="#1c1c1c", height=60, bd=1, relief="solid")
    header_frame.pack(side="top", fill="x")

    title_container = Frame(header_frame, bg="#1c1c1c")
    title_container.pack(side="left", padx=20, pady=10)

    logo_img = load_cinema_logo(size=(40, 40))
    if logo_img:
        admin_window.image_refs.append(logo_img)
        Label(title_container, image=logo_img, bg="#1c1c1c").pack(side="left", padx=(0, 12))

    Label(
        title_container, text="AA CINEMA - ADMIN CONTROL CENTER",
        font=("Segoe UI", 14, "bold"), fg="#FFD700", bg="#1c1c1c"
    ).pack(side="left")

    def handle_logout():
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to log out of the Admin Panel?", parent=admin_window):
            admin_window.destroy()

    Button(
        header_frame, text="🚪 Logout", bg="#E53935", fg="white", activebackground="#d32f2f",
        activeforeground="white", font=("Segoe UI", 9, "bold"), bd=0, padx=15, pady=5, cursor="hand2", command=handle_logout
    ).pack(side="right", padx=20)

    main_container = Frame(admin_window, bg="#0f0f0f")
    main_container.pack(fill="both", expand=True)

    sidebar = Frame(main_container, bg="#181818", width=230, bd=1, relief="solid")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    content_area = Frame(main_container, bg="#0f0f0f")
    content_area.pack(side="right", fill="both", expand=True, padx=15, pady=15)

    nav_buttons = {}

    def switch_view(view_name):
        for widget in content_area.winfo_children():
            widget.destroy()

        for name, btn in nav_buttons.items():
            if name == view_name:
                btn.config(bg="#FFD700", fg="#000000")
            else:
                btn.config(bg="#181818", fg="#cccccc")

        if view_name == "Dashboard":
            render_dashboard(content_area)
        elif view_name == "Movies":
            render_movies_view(content_area)
        elif view_name == "Showtimes":
            render_showtimes_view(content_area)
        elif view_name == "Theaters":
            render_theaters_view(content_area)
        elif view_name == "Seats":
            render_seats_view(content_area)
        elif view_name == "Customers":
            render_customers_view(content_area)
        elif view_name == "Bookings":
            render_bookings_view(content_area)
        elif view_name == "Payments":
            render_payments_view(content_area)
        elif view_name == "Reports":
            render_reports_view(content_area)
        elif view_name == "Settings":
            render_settings_view(content_area)

    menu_items = [
        ("🏠 Dashboard", "Dashboard"),
        ("🎬 Manage Movies", "Movies"),
        ("📅 Manage Showtimes", "Showtimes"),
        ("🏢 Manage Theaters", "Theaters"),
        ("💺 Manage Seats", "Seats"),
        ("👤 Manage Customers", "Customers"),
        ("🎟️ Manage Bookings", "Bookings"),
        ("💳 Manage Payments", "Payments"),
        ("📊 Reports", "Reports"),
        ("⚙️ Settings", "Settings"),
        ("🚪 Logout", "Logout")
    ]

    Label(sidebar, text="NAVIGATION", font=("Segoe UI", 9, "bold"), fg="#666666", bg="#181818").pack(anchor="w", padx=15, pady=(15, 10))

    for label, view_key in menu_items:
        if view_key == "Logout":
            btn = Button(
                sidebar, text=label, font=("Segoe UI", 10, "bold"), bg="#181818", fg="#E53935",
                activebackground="#E53935", activeforeground="white", bd=0, anchor="w", padx=15, pady=8, cursor="hand2", command=handle_logout
            )
            btn.pack(fill="x", pady=2)
        else:
            btn = Button(
                sidebar, text=label, font=("Segoe UI", 10, "bold"), bg="#181818", fg="#cccccc",
                activebackground="#FFD700", activeforeground="#000000", bd=0, anchor="w", padx=15, pady=8, cursor="hand2", command=lambda vk=view_key: switch_view(vk)
            )
            btn.pack(fill="x", pady=2)
            nav_buttons[view_key] = btn

    # Helper function for styled form fields
    def create_form_entry(parent, label_text):
        Frame(parent, bg="#1c1c1c", height=3).pack()
        Label(parent, text=label_text, font=("Segoe UI", 8, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w")
        e = Entry(parent, font=("Segoe UI", 9), bg="#2b2b2b", fg="white", insertbackground="white", bd=1, relief="solid")
        e.pack(fill="x", pady=(1, 4))
        return e

    # ------------------ Views Rendering Logic ------------------
    def render_dashboard(parent):
        Label(parent, text="🏠 System Dashboard Overview", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 15))
        stats = [("Total Bookings", "0", "#2196F3"), ("Total Revenue", "Rs. 0.00", "#00E676"),
                 ("Pending Payments", "0", "#FF9800"), ("Configured Seats", "0", "#9C27B0")]
        if cursor:
            try:
                cursor.execute("SELECT COUNT(*) FROM bookings")
                row1 = cursor.fetchone()
                total_b = row1[0] if row1 else 0

                cursor.execute("SELECT SUM(amount) FROM payments WHERE LOWER(payment_status) = 'completed'")
                row2 = cursor.fetchone()
                total_r = float(row2[0]) if row2 and row2[0] else 0.0

                cursor.execute("SELECT COUNT(*) FROM payments WHERE LOWER(payment_status) LIKE '%pending%'")
                row3 = cursor.fetchone()
                pending_p = row3[0] if row3 else 0

                cursor.execute("SELECT COUNT(*) FROM seats")
                row4 = cursor.fetchone()
                total_s = row4[0] if row4 else 0

                stats = [
                    ("Total Bookings", f"{total_b}", "#2196F3"),
                    ("Total Revenue", f"Rs. {total_r:,.2f}", "#00E676"),
                    ("Pending Payments", f"{pending_p}", "#FF9800"),
                    ("Configured Seats", f"{total_s}", "#9C27B0")
                ]
            except Exception as e:
                print(f"Dashboard query error: {e}")

        cards_frame = Frame(parent, bg="#0f0f0f")
        cards_frame.pack(fill="x", pady=10)
        for title, val, color in stats:
            card = Frame(cards_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground=color, highlightthickness=2)
            card.pack(side="left", expand=True, fill="both", padx=10, ipady=15)
            Label(card, text=title, font=("Segoe UI", 10, "bold"), fg="#aaaaaa", bg="#1c1c1c").pack(pady=(10, 5))
            Label(card, text=val, font=("Segoe UI", 18, "bold"), fg=color, bg="#1c1c1c").pack(pady=(0, 10))

    # 1. MOVIES VIEW (movie_id, title, genre, duration, language, release_date, poster)
    def render_movies_view(parent):
        Label(parent, text="🎬 Manage Movies", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=10, bd=1, relief="solid", width=300)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Add New Movie", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 2))
        e_title = create_form_entry(form_frame, "Title:")
        e_genre = create_form_entry(form_frame, "Genre:")
        e_dur = create_form_entry(form_frame, "Duration (mins):")
        e_lang = create_form_entry(form_frame, "Language:")
        e_rdate = create_form_entry(form_frame, "Release Date (YYYY-MM-DD):")
        e_poster = create_form_entry(form_frame, "Poster URL/Path:")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("ID", "Title", "Genre", "Duration", "Language", "Release Date", "Poster")
        m_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            m_tree.heading(col, text=col)
            m_tree.column(col, anchor="center", width=90)
        m_tree.pack(fill="both", expand=True)

        def refresh():
            for row in m_tree.get_children():
                m_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT movie_id, title, genre, duration, language, release_date, poster FROM movies")
                    for row in cursor.fetchall():
                        m_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch movies: {e}", parent=admin_window)

        def add_movie():
            t, g, d, l, rd, p = (e_title.get().strip(), e_genre.get().strip(), e_dur.get().strip(),
                                e_lang.get().strip(), e_rdate.get().strip(), e_poster.get().strip())
            if not t or not d:
                messagebox.showwarning("Warning", "Title and Duration are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO movies (title, genre, duration, language, release_date, poster) VALUES (%s, %s, %s, %s, %s, %s)",
                                   (t, g, d, l, rd if rd else None, p))
                    conn.commit()
                    messagebox.showinfo("Success", "Movie added successfully!", parent=admin_window)
                    for e in (e_title, e_genre, e_dur, e_lang, e_rdate, e_poster): e.delete(0, tk.END)
                    refresh()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to add movie: {e}", parent=admin_window)

        def delete_movie():
            sel = m_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a movie to delete.", parent=admin_window)
                return
            mid = m_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Movie ID #{mid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM movies WHERE movie_id = %s", (mid,))
                        conn.commit()
                        refresh()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete movie: {e}", parent=admin_window)

        Button(form_frame, text="➕ Add Movie", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_movie).pack(fill="x", pady=(10, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_movie).pack(fill="x")
        refresh()

    # 2. SHOWTIMES VIEW (show_id, movie_id, theater_id, show_date, show_time)
    def render_showtimes_view(parent):
        Label(parent, text="📅 Manage Showtimes", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=15, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Add Showtime", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 5))
        e_m_id = create_form_entry(form_frame, "Movie ID:")
        e_t_id = create_form_entry(form_frame, "Theater ID:")
        e_s_date = create_form_entry(form_frame, "Show Date (YYYY-MM-DD):")
        e_s_time = create_form_entry(form_frame, "Show Time (HH:MM:SS):")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Show ID", "Movie ID", "Theater ID", "Show Date", "Show Time")
        st_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            st_tree.heading(col, text=col)
            st_tree.column(col, anchor="center", width=120)
        st_tree.pack(fill="both", expand=True)

        def refresh():
            for row in st_tree.get_children():
                st_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT show_id, movie_id, theater_id, show_date, show_time FROM showtimes")
                    for row in cursor.fetchall():
                        st_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch showtimes: {e}", parent=admin_window)

        def add_showtime():
            m, t, sd, st = e_m_id.get().strip(), e_t_id.get().strip(), e_s_date.get().strip(), e_s_time.get().strip()
            if not m or not t or not sd or not st:
                messagebox.showwarning("Warning", "All fields are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO showtimes (movie_id, theater_id, show_date, show_time) VALUES (%s, %s, %s, %s)", (m, t, sd, st))
                    conn.commit()
                    messagebox.showinfo("Success", "Showtime added successfully!", parent=admin_window)
                    for e in (e_m_id, e_t_id, e_s_date, e_s_time): e.delete(0, tk.END)
                    refresh()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to add showtime: {e}", parent=admin_window)

        def delete_showtime():
            sel = st_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a showtime to delete.", parent=admin_window)
                return
            sid = st_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Showtime ID #{sid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM showtimes WHERE show_id = %s", (sid,))
                        conn.commit()
                        refresh()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete showtime: {e}", parent=admin_window)

        Button(form_frame, text="➕ Add Showtime", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_showtime).pack(fill="x", pady=(15, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_showtime).pack(fill="x")
        refresh()

    # 3. THEATERS VIEW (theater_id, theater_name, location)
    def render_theaters_view(parent):
        Label(parent, text="🏢 Manage Theaters", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=15, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Add Theater", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 5))
        e_name = create_form_entry(form_frame, "Theater Name:")
        e_loc = create_form_entry(form_frame, "Location:")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Theater ID", "Theater Name", "Location")
        th_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            th_tree.heading(col, text=col)
            th_tree.column(col, anchor="center", width=160)
        th_tree.pack(fill="both", expand=True)

        def refresh():
            for row in th_tree.get_children():
                th_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT theater_id, theater_name, location FROM theaters")
                    for row in cursor.fetchall():
                        th_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch theaters: {e}", parent=admin_window)

        def add_theater():
            n, l = e_name.get().strip(), e_loc.get().strip()
            if not n:
                messagebox.showwarning("Warning", "Theater Name is required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO theaters (theater_name, location) VALUES (%s, %s)", (n, l))
                    conn.commit()
                    messagebox.showinfo("Success", "Theater added successfully!", parent=admin_window)
                    for e in (e_name, e_loc): e.delete(0, tk.END)
                    refresh()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to add theater: {e}", parent=admin_window)

        def delete_theater():
            sel = th_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a theater to delete.", parent=admin_window)
                return
            tid = th_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Theater ID #{tid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM theaters WHERE theater_id = %s", (tid,))
                        conn.commit()
                        refresh()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete theater: {e}", parent=admin_window)

        Button(form_frame, text="➕ Add Theater", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_theater).pack(fill="x", pady=(15, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_theater).pack(fill="x")
        refresh()

    # 4. SEATS VIEW (seat_id, theater_id, seat_number, seat_type)
    def render_seats_view(parent):
        Label(parent, text="💺 Manage Seats", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=15, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Configure Seat", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 5))
        e_th_id = create_form_entry(form_frame, "Theater ID:")
        e_s_num = create_form_entry(form_frame, "Seat Number (e.g. A1, B5):")
        e_s_type = create_form_entry(form_frame, "Seat Type (VIP/Regular):")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Seat ID", "Theater ID", "Seat Number", "Seat Type")
        seat_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            seat_tree.heading(col, text=col)
            seat_tree.column(col, anchor="center", width=130)
        seat_tree.pack(fill="both", expand=True)

        def refresh():
            for row in seat_tree.get_children():
                seat_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT seat_id, theater_id, seat_number, seat_type FROM seats")
                    for row in cursor.fetchall():
                        seat_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch seats: {e}", parent=admin_window)

        def add_seat():
            t, n, st = e_th_id.get().strip(), e_s_num.get().strip(), e_s_type.get().strip()
            if not t or not n:
                messagebox.showwarning("Warning", "Theater ID and Seat Number are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO seats (theater_id, seat_number, seat_type) VALUES (%s, %s, %s)", (t, n, st))
                    conn.commit()
                    messagebox.showinfo("Success", "Seat added successfully!", parent=admin_window)
                    for e in (e_th_id, e_s_num, e_s_type): e.delete(0, tk.END)
                    refresh()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to add seat: {e}", parent=admin_window)

        def delete_seat():
            sel = seat_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a seat to delete.", parent=admin_window)
                return
            sid = seat_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Seat ID #{sid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM seats WHERE seat_id = %s", (sid,))
                        conn.commit()
                        refresh()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete seat: {e}", parent=admin_window)

        Button(form_frame, text="➕ Add Seat", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_seat).pack(fill="x", pady=(15, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_seat).pack(fill="x")
        refresh()

    # 5. CUSTOMERS VIEW
    def render_customers_view(parent):
        Label(parent, text="👤 Registered Customers", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=15, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Add Customer", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 5))
        e_c_name = create_form_entry(form_frame, "Full Name:")
        e_c_email = create_form_entry(form_frame, "Email Address:")
        e_c_phone = create_form_entry(form_frame, "Phone Number:")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Customer ID", "Full Name", "Email", "Phone Number")
        cust_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            cust_tree.heading(col, text=col)
            cust_tree.column(col, anchor="center", width=140)
        cust_tree.pack(fill="both", expand=True)

        def refresh():
            for row in cust_tree.get_children():
                cust_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT customer_id, name, email, phone FROM customers")
                    for row in cursor.fetchall():
                        cust_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch customers: {e}", parent=admin_window)

        def add_customer():
            n, e, p = e_c_name.get().strip(), e_c_email.get().strip(), e_c_phone.get().strip()
            if not n or not e:
                messagebox.showwarning("Warning", "Customer Name and Email are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO customers (name, email, phone) VALUES (%s, %s, %s)", (n, e, p))
                    conn.commit()
                    messagebox.showinfo("Success", "Customer registered successfully!", parent=admin_window)
                    for entry in (e_c_name, e_c_email, e_c_phone): entry.delete(0, tk.END)
                    refresh()
                except Exception as err:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to register customer: {err}", parent=admin_window)

        def delete_customer():
            sel = cust_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a customer to delete.", parent=admin_window)
                return
            cid = cust_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Customer ID #{cid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM customers WHERE customer_id = %s", (cid,))
                        conn.commit()
                        refresh()
                    except Exception as err:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete customer: {err}", parent=admin_window)

        Button(form_frame, text="➕ Add Customer", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_customer).pack(fill="x", pady=(15, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_customer).pack(fill="x")
        refresh()

    # 6. BOOKINGS VIEW (booking_id, customer_id, show_id, seat_id, booking_date)
    def render_bookings_view(parent):
        Label(parent, text="🎟️ Manage Bookings", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=15, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="Create Booking", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 5))
        e_b_cust = create_form_entry(form_frame, "Customer ID:")
        e_b_show = create_form_entry(form_frame, "Show ID:")
        e_b_seat = create_form_entry(form_frame, "Seat ID:")
        e_b_date = create_form_entry(form_frame, "Booking Date (YYYY-MM-DD):")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Booking ID", "Customer ID", "Show ID", "Seat ID", "Booking Date")
        b_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            b_tree.heading(col, text=col)
            b_tree.column(col, anchor="center", width=110)
        b_tree.pack(fill="both", expand=True)

        def refresh():
            for row in b_tree.get_children():
                b_tree.delete(row)
            if cursor:
                try:
                    cursor.execute("SELECT booking_id, customer_id, show_id, seat_id, booking_date FROM bookings ORDER BY booking_date DESC")
                    for row in cursor.fetchall():
                        b_tree.insert("", "end", values=row)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch bookings: {e}", parent=admin_window)

        def add_booking():
            c, s, st, d = e_b_cust.get().strip(), e_b_show.get().strip(), e_b_seat.get().strip(), e_b_date.get().strip()
            if not c or not s or not st or not d:
                messagebox.showwarning("Warning", "All fields are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    cursor.execute("INSERT INTO bookings (customer_id, show_id, seat_id, booking_date) VALUES (%s, %s, %s, %s)", (c, s, st, d))
                    conn.commit()
                    messagebox.showinfo("Success", "Booking created successfully!", parent=admin_window)
                    for entry in (e_b_cust, e_b_show, e_b_seat, e_b_date): entry.delete(0, tk.END)
                    refresh()
                except Exception as err:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to create booking: {err}", parent=admin_window)

        def delete_booking():
            sel = b_tree.selection()
            if not sel:
                messagebox.showwarning("Warning", "Select a booking to delete.", parent=admin_window)
                return
            bid = b_tree.item(sel[0], 'values')[0]
            if messagebox.askyesno("Confirm Delete", f"Delete Booking ID #{bid}?", parent=admin_window):
                if cursor and conn:
                    try:
                        cursor.execute("DELETE FROM bookings WHERE booking_id = %s", (bid,))
                        conn.commit()
                        refresh()
                    except Exception as err:
                        conn.rollback()
                        messagebox.showerror("Error", f"Failed to delete booking: {err}", parent=admin_window)

        Button(form_frame, text="➕ Add Booking", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=add_booking).pack(fill="x", pady=(15, 5))
        Button(form_frame, text="🗑️ Delete Selected", bg="#E53935", fg="white", font=("Segoe UI", 9, "bold"), bd=0, pady=6, cursor="hand2", command=delete_booking).pack(fill="x")
        refresh()

    # 7. PAYMENTS VIEW (payment_id, booking_id, customer_id, amount, payment_date, payment_method, payment_status)
    def render_payments_view(parent):
        Label(parent, text="💳 Manage Payments & Transactions", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 10))

        body = Frame(parent, bg="#0f0f0f")
        body.pack(fill="both", expand=True)

        form_frame = Frame(body, bg="#1c1c1c", padx=15, pady=10, bd=1, relief="solid", width=280)
        form_frame.pack(side="left", fill="y", padx=(0, 15))
        form_frame.pack_propagate(False)

        Label(form_frame, text="New Transaction", font=("Segoe UI", 11, "bold"), fg="#FFD700", bg="#1c1c1c").pack(anchor="w", pady=(0, 2))
        e_p_book = create_form_entry(form_frame, "Booking ID:")
        e_p_cust = create_form_entry(form_frame, "Customer ID:")
        e_p_amt = create_form_entry(form_frame, "Amount (Rs.):")
        e_p_date = create_form_entry(form_frame, "Payment Date (YYYY-MM-DD):")
        e_p_meth = create_form_entry(form_frame, "Method (Card/Cash/Online):")
        e_p_stat = create_form_entry(form_frame, "Status (Completed/Pending):")

        table_frame = Frame(body, bg="#0f0f0f")
        table_frame.pack(side="right", fill="both", expand=True)

        cols = ("Payment ID", "Booking ID", "Customer ID", "Amount", "Payment Date", "Method", "Status")
        p_tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for col in cols:
            p_tree.heading(col, text=col)
            p_tree.column(col, anchor="center", width=105)
        p_tree.pack(fill="both", expand=True)

        def refresh_p():
            for item in p_tree.get_children():
                p_tree.delete(item)
            if cursor:
                try:
                    cursor.execute("SELECT payment_id, booking_id, customer_id, amount, payment_date, payment_method, payment_status FROM payments ORDER BY payment_date DESC")
                    for row in cursor.fetchall():
                        formatted = list(row)
                        if formatted[3] is not None:
                            formatted[3] = f"Rs. {float(formatted[3]):.2f}"
                        p_tree.insert("", "end", values=formatted)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to fetch payments: {e}", parent=admin_window)

        def add_payment():
            b, c, a, pd, m, s = (e_p_book.get().strip(), e_p_cust.get().strip(), e_p_amt.get().strip(),
                                e_p_date.get().strip(), e_p_meth.get().strip(), e_p_stat.get().strip())
            if not b or not c or not a:
                messagebox.showwarning("Warning", "Booking ID, Customer ID, and Amount are required.", parent=admin_window)
                return
            if cursor and conn:
                try:
                    query = "INSERT INTO payments (booking_id, customer_id, amount, payment_date, payment_method, payment_status) VALUES (%s, %s, %s, %s, %s, %s)"
                    cursor.execute(query, (b, c, a, pd if pd else time.strftime('%Y-%m-%d'), m if m else "Cash", s if s else "Completed"))
                    conn.commit()
                    messagebox.showinfo("Success", "Payment recorded successfully!", parent=admin_window)
                    for entry in (e_p_book, e_p_cust, e_p_amt, e_p_date, e_p_meth, e_p_stat): entry.delete(0, tk.END)
                    refresh_p()
                except Exception as err:
                    conn.rollback()
                    messagebox.showerror("Error", f"Failed to add payment: {err}", parent=admin_window)

        def mark_paid():
            selected = p_tree.selection()
            if not selected:
                messagebox.showwarning("Select Row", "Please select a payment record to update.", parent=admin_window)
                return
            pid = p_tree.item(selected[0], 'values')[0]
            if cursor and conn:
                try:
                    cursor.execute("UPDATE payments SET payment_status = 'Completed' WHERE payment_id = %s", (pid,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Payment #{pid} completed!", parent=admin_window)
                    refresh_p()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Error", f"Update failed: {e}", parent=admin_window)

        Button(form_frame, text="➕ Record Payment", bg="#00E676", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=5, cursor="hand2", command=add_payment).pack(fill="x", pady=(10, 4))
        Button(form_frame, text="✅ Mark as Completed", bg="#FFD700", fg="black", font=("Segoe UI", 9, "bold"), bd=0, pady=5, cursor="hand2", command=mark_paid).pack(fill="x")
        refresh_p()

    def render_reports_view(parent):
        Label(parent, text="📊 Analytics & Sales Reports", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 15))
        rep_card = Frame(parent, bg="#1c1c1c", padx=20, pady=20, bd=1, relief="solid")
        rep_card.pack(fill="x", pady=10)
        Label(rep_card, text="📈 Revenue Summary", font=("Segoe UI", 12, "bold"), fg="#00E676", bg="#1c1c1c").pack(anchor="w", pady=(0, 10))
        Label(rep_card, text="• Financial breakdowns (Daily, Weekly, Monthly) are computed directly from completed payments.", font=("Segoe UI", 10), fg="#cccccc", bg="#1c1c1c").pack(anchor="w", pady=2)

    def render_settings_view(parent):
        Label(parent, text="⚙️ Admin & System Settings", font=("Segoe UI", 16, "bold"), fg="#FFD700", bg="#0f0f0f").pack(anchor="w", pady=(0, 15))
        sett_card = Frame(parent, bg="#1c1c1c", padx=20, pady=20, bd=1, relief="solid")
        sett_card.pack(fill="x", pady=10)
        Label(sett_card, text="Database Status", font=("Segoe UI", 12, "bold"), fg="white", bg="#1c1c1c").pack(anchor="w", pady=(0, 10))
        status_text = "🟢 Connected to MySQL Database" if conn else "🔴 Database Disconnected"
        status_color = "#00E676" if conn else "#E53935"
        Label(sett_card, text=status_text, font=("Segoe UI", 11, "bold"), fg=status_color, bg="#1c1c1c").pack(anchor="w")

    switch_view("Dashboard")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    show_login_window(root)
    root.mainloop()