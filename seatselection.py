import os
import sys
import time
from datetime import datetime
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk

# ------------------ Dynamic Directory & Search Path Setup ------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)

for path in (script_dir, project_root):
    if path not in sys.path:
        sys.path.append(path)

# ------------------ Safe Database Import ------------------
cursor = None
conn = None

try:
    from Scripts.database import conn, cursor
except ImportError:
    try:
        from database import conn, cursor
    except ImportError as e:
        print(f"Database import error in seatselection: {e}")

# Helper to determine SQL placeholder style (? for sqlite3, %s for mysql/pg)
def get_sql_param():
    if conn and type(conn).__module__.startswith("sqlite3"):
        return "?"
    return "%s"

# ------------------ Safe Payment Module Import ------------------
try:
    from Scripts.pay import show_payment_window
except ImportError:
    try:
        from pay import show_payment_window
    except ImportError:
        try:
            import pay
            show_payment_window = pay.show_payment_window
        except ImportError as e:
            print(f"Error loading pay module in seatselection: {e}")

            def show_payment_window(parent, customer_id, total_amount=0.0):
                messagebox.showerror(
                    "Module Error",
                    "Payment module ('pay.py') could not be loaded.\nMake sure pay.py is in your root directory or Scripts folder."
                )


def select_seats(parent, customer_id, movie_id, theater_id, showtime):
    param = get_sql_param()

    # Helper function to locate asset files across directory levels
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

    # ------------------ Create Fullscreen Window ------------------
    seat_window = Toplevel(parent)
    seat_window.title("Select Seats - AA Cinema")
    seat_window.configure(bg="#0f0f0f")

    # Image garbage collection tracking list
    image_refs = []
    seat_window.image_refs = image_refs

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    seat_window.geometry(f"{screen_w}x{screen_h}+0+0")
    try:
        seat_window.state('zoomed')
    except Exception:
        try:
            seat_window.attributes('-fullscreen', True)
        except Exception:
            pass

    seat_window.deiconify()
    seat_window.lift()
    seat_window.focus_force()

    seat_window.bind("<Escape>", lambda e: seat_window.destroy())

    # ------------------ Top Date & Time Header Bar ------------------
    header_top_bar = Frame(seat_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(seat_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar,
        text="🍿 AA CINEMA - SEAT SELECTION",
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
        if seat_window.winfo_exists():
            seat_window.after(1000, update_datetime)

    update_datetime()

    # ------------------ Locate Logo Path & Icons ------------------
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
    header_logo_img = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)

            # Titlebar Icon
            window_logo = ImageTk.PhotoImage(logo_raw, master=seat_window)
            seat_window.iconphoto(False, window_logo)
            image_refs.append(window_logo)

            # Header Logo
            logo_resized = logo_raw.resize((35, 35), Image.LANCZOS)
            header_logo_img = ImageTk.PhotoImage(logo_resized, master=seat_window)
            seat_window.header_logo_img = header_logo_img  # Prevent GC
            image_refs.append(header_logo_img)
        except Exception as e:
            print(f"Could not load logo icon in seat selection: {e}")

    # ------------------ Search & Load for theater1 Image ------------------
    theater1_path = find_file(["theater1.JPEG", "theater1.jpeg", "theater1.jpg", "theater1.png"])

    theater_banner_img = None
    if theater1_path and os.path.exists(theater1_path):
        try:
            raw_banner = Image.open(theater1_path)
            resized_banner = raw_banner.resize((340, 150), Image.LANCZOS)
            theater_banner_img = ImageTk.PhotoImage(resized_banner, master=seat_window)
            seat_window.theater_banner_img = theater_banner_img  # Persistent reference
            image_refs.append(theater_banner_img)
        except Exception as e:
            print(f"Error loading theater1 image: {e}")

    # ------------------ Hero Header Section ------------------
    hero_frame = Frame(seat_window, bg="#1a1a1a", bd=2, relief="groove")
    hero_frame.pack(fill="x", padx=20, pady=(12, 6))

    title_box = Frame(hero_frame, bg="#1a1a1a")
    title_box.pack(pady=(10, 4))

    if header_logo_img:
        hdr_logo_lbl = Label(title_box, image=header_logo_img, bg="#1a1a1a")
        hdr_logo_lbl.image = header_logo_img
        hdr_logo_lbl.pack(side="left", padx=(0, 10))

    Label(
        title_box,
        text="AUDITORIUM SEATING PLAN",
        font=("Segoe UI", 18, "bold"),
        fg="white",
        bg="#1a1a1a"
    ).pack(side="left")

    Label(
        title_box,
        text=" • CHOOSE YOUR SEATS",
        font=("Segoe UI", 18, "bold"),
        fg="#FFD700",
        bg="#1a1a1a"
    ).pack(side="left")

    # Banner Container
    if theater_banner_img:
        banner_container = Frame(
            hero_frame,
            bg="#FFD700",
            bd=1,
            relief="solid"
        )
        banner_container.pack(pady=(6, 10), anchor="center")

        banner_lbl = Label(
            banner_container,
            image=theater_banner_img,
            bg="#1a1a1a"
        )
        banner_lbl.image = theater_banner_img
        banner_lbl.pack()

        badge_tag = Label(
            banner_lbl,
            text=" 🍿 PREMIUM CINEMA HALL EXPERIENCE 🍿 ",
            font=("Segoe UI", 8, "bold"),
            fg="#121212",
            bg="#FFD700",
            bd=0
        )
        badge_tag.place(relx=0.03, rely=0.70)
    else:
        Label(
            hero_frame,
            text="Press 'ESC' key on your keyboard to exit seat selection.",
            font=("Segoe UI", 9, "italic"),
            fg="#aaaaaa",
            bg="#1a1a1a"
        ).pack(pady=(0, 8))

    # ------------------ Screen Banner Visual Indicator ------------------
    screen_box = Frame(seat_window, bg="#0f0f0f")
    screen_box.pack(fill="x", padx=100, pady=(2, 6))

    Frame(screen_box, bg="#FFD700", height=4).pack(fill="x", pady=(0, 2))

    Label(
        screen_box,
        text="🎬 ALL EYES THIS WAY • CINEMA SCREEN",
        font=("Segoe UI", 9, "bold"),
        fg="#888888",
        bg="#0f0f0f"
    ).pack()

    # ------------------ Scrollable Container ------------------
    canvas = Canvas(seat_window, bg="#0f0f0f", highlightthickness=0)
    scrollbar = Scrollbar(seat_window, orient="vertical", command=canvas.yview)

    grid_frame = Frame(canvas, bg="#0f0f0f")
    container_window = canvas.create_window((screen_w // 2, 0), window=grid_frame, anchor="n")

    grid_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

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

    # ------------------ Database Lookups ------------------
    all_seats = []
    if cursor:
        try:
            cursor.execute(f"""
                SELECT seat_id, seat_number
                FROM seats
                WHERE theater_id = {param}
                ORDER BY seat_id
            """, (theater_id,))
            all_seats = cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error querying seats: {e}")
            seat_window.destroy()
            return

    if not all_seats:
        messagebox.showinfo("No Seats", "No seating layout registered for this theater.")
        seat_window.destroy()
        return

    # Resolve show_id safely checking showtimes table first
    show_id = None
    if cursor:
        try:
            cursor.execute(f"""
                SELECT show_id 
                FROM showtimes 
                WHERE movie_id = {param} AND theater_id = {param}
                LIMIT 1
            """, (movie_id, theater_id))
            show_row = cursor.fetchone()
            if show_row:
                show_id = show_row[0]
        except Exception:
            try:
                cursor.execute(f"""
                    SELECT show_id 
                    FROM shows 
                    WHERE movie_id = {param} AND theater_id = {param}
                    LIMIT 1
                """, (movie_id, theater_id))
                show_row = cursor.fetchone()
                if show_row:
                    show_id = show_row[0]
            except Exception as e:
                print(f"Notice: Could not resolve show ID: {e}")

    # Fetch Pricing
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

    # Fetch Booked Seats
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
                cursor.execute(f"""
                    SELECT b.seat_id 
                    FROM bookings b
                    JOIN seats st ON b.seat_id = st.seat_id
                    WHERE st.theater_id = {param}
                """, (theater_id,))
                booked_seat_rows = cursor.fetchall()
                booked_seat_ids = {row[0] for row in booked_seat_rows}
        except Exception as e:
            print(f"Notice: Error fetching booked seats: {e}")

    # Classify seats
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
        summary_lbl.config(
            text=f"Selected: {count} Seat(s)   |   Total Amount: Rs. {total_amount:.2f}"
        )

    def toggle_seat(s_id, btn):
        if s_id in selected_seat_ids:
            selected_seat_ids.remove(s_id)
            btn.config(bg="#4CAF50", fg="white")
        else:
            selected_seat_ids.append(s_id)
            btn.config(bg="#FFD700", fg="black")

        update_summary_label()

    # ------------------ Render Grid Sections ------------------
    columns_per_row = 5

    def render_section(section_title, section_seats, start_row_num, badge_color):
        if not section_seats:
            return

        section_frame = Frame(grid_frame, bg="#1c1c1c", bd=1, relief="solid", highlightbackground="#333333",
                              highlightthickness=1)
        section_frame.pack(anchor="center", pady=10, padx=20)

        header_frame = Frame(section_frame, bg="#262626")
        header_frame.pack(fill="x")

        Label(
            header_frame,
            text=section_title,
            font=("Segoe UI", 10, "bold"),
            fg=badge_color,
            bg="#262626",
            padx=15,
            pady=5
        ).pack()

        grid_inner = Frame(section_frame, bg="#1c1c1c", padx=20, pady=12)
        grid_inner.pack()

        for idx, seat in enumerate(section_seats):
            s_id, s_num = seat[0], str(seat[1])

            r_idx = idx // columns_per_row
            c_idx = idx % columns_per_row

            if c_idx == 0:
                Label(
                    grid_inner,
                    text=f"Row {start_row_num + r_idx}",
                    font=("Segoe UI", 9, "bold"),
                    fg="#888888",
                    bg="#1c1c1c",
                    width=6
                ).grid(row=r_idx, column=0, padx=(0, 10), pady=5)

            if s_id in booked_seat_ids:
                btn = Button(
                    grid_inner,
                    text=s_num,
                    width=6,
                    height=2,
                    font=("Segoe UI", 10, "bold"),
                    bg="#E53935",
                    fg="white",
                    state="disabled",
                    bd=0
                )
            else:
                btn = Button(
                    grid_inner,
                    text=s_num,
                    width=6,
                    height=2,
                    font=("Segoe UI", 10, "bold"),
                    bg="#4CAF50",
                    fg="white",
                    cursor="hand2",
                    bd=0
                )
                btn.config(command=lambda sid=s_id, b=btn: toggle_seat(sid, b))

            btn.grid(row=r_idx, column=c_idx + 1, padx=6, pady=5)
            seat_buttons[s_id] = btn

    render_section(f"ODC SECTION  •  Rs. {odc_price:.2f} per seat", odc_seats, start_row_num=1, badge_color="#00E676")
    render_section(f"BALCONY SECTION  •  Rs. {balcony_price:.2f} per seat", balcony_seats, start_row_num=3,
                   badge_color="#FFD700")

    # ------------------ Bottom Control Panel ------------------
    bottom_panel = Frame(seat_window, bg="#1a1a1a", bd=1, relief="groove")
    bottom_panel.pack(side="bottom", fill="x", ipady=8)

    # Legend Display
    legend_frame = Frame(bottom_panel, bg="#1a1a1a")
    legend_frame.pack(pady=(4, 4))

    Label(legend_frame, text="■ Available", fg="#4CAF50", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left", padx=15)
    Label(legend_frame, text="■ Selected", fg="#FFD700", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left", padx=15)
    Label(legend_frame, text="■ Booked", fg="#E53935", bg="#1a1a1a", font=("Segoe UI", 10, "bold")).pack(side="left", padx=15)

    summary_lbl = Label(
        bottom_panel,
        text="Selected: 0 Seat(s)   |   Total Amount: Rs. 0.00",
        font=("Segoe UI", 11, "bold"),
        fg="white",
        bg="#2b2b2b",
        padx=16,
        pady=5,
        bd=1,
        relief="solid"
    )
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
                        cursor.execute(f"""
                            INSERT INTO bookings (customer_id, show_id, seat_id, booking_date)
                            VALUES ({param}, {param}, {param}, {param})
                        """, (customer_id, show_id, s_id, now_timestamp))
                    else:
                        cursor.execute(f"""
                            INSERT INTO bookings (customer_id, seat_id, booking_date)
                            VALUES ({param}, {param}, {param})
                        """, (customer_id, s_id, now_timestamp))

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

    # Action Buttons Container
    btn_container = Frame(bottom_panel, bg="#1a1a1a")
    btn_container.pack(pady=(2, 4))

    btn_back = Button(
        btn_container,
        text="Cancel",
        bg="#E53935",
        fg="white",
        activebackground="#d32f2f",
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        width=12,
        cursor="hand2",
        bd=0,
        command=seat_window.destroy
    )
    btn_back.pack(side="left", ipady=5, padx=(0, 10))

    btn_confirm = Button(
        btn_container,
        text="Proceed to Payment  💳",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        width=24,
        cursor="hand2",
        bd=0,
        command=confirm_booking
    )
    btn_confirm.pack(side="right", ipady=5, padx=(10, 0))