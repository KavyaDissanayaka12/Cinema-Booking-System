import os
import sys
import importlib
import time
import tkinter as tk
from tkinter import Button, Label, Frame, messagebox
from PIL import Image, ImageTk

# ------------------ Set Search Paths BEFORE Imports ------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "Scripts")

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
if os.path.exists(SCRIPTS_DIR) and SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

image_refs = []


def find_file(filenames):
    for name in filenames:
        p1 = os.path.join(BASE_DIR, name)
        p2 = os.path.join(SCRIPTS_DIR, name)
        if os.path.exists(p1):
            return p1
        elif os.path.exists(p2):
            return p2
    return None


RESAMPLE_FILTER = getattr(Image, 'Resampling', Image).LANCZOS

LOGO_PATH = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
BACKGROUND_IMAGE_PATH = find_file(
    ["background.JPEG", "background.jpeg", "background.jpg", "background.png", "bg.JPEG", "bg.jpg"]
)


# ------------------ Safe Dynamic Admin Import ------------------
def launch_admin_login(parent_win):
    try:
        if 'admin' in sys.modules:
            admin_mod = importlib.reload(sys.modules['admin'])
        else:
            try:
                from Scripts import admin as admin_mod
            except ImportError:
                import admin as admin_mod

        admin_mod.show_login_window(parent_win)
    except Exception as err:
        messagebox.showerror("Error", f"Failed to launch Admin Login: {err}")


# ------------------ Safe Module Imports ------------------
try:
    from Scripts import movies

    view_movies = movies.view_movies
except ImportError:
    try:
        import movies

        view_movies = movies.view_movies
    except ImportError:
        def view_movies(parent):
            messagebox.showerror("Module Error", "Movies view module could not be loaded.")

try:
    from Scripts import upcomingmovies

    upcoming_mod = upcomingmovies
except ImportError:
    try:
        import upcomingmovies

        upcoming_mod = upcomingmovies
    except ImportError:
        upcoming_mod = None


def open_upcoming_movies(parent_window):
    global upcoming_mod
    if upcoming_mod is not None:
        try:
            importlib.reload(upcoming_mod)
            upcoming_mod.view_movies1(parent_window)
        except Exception as e:
            messagebox.showerror("Error", f"Could not launch upcoming movies: {e}")
    else:
        messagebox.showwarning("Unavailable", "Upcoming movies module is not available.")


def open_showing_movies(parent_window):
    try:
        if 'movies' in sys.modules:
            importlib.reload(sys.modules['movies'])
            if hasattr(sys.modules['movies'], 'view_movies'):
                sys.modules['movies'].view_movies(parent_window)
                return
    except Exception:
        pass
    view_movies(parent_window)


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

# Subtle golden separator line under header
header_border = Frame(root, bg="#D4AF37", height=1)
header_border.pack(side="top", fill="x")

# Branding on top-left
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

# Date & Time display container on top-right
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
    """Live updater function for the real-time clock and current date."""
    current_time = time.strftime("%I:%M:%S %p")  # 12-hour format with AM/PM
    current_date = time.strftime("%A, %B %d, %Y")  # e.g., Tuesday, July 28, 2026
    lbl_time.config(text=f"🕒 {current_time}")
    lbl_date.config(text=f"📅 {current_date}")
    root.after(1000, update_datetime)  # Schedule refresh every 1 second


# Start live clock thread loop
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
    command=lambda: open_upcoming_movies(root)
)
btn_upcoming.pack(pady=7, ipady=5)
add_hover_effect(btn_upcoming, "#FF9800", "#FFB74D", "#121212", "#121212")

# Admin Button Linked directly to safe function caller
btn_admin = Button(
    card_frame,
    text="⚙️   Admin Control Panel",
    font=("Segoe UI", 11, "bold"),
    bg="#2B2B2B",
    fg="#FFD700",
    activebackground="#3D3D3D",
    activeforeground="#FFD700",
    width=26,
    height=1,
    cursor="hand2",
    bd=0,
    command=lambda: launch_admin_login(root)
)
btn_admin.pack(pady=7, ipady=5)
add_hover_effect(btn_admin, "#2B2B2B", "#3D3D3D", "#FFD700", "#FFD700")

btn_exit = Button(
    card_frame,
    text="❌   Exit System",
    font=("Segoe UI", 11, "bold"),
    bg="#2B2B2B",
    fg="#E53935",
    activebackground="#D32F2F",
    activeforeground="white",
    width=26,
    height=1,
    cursor="hand2",
    bd=0,
    command=root.destroy
)
btn_exit.pack(pady=(12, 5), ipady=5)
add_hover_effect(btn_exit, "#2B2B2B", "#E53935", "#E53935", "white")

Label(
    root,
    text="© 2026 AA Cinema. All Rights Reserved. Experience the Magic of Movies.",
    font=("Segoe UI", 9),
    fg="#aaaaaa",
    bg="#0d0d0d" if not BACKGROUND_IMAGE_PATH else "#121212"
).pack(side="bottom", pady=15)

root.mainloop()