import os
import sys
import time
from datetime import datetime
import json
import webbrowser
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# PDF imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# ------------------ Dynamic Search Path Setup ------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) if "Scripts" in script_dir else script_dir

for path in (script_dir, project_root):
    if path not in sys.path:
        sys.path.append(path)

# ------------------ Safe Database Import ------------------
conn = None
cursor = None
IS_SQLITE = False

try:
    from Scripts.database import conn, cursor
except ImportError:
    try:
        from database import conn, cursor
    except ImportError as e:
        print(f"Database import error in pay.py: {e}")

# Detect database type dynamically to handle placeholders correctly
if conn:
    IS_SQLITE = "sqlite" in type(conn).__module__.lower()

PH = "?" if IS_SQLITE else "%s"


# ------------------ PDF Ticket Generator Function ------------------
def generate_pdf_ticket(booking_id, customer_id, payment_id, total_amount, payment_method):
    """
    Generates an attractively formatted PDF cinema ticket complete with movie details,
    theater info, seat numbers, seat types, and payment details.
    """
    try:
        # Create output directory for tickets
        tickets_dir = os.path.join(project_root, "Tickets")
        os.makedirs(tickets_dir, exist_ok=True)

        pdf_filename = os.path.join(tickets_dir, f"Ticket_Booking_{booking_id}.pdf")

        # Fallbacks
        movie_title = "AA Cinema Movie"
        screen_name = "Screen 1"
        theater_location = "Main Branch"
        seats_str = "Standard"
        seat_id_val = "N/A"
        customer_name = f"Customer #{customer_id}"

        if cursor:
            try:
                # 1. Fetch Customer Name safely
                q_cust = f"SELECT name FROM customers WHERE customer_id = {PH}"
                cursor.execute(q_cust, (customer_id,))
                c_row = cursor.fetchone()
                if c_row:
                    customer_name = c_row[0] if isinstance(c_row, (tuple, list)) else c_row.get('name', customer_name)

                # 2. Query ALL Seats, Seat Types, and IDs booked by this customer for the current show/booking
                # Dialect-specific string concatenation
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

                # Fallback query if show_id comparison yields no results
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
                    else:  # tuple/list return
                        movie_title = str(row[0]) if row[0] else movie_title
                        screen_name = str(row[1]) if row[1] else screen_name
                        theater_location = str(row[2]) if row[2] else theater_location
                        seats_str = str(row[3]) if row[3] else seats_str
                        seat_id_val = str(row[4]) if row[4] else seat_id_val

            except Exception as db_err:
                print(f"Notice: Ticket query database error: {db_err}")

        # Format list strings nicely with spaces after commas
        seats_str = seats_str.replace(",", ", ")
        seat_id_val = seat_id_val.replace(",", ", ")

        # ------------------ Build ReportLab PDF Design ------------------
        # Document Margins: 0.75 in (54 pt) -> Printable Width = 7.0 in (504 pt)
        doc = SimpleDocTemplate(
            pdf_filename,
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )

        styles = getSampleStyleSheet()

        # Custom Color Palette
        GOLD = colors.HexColor("#D4AF37")
        DARK_BG = colors.HexColor("#1A1A1A")
        LIGHT_BG = colors.HexColor("#FAFAFA")
        TEXT_DARK = colors.HexColor("#222222")
        TEXT_MUTED = colors.HexColor("#666666")

        # Typography Styles
        title_style = ParagraphStyle('HeaderTitle', fontName='Helvetica-Bold', fontSize=18, textColor=GOLD, leading=22)
        subtitle_style = ParagraphStyle('HeaderSub', fontName='Helvetica-Bold', fontSize=8, textColor=colors.white, leading=10)
        movie_style = ParagraphStyle('MovieTitle', fontName='Helvetica-Bold', fontSize=15, textColor=DARK_BG, leading=19)
        label_style = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=8, textColor=TEXT_MUTED, leading=10)
        val_style = ParagraphStyle('Value', fontName='Helvetica-Bold', fontSize=10, textColor=TEXT_DARK, leading=13)
        ref_badge_style = ParagraphStyle('RefBadge', fontName='Helvetica-Bold', fontSize=9, textColor=GOLD, alignment=1)
        price_badge_style = ParagraphStyle('PriceBadge', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor("#2E7D32"), alignment=1)

        elements = []

        # Find Logo
        logo_path = None
        for name in ["logo_converted.png", "logo.png", "logo_converted.PNG"]:
            p1 = os.path.join(script_dir, name)
            p2 = os.path.join(project_root, name)
            if os.path.exists(p1): logo_path = p1; break
            elif os.path.exists(p2): logo_path = p2; break

        # Top Header Banner (Total Width = 6.2 inches)
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

        # ------------------ Dynamic Ticket Container Design ------------------
        # Booking Ref Badge
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

        # Information Grid displaying concatenated Seat IDs and Seat Numbers (Type)
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

        # Dashed Divider Line (Perforated Stub Line)
        dashed_line = HRFlowable(
            width="100%", thickness=1, color=colors.HexColor("#CCCCCC"),
            spaceBefore=8, spaceAfter=8, hAlign='CENTER', vAlign='MIDDLE', dash=[4, 4]
        )

        # Price Box
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

        # Outer Ticket Table Container Width = 6.2 inches
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

        # Footer Notice
        footer_style = ParagraphStyle('FooterText', fontName='Helvetica-Oblique', fontSize=8, textColor=TEXT_MUTED, alignment=1)
        elements.append(Paragraph("Thank you for choosing AA Cinema. Enjoy your movie!", footer_style))

        # Build Document
        doc.build(elements)

        # Open automatically
        webbrowser.open(f"file://{os.path.abspath(pdf_filename)}")
        return pdf_filename

    except Exception as e:
        print(f"Error generating PDF ticket: {e}")
        return None


def show_payment_window(parent, customer_id, total_amount=0.0):
    # ------------------ Create Window ------------------
    pay_window = Toplevel(parent)
    pay_window.title("Checkout & Payment - AA Cinema")
    pay_window.configure(bg="#0f0f0f")

    image_refs = []
    pay_window.image_refs = image_refs

    screen_w = parent.winfo_screenwidth()
    screen_h = parent.winfo_screenheight()

    pay_window.geometry(f"{screen_w}x{screen_h}+0+0")
    pay_window.deiconify()
    try:
        pay_window.state('zoomed')
    except Exception:
        try:
            pay_window.attributes('-fullscreen', True)
        except Exception:
            pass

    pay_window.lift()
    pay_window.focus_force()

    pay_window.bind("<Escape>", lambda e: pay_window.destroy())

    # ------------------ Top Date & Time Header Bar ------------------
    header_top_bar = Frame(pay_window, bg="#121212")
    header_top_bar.pack(side="top", fill="x")

    header_border = Frame(pay_window, bg="#D4AF37", height=1)
    header_border.pack(side="top", fill="x")

    header_brand = Label(
        header_top_bar,
        text="🍿 AA CINEMA - CHECKOUT & PAYMENT",
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

    def update_datetime():
        current_time = time.strftime("%I:%M:%S %p")
        current_date = time.strftime("%A, %B %d, %Y")
        lbl_time.config(text=f"🕒 {current_time}")
        lbl_date.config(text=f"📅 {current_date}")
        if pay_window.winfo_exists():
            pay_window.after(1000, update_datetime)

    update_datetime()

    # ------------------ Helper: File Path Resolution ------------------
    def find_file(filenames):
        for name in filenames:
            p1 = os.path.join(script_dir, name)
            p2 = os.path.join(project_root, name)
            if os.path.exists(p1):
                return p1
            elif os.path.exists(p2):
                return p2
        return None

    # ------------------ Logo Setup ------------------
    logo_path = find_file(["logo_converted.png", "logo.png", "logo_converted.PNG"])
    card_logo_img = None
    window_logo = None

    if logo_path and os.path.exists(logo_path):
        try:
            logo_raw = Image.open(logo_path)

            window_logo = ImageTk.PhotoImage(logo_raw, master=pay_window)
            pay_window.iconphoto(False, window_logo)
            image_refs.append(window_logo)

            logo_resized = logo_raw.resize((55, 55), Image.LANCZOS)
            card_logo_img = ImageTk.PhotoImage(logo_resized, master=pay_window)
            pay_window.card_logo_img = card_logo_img
            image_refs.append(card_logo_img)
        except Exception as e:
            print(f"Could not load logo in pay.py: {e}")

    # ------------------ Background Image Setup ------------------
    bg_path = find_file(["background.JPEG", "background.jpeg", "background.jpg", "background.PNG", "background.png"])
    bg_raw_img = None

    if bg_path and os.path.exists(bg_path):
        try:
            bg_raw_img = Image.open(bg_path)
        except Exception as e:
            print(f"Could not load background image in pay.py: {e}")

    # ------------------ Fetch Recent Bookings ------------------
    recent_bookings = []
    booked_count = 0

    if cursor:
        try:
            query_rec = f"""
                SELECT booking_id, seat_id
                FROM bookings
                WHERE customer_id = {PH}
                ORDER BY booking_id DESC
                LIMIT 10
            """
            cursor.execute(query_rec, (customer_id,))
            recent_bookings = cursor.fetchall()
            booked_count = len(recent_bookings)

            if total_amount <= 0.0 and recent_bookings:
                try:
                    q_price = f"""
                        SELECT t.price
                        FROM bookings b
                        JOIN seats s ON b.seat_id = s.seat_id
                        JOIN ticket t ON UPPER(s.seat_type) = UPPER(t.seat_type)
                        WHERE b.customer_id = {PH}
                    """
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

    # ------------------ Responsive Container & Background Canvas ------------------
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
                image_refs.append(current_bg_photo)
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

    # ------------------ Elevated Card Frame ------------------
    card = Frame(
        center_frame,
        bg="#1c1c1c",
        bd=1,
        relief="solid",
        highlightbackground="#333333",
        highlightthickness=1,
        padx=45,
        pady=30
    )
    card.pack(anchor="center", pady=20)

    if card_logo_img:
        logo_lbl = Label(card, image=card_logo_img, bg="#1c1c1c")
        logo_lbl.image = card_logo_img
        logo_lbl.pack(pady=(0, 8))

    Label(card, text="CHECKOUT & BILLING", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#1c1c1c").pack(pady=(0, 2))
    Label(card, text="Payment & Checkout", font=("Segoe UI", 20, "bold"), fg="white", bg="#1c1c1c").pack(pady=(0, 15))

    # ------------------ Order Summary Section ------------------
    summary_frame = Frame(card, bg="#262626", bd=1, relief="solid", highlightbackground="#3d3d3d", highlightthickness=1)
    summary_frame.pack(fill="x", pady=(0, 20), ipadx=10, ipady=5)

    Label(summary_frame, text="ORDER SUMMARY", font=("Segoe UI", 10, "bold"), fg="#FFD700", bg="#262626").pack(anchor="w", padx=15, pady=(10, 4))
    Label(summary_frame, text=f"Total Seats Selected: {booked_count}", font=("Segoe UI", 10), fg="#dddddd", bg="#262626").pack(anchor="w", padx=15, pady=2)
    Label(summary_frame, text=f"Total Amount Due: Rs. {total_amount:.2f}", font=("Segoe UI", 12, "bold"), fg="#00E676", bg="#262626").pack(anchor="w", padx=15, pady=(2, 10))

    # ------------------ Payment Method Selector ------------------
    Label(card, text="SELECT PAYMENT METHOD", font=("Segoe UI", 9, "bold"), fg="#aaaaaa", bg="#1c1c1c", anchor="w").pack(fill="x", pady=(0, 8))

    payment_method_var = StringVar(value="Credit / Debit Card")

    methods = [
        ("💳 Credit / Debit Card", "Credit / Debit Card"),
        ("📱 Mobile Wallet (Apple Pay / Google Pay)", "Mobile Wallet"),
        ("💵 Pay at Counter", "Pay at Counter")
    ]

    for label_text, value_text in methods:
        Radiobutton(
            card,
            text=label_text,
            variable=payment_method_var,
            value=value_text,
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#1c1c1c",
            selectcolor="#2b2b2b",
            activebackground="#1c1c1c",
            activeforeground="#FFD700",
            cursor="hand2"
        ).pack(anchor="w", padx=10, pady=3)

    # ------------------ Dynamic Input Sub-Frames ------------------
    card_frame = Frame(card, bg="#1c1c1c")
    Label(card_frame, text="Cardholder Name", font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w", pady=(8, 2))
    card_name_entry = Entry(card_frame, font=("Segoe UI", 10), bg="#2b2b2b", fg="white", insertbackground="white", bd=1, relief="solid")
    card_name_entry.pack(fill="x", pady=(0, 8), ipady=5)

    Label(card_frame, text="Card Number", font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#1c1c1c").pack(anchor="w", pady=(2, 2))
    card_num_entry = Entry(card_frame, font=("Segoe UI", 10), bg="#2b2b2b", fg="white", insertbackground="white", bd=1, relief="solid")
    card_num_entry.pack(fill="x", pady=(0, 5), ipady=5)

    wallet_frame = Frame(card, bg="#1c1c1c")
    Label(wallet_frame, text="Click below to complete authorization on your wallet platform:", font=("Segoe UI", 9), fg="#aaaaaa", bg="#1c1c1c").pack(anchor="w", pady=(10, 8))

    btn_subframe = Frame(wallet_frame, bg="#1c1c1c")
    btn_subframe.pack(fill="x")

    Button(btn_subframe, text="🍎 Open Apple Pay", bg="#2b2b2b", fg="white", activebackground="#3d3d3d", activeforeground="white", font=("Segoe UI", 9, "bold"), cursor="hand2", bd=0, command=lambda: webbrowser.open("https://www.apple.com/apple-pay/")).pack(side="left", padx=(0, 6), expand=True, fill="x", ipady=5)
    Button(btn_subframe, text="🌐 Open Google Pay", bg="#2b2b2b", fg="white", activebackground="#3d3d3d", activeforeground="white", font=("Segoe UI", 9, "bold"), cursor="hand2", bd=0, command=lambda: webbrowser.open("https://pay.google.com/")).pack(side="left", expand=True, fill="x", ipady=5)

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

    # ------------------ Custom Payment Success Window ------------------
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

        dw, dh = 420, 480
        sx = (pay_window.winfo_screenwidth() - dw) // 2
        sy = (pay_window.winfo_screenheight() - dh) // 2
        dlg.geometry(f"{dw}x{dh}+{sx}+{sy}")
        dlg.resizable(False, False)

        success_img_path = find_file(["Paymentsuccess.PNG", "Paymentsuccess.png", "Paymentsuccess.jpg", "Paymentsuccess.jpeg"])

        if success_img_path and os.path.exists(success_img_path):
            try:
                raw_img = Image.open(success_img_path)
                resized = raw_img.resize((220, 150), Image.LANCZOS)
                ph = ImageTk.PhotoImage(resized, master=dlg)
                img_lbl = Label(dlg, image=ph, bg="#1c1c1c")
                dlg.ph = ph  # Prevent garbage collection of image
                img_lbl.pack(pady=(25, 10))
            except Exception as e:
                print(f"Could not display Paymentsuccess image: {e}")

        Label(dlg, text="Card Payment Successful! 💳", font=("Segoe UI", 14, "bold"), fg="#00E676", bg="#1c1c1c").pack(pady=(5, 10))

        msg_text = (
            f"Payment of Rs. {amount:.2f} via Credit / Debit Card\n"
            f"was processed successfully!\n\n"
            f"Your PDF ticket pass has been generated."
        )

        Label(dlg, text=msg_text, font=("Segoe UI", 10), fg="#dddddd", bg="#1c1c1c", justify="center").pack(padx=20, pady=(0, 20))

        btn_close = Button(
            dlg,
            text="OK",
            bg="#00E676",
            fg="black",
            activebackground="#00c853",
            activeforeground="black",
            font=("Segoe UI", 10, "bold"),
            width=15,
            bd=0,
            cursor="hand2",
            command=dlg.destroy
        )
        btn_close.pack(pady=(0, 20), ipady=5)

        dlg.wait_window()

    # ------------------ Process Payment Execution ------------------
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
                    q_pay = f"""
                        INSERT INTO payments (booking_id, customer_id, amount, payment_date, payment_method, payment_status)
                        VALUES ({PH}, {PH}, {PH}, {PH}, {PH}, {PH})
                    """
                    cursor.execute(q_pay, (primary_booking_id, customer_id, total_amount, payment_date, method, status_val))
                    inserted_booking_id = primary_booking_id
                else:
                    q_pay = f"""
                    INSERT INTO payments
                    (customer_id, amount, payment_date, payment_method, payment_status)
                    VALUES ({PH}, {PH}, {PH}, {PH}, {PH})
                    """

                    cursor.execute(
                        q_pay,
                        (
                            customer_id,
                            total_amount,
                            payment_date,
                            method,
                            status_val
                        )
                    )
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

        # ------------------ Generate PDF ------------------
        pdf_path = generate_pdf_ticket(
            booking_id=inserted_booking_id,
            customer_id=customer_id,
            payment_id=inserted_payment_id,
            total_amount=total_amount,
            payment_method=method
        )

        # ------------------ Confirmation Notifications ------------------
        if method == "Credit / Debit Card":
            show_card_success_modal(total_amount)
        elif method == "Mobile Wallet":
            messagebox.showinfo(
                "Wallet Payment Successful! 📱",
                f"Payment of Rs. {total_amount:.2f} via Mobile Wallet was verified!\n\n"
                f"Your PDF ticket pass has been saved to 'Tickets/'."
            )
        elif method == "Pay at Counter":
            messagebox.showinfo(
                "Seats Reserved! 💵",
                f"Your seats have been successfully reserved!\n\n"
                f"Total Amount Due: Rs. {total_amount:.2f}\n"
                f"Your printable reservation voucher has been created."
            )

        pay_window.destroy()
        if parent:
            parent.deiconify()
            parent.lift()
            parent.focus_force()

    # ------------------ Action Controls ------------------
    action_frame = Frame(card, bg="#1c1c1c")
    action_frame.pack(fill="x", pady=(20, 0))

    btn_back = Button(
        action_frame,
        text="Cancel",
        bg="#E53935",
        fg="white",
        activebackground="#d32f2f",
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        width=12,
        cursor="hand2",
        bd=0,
        command=pay_window.destroy
    )
    btn_back.pack(side="left", ipady=6, padx=(0, 8))

    btn_confirm = Button(
        action_frame,
        text="Confirm & Pay 🎟️",
        bg="#4CAF50",
        fg="white",
        activebackground="#45a049",
        activeforeground="white",
        font=("Segoe UI", 11, "bold"),
        width=20,
        cursor="hand2",
        bd=0,
        command=process_payment
    )
    btn_confirm.pack(side="right", ipady=6, padx=(8, 0))