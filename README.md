<p align="center">
  <img width="400" height="400" alt="logo_converted" src="https://github.com/user-attachments/assets/4f38b4f9-b3c1-4735-9ae4-2e0720b1ff75" />
</p>
<h1 align="center">AA CINEMA</h1>
<p align="center"><b>Cinema Booking System</b></p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-0052CC?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-00BFFF?style=flat-square" alt="GUI">
  <img src="https://img.shields.io/badge/Database-MySQL-EA5B0C?style=flat-square&logo=mysql&logoColor=white" alt="Database">
  <img src="https://img.shields.io/badge/Document_Engine-ReportLab-26A65B?style=flat-square" alt="ReportLab">
  <img src="https://img.shields.io/badge/Status-Active-47A248?style=flat-square" alt="Status">
</p>

The **AA Cinema Management System** is a desktop application designed to streamline theater operations, movie scheduling, seat allocation, customer registration, checkout processing, and admin security. Built with an intuitive Tkinter interface, custom dark-themed UI components, and a robust backend, the system offers an end-to-end ticketing and administration experience.

---

## 💻 Visual Application Workflow & UI Features

### 1. Main Navigation Hub

<img width="1900" height="1015" alt="Screenshot (467)" src="https://github.com/user-attachments/assets/fa918c86-831e-40c8-86b0-a68361916f4c" />

* **Welcome Screen:** Features dynamic date/time tracking in the top header and clean navigation.
* **Core Action Buttons:**
* **🎬 Now Showing Movies:** Direct link to currently active film listings.
* **📅 Upcoming Releases:** First-look gallery for upcoming films.
* **⚙️ Admin Control Panel:** Secure portal for staff and administrator login.
* **❌ Exit System:** Safely terminates application execution.
---

### 2. Movie Catalog Views

#### 🎬 Now Showing
Displays active screenings with rich movie card layouts:

<img width="1900" height="1015" alt="Screenshot (469)" src="https://github.com/user-attachments/assets/86067ad8-8ac5-4c99-bc6d-5b91aec5864f" />

* **Movie Metadata:** Displays poster preview, title, genre tags (*Sci-Fi, Action, Animation, Adventure*), duration, audio language, and release date.

* **Action:** Direct **"Book Ticket"** triggers for active screenings.

#### 🌟 Upcoming Releases ("Coming Soon")
Provides an exclusive look at scheduled upcoming titles:

<img width="1920" height="1020" alt="Screenshot (468)" src="https://github.com/user-attachments/assets/82e4b10e-a5b8-4a91-bed1-68ff6158d6b6" />

---

### 3. Customer Booking Workflow

#### Step 1: Guest Checkout (Customer Information)

<img width="1900" height="1013" alt="Screenshot (472)" src="https://github.com/user-attachments/assets/6dfb0f46-a1d9-4cc3-9849-6cd63d7109db" />

#### Step 2: Theater & Showtime Selection

<img width="1900" height="1015" alt="Screenshot (485)" src="https://github.com/user-attachments/assets/adedd518-fc6f-4190-ae7a-570952abc265" />

#### Step 3: Auditorium Interactive Seat Map
Interactive visual seat layout with tier-based pricing:

<img width="1900" height="1017" alt="Screenshot (486)" src="https://github.com/user-attachments/assets/b225a73e-3bd6-45f8-bf16-d760c2124175" />


* **ODC Section:** Standard seats priced at **Rs. 800.00** per seat (e.g., Seats `A1` – `A10`).
* **Balcony Section:** Premium seats priced at **Rs. 900.00** per seat (e.g., Seats `A11` – `A20`).
* **Real-time Status Legend:**
* 🟩 **Green (Available):** Vacant seats ready for selection.
* 🟨 **Yellow (Selected):** Active seat selections.
* 🟥 **Red (Booked):** Occupied/reserved seats.


* **Dynamic Cart Summary:** Live tally of total selected seats and total calculated amount (e.g., *Selected: 2 Seat(s) | Total Amount: Rs. 1800.00*).

---

### 4. Payment & Automated E-Ticket Generation

Supports flexible payment channels with instant confirmation feedback and dynamic PDF pass output:
Payments Methods:
#### Option A: Credit / Debit Card

<img width="1900" height="1024" alt="Screenshot (475)" src="https://github.com/user-attachments/assets/d86e6d07-96cc-477d-aeb9-42ea7b3ac808" />

#### Option B: Mobile Wallet

<img width="1900" height="1017" alt="Screenshot (476)" src="https://github.com/user-attachments/assets/647e9030-6501-4e4a-b993-6e95717864bf" />

#### Option C: Pay at Counter

<img width="1900" height="1026" alt="Screenshot (477)" src="https://github.com/user-attachments/assets/66eb9df7-3128-42e3-ae52-c99a4ffacb06" />

Payment Confirmation
Real-time Processing Notice: Pops up upon successful checkout completion.
<p align="center">
  <img width="523" height="637" alt="Screenshot (487)" src="https://github.com/user-attachments/assets/87e39413-196a-4e64-8de6-b8d1099a4fc2" />
</p>p
Automated PDF Ticket Generation: Confirms successful payment processing (e.g., Rs. 1800.00 via Credit / Debit Card) and automatically outputs the official entry pass.

Official Generated E-Ticket Pass
PDF E-Ticket Breakdown: Automatically generates a branded ticket containing:

<img width="1900" height="1017" alt="Screenshot (488)" src="https://github.com/user-attachments/assets/5eb657c2-63db-433b-a406-bef77d835917" />


Booking Reference: Unique ID tag (e.g., #BK-145).

Customer & Venue Info: Passenger name, cinema hall location, and movie title.

Seat & Pricing Breakdown: Explicit seat IDs/numbers (e.g., A12 (BALCONY), A13 (BALCONY)), payment method, and total amount paid.

Entry Pass Requirement: Formatted pass ready to present at venue entry.

---
### 5. Security & Administration Control Center
🔐 How It Works Under the Hood:

Admin Login: Full access to all tabs (including Analytics and Suppliers) + Data Deletion rights.

<img width="779" height="120" alt="Screenshot (497)" src="https://github.com/user-attachments/assets/dbbb16be-463c-4190-b538-9f95ad67a826" />

🔐 Admin Authentication Panel:
<p align="center">
<img width="473" height="603" alt="Screenshot (470)" src="https://github.com/user-attachments/assets/bcb5f29f-2fa1-46b5-9eb9-eb1729ad5dc4" />
</p>
Dedicated login module requiring Admin ID and Password credentials to access administrative controls, catalog operations, and revenue analytics.

📊 Admin System Dashboard Overview

<img width="1900" height="1013" alt="Screenshot (489)" src="https://github.com/user-attachments/assets/c01fcfdf-c6d6-483f-b048-5e015d3f59dc" />

Provides high-level system metrics at a glance:

Total Bookings Count (e.g., 4).

Total Revenue Tracked (e.g., Rs. 3,400.00).

Pending Payments Tally (e.g., 0).

Configured Capacity / Seats Count (e.g., 120).

🎬 Movie Management Module

<img width="1900" height="1011" alt="Screenshot (490)" src="https://github.com/user-attachments/assets/8fc4d554-9ced-4d53-a4cc-51ae12df4ca1" />

Empowers admins to control catalog inventory in real time:

Add New Movie Form: Direct entry fields for Title, Genre, Duration (mins), Language, Release Date (YYYY-MM-DD), and Poster File Path/URL.

Catalog Data Table: Data grid displaying current database records with options to view, edit, or delete existing titles.

just like this module, all the other modules are managed by the admin panel.
---

## 🗄️ Database Architecture Schema

```text
[ Customers ] ─── (1:N) ─── [ Bookings ] ─── (N:1) ─── [ Showtimes ] ─── (N:1) ─── [ Movies ]
                                 │                            │
                              (N:1)                        (N:1)
                                 │                            │
                              [ Seats ] ─── (N:1) ──── [ Theaters ]
                                 │
                              (1:1)
                                 │
                             [ Payments ]

```

### Table Breakdown

| Table Name | Primary Key | Attributes / Foreign Keys | Description |
| --- | --- | --- | --- |
| **`movies`** | `movie_id` | `title`, `genre`, `duration`, `language`, `release_date`, `poster` | Stores active and upcoming movie catalog data. |
| **`theaters`** | `theater_id` | `theater_name`, `location` | Stores physical theater and screen locations. |
| **`seats`** | `seat_id` | `theater_id` *(FK)*, `seat_number`, `section_type`, `price` | Contains seat mapping, row structures, and section pricing (ODC / Balcony). |
| **`showtimes`** | `show_id` | `movie_id` *(FK)*, `theater_id` *(FK)*, `show_date`, `show_time` | Maps scheduled movies to specific screens and dates/times. |
| **`customers`** | `customer_id` | `full_name`, `email`, `phone` | Stores guest checkout contact details. |
| **`bookings`** | `booking_id` | `customer_id` *(FK)*, `show_id` *(FK)*, `seat_id` *(FK)*, `booking_date` | Logs completed ticket reservations. |
| **`payments`** | `payment_id` | `booking_id` *(FK)*, `amount`, `payment_method`, `payment_status`, `payment_date` | Manages financial transaction details (Card, Mobile Wallet, Counter Cash). |

---

### 🛠️ Technology Stack
<ul>
  GUI / Frontend: Python Tkinter, Pillow (PIL)

  PDF Engine: ReportLab / FPDF (for automated ticket generation)
  
  Styling & UI: Dark Mode aesthetic with custom color-coded status badges
  
  Backend Core: Python 3.x
  
  Database: MySQL / MariaDB
  
  Connector: mysql-connector-python / pymysql
</ul>

