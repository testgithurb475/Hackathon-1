"""
Smart Bus Reservation System — nicer GUI (tkinter, built-in only)

Same rules as the console version:
  - validate before changing data
  - cancel restores seats exactly once
  - cancelled bookings kept but excluded from revenue
Data is IN MEMORY only.

Run:  python Gui.py
"""

import tkinter as tk
from tkinter import ttk


# ============================================================
# COLORS  (change these to re-theme the whole app)
# ============================================================
DARK    = "#0f172a"
DARKER  = "#020617"
ACCENT  = "#2563eb"
ACCENT_D= "#1d4ed8"
BG      = "#f1f5f9"
CARD    = "#ffffff"
TEXT    = "#0f172a"
MUTED   = "#64748b"
BORDER  = "#e2e8f0"
GREEN   = "#16a34a"
RED     = "#dc2626"


# ============================================================
# DATA
# ============================================================
routes = [
    {"route_id": "R101", "departure": "Karachi",   "destination": "Hyderabad",
     "time": "08:00 AM", "fare": 1200, "total": 40, "available": 40},
    {"route_id": "R102", "departure": "Karachi",   "destination": "Sukkur",
     "time": "09:30 AM", "fare": 2000, "total": 36, "available": 36},
    {"route_id": "R103", "departure": "Hyderabad", "destination": "Mirpur Khas",
     "time": "11:00 AM", "fare": 800,  "total": 32, "available": 32},
    {"route_id": "R104", "departure": "Karachi",   "destination": "Lahore",
     "time": "07:00 PM", "fare": 5000, "total": 45, "available": 45},
    {"route_id": "R105", "departure": "Sukkur",    "destination": "Hyderabad",
     "time": "02:00 PM", "fare": 1500, "total": 30, "available": 30},
]

cities     = ("Karachi", "Hyderabad", "Sukkur", "Mirpur Khas", "Lahore")
bookings   = []
issued_ids = set()


# ============================================================
# HELPERS
# ============================================================
def find_route(route_id):
    for r in routes:
        if r["route_id"].lower() == str(route_id).strip().lower():
            return r
    return None


def make_booking_id():
    number = 1001
    while ("B" + str(number)) in issued_ids:
        number += 1
    new_id = "B" + str(number)
    issued_ids.add(new_id)
    return new_id


def money(amount):
    return "Rs. " + format(amount, ",")


def journey(route):
    return route["departure"] + "  →  " + route["destination"]


def seat_text(route):
    if route["available"] == 0:
        return "Fully Booked"
    return str(route["available"]) + " / " + str(route["total"])


def status_text(route):
    if route["available"] == 0:
        return "Fully Booked"
    if route["available"] == route["total"]:
        return "Available"
    return "Partially Booked"


# ============================================================
# APP
# ============================================================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Bus Reservation System")
        self.geometry("1200x760")
        self.minsize(1000, 680)
        self.configure(bg=BG)

        self._setup_ttk_style()
        self._build_sidebar()
        self._build_content_area()
        self._build_status_bar()

        self.show_page("routes")
        self.refresh_all()
        self.set_status("Ready — records are kept in memory only.")

    # --------------------------------------------------------
    # ttk style
    # --------------------------------------------------------
    def _setup_ttk_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("Treeview",
                        background=CARD, fieldbackground=CARD,
                        foreground=TEXT, borderwidth=0,
                        rowheight=32, font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background=BG, foreground=MUTED,
                        relief="flat", borderwidth=0,
                        font=("Segoe UI", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", "white")])

        style.configure("TCombobox",
                        fieldbackground=CARD, background=CARD,
                        foreground=TEXT, arrowcolor=MUTED,
                        padding=6)

    # --------------------------------------------------------
    # SIDEBAR
    # --------------------------------------------------------
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=DARK, width=220)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        brand = tk.Frame(sidebar, bg=DARKER, pady=22)
        brand.pack(fill="x")
        tk.Label(brand, text="SMART BUS", bg=DARKER, fg="white",
                 font=("Segoe UI", 15, "bold")).pack()
        tk.Label(brand, text="Reservation System", bg=DARKER, fg="#94a3b8",
                 font=("Segoe UI", 9)).pack(pady=(2, 0))

        self.nav_buttons = {}
        nav_items = [
            ("routes",       "1. View Routes"),
            ("search",       "2. Search"),
            ("book",         "3. Book Ticket"),
            ("bookings",     "4. My Bookings"),
            ("cancel",       "5. Cancel Booking"),
            ("availability", "6. Availability"),
            ("report",       "7. Report"),
            ("schedule",     "8. Schedule"),
        ]
        for page, label in nav_items:
            btn = tk.Button(
                sidebar, text=label, anchor="w",
                font=("Segoe UI", 10), padx=22, pady=12,
                bg=DARK, fg="#cbd5e1", bd=0, relief="flat",
                activebackground=DARK, activeforeground="white",
                cursor="hand2",
                command=lambda p=page: self.show_page(p),
            )
            btn.pack(fill="x")
            self.nav_buttons[page] = btn

        info = tk.Frame(sidebar, bg=DARK, pady=12)
        info.pack(side="bottom", fill="x")
        tk.Label(info, text="In-memory only", bg=DARK, fg="#94a3b8",
                 font=("Segoe UI", 8)).pack()

    # --------------------------------------------------------
    # CONTENT AREA
    # --------------------------------------------------------
    def _build_content_area(self):
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.pages = {}
        page_builders = {
            "routes":       self._build_routes_page,
            "search":       self._build_search_page,
            "book":         self._build_book_page,
            "bookings":     self._build_bookings_page,
            "cancel":       self._build_cancel_page,
            "availability": self._build_availability_page,
            "report":       self._build_report_page,
            "schedule":     self._build_schedule_page,
        }

        for name, builder in page_builders.items():
            frame = tk.Frame(self.content, bg=BG, padx=32, pady=28)
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[name] = frame
            builder(frame)

        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

    # --------------------------------------------------------
    # STATUS BAR
    # --------------------------------------------------------
    def _build_status_bar(self):
        self.status_var = tk.StringVar(value="")
        bar = tk.Frame(self, bg=DARKER, pady=6)
        bar.pack(side="bottom", fill="x")
        tk.Label(bar, textvariable=self.status_var,
                 bg=DARKER, fg="#cbd5e1", anchor="w",
                 font=("Segoe UI", 9), padx=16).pack(fill="x")

    def set_status(self, message):
        self.status_var.set("  " + message)

    # --------------------------------------------------------
    # PAGE SWITCHING
    # --------------------------------------------------------
    def show_page(self, name):
        for page_name, btn in self.nav_buttons.items():
            if page_name == name:
                btn.configure(bg=ACCENT, fg="white")
            else:
                btn.configure(bg=DARK, fg="#cbd5e1")
        self.pages[name].tkraise()

    # ========================================================
    # REUSABLE WIDGETS
    # ========================================================
    def page_header(self, parent, title, subtitle):
        tk.Label(parent, text=title, bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(parent, text=subtitle, bg=BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w", pady=(2, 22))

    def card(self, parent):
        return tk.Frame(parent, bg=CARD, padx=20, pady=16,
                        highlightthickness=1, highlightbackground=BORDER)

    def primary_button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command,
                         font=("Segoe UI", 10, "bold"),
                         bg=ACCENT, fg="white",
                         activebackground=ACCENT_D, activeforeground="white",
                         relief="flat", bd=0, padx=18, pady=8,
                         cursor="hand2")

    def secondary_button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command,
                         font=("Segoe UI", 10),
                         bg=CARD, fg=TEXT,
                         activebackground=BG, activeforeground=TEXT,
                         relief="flat", bd=0, padx=14, pady=6,
                         highlightthickness=1, highlightbackground=BORDER,
                         cursor="hand2")

    def entry(self, parent, textvariable):
        return tk.Entry(parent, textvariable=textvariable,
                        font=("Segoe UI", 10), bg="white", fg=TEXT,
                        relief="flat", bd=0,
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=ACCENT,
                        insertbackground=TEXT)

    def make_table(self, parent, columns, headings, widths):
        wrapper = tk.Frame(parent, bg=CARD,
                           highlightthickness=1, highlightbackground=BORDER)
        wrapper.pack(fill="both", expand=True)

        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="w")

        scroll = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)

        tree.pack(side="left", fill="both", expand=True, padx=(1, 0), pady=1)
        scroll.pack(side="right", fill="y", pady=1)

        tree.tag_configure("cancelled", foreground=MUTED)
        return tree

    def _build_routes_page(self, parent):
        self.page_header(parent, "Available Routes",
                         "Browse all bus routes and their seat status.")

        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(0, 12))

        self.routes_only = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="Only routes with seats",
                       variable=self.routes_only,
                       command=self.refresh_routes,
                       bg=BG, fg=TEXT, font=("Segoe UI", 10),
                       activebackground=BG, selectcolor="white",
                       cursor="hand2").pack(side="left")

        self.secondary_button(bar, "Refresh", self.refresh_all).pack(side="right")

        self.routes_tree = self.make_table(
            parent,
            ("no", "id", "journey", "time", "fare", "seats", "status"),
            {"no": "#", "id": "Route", "journey": "Journey",
             "time": "Departure", "fare": "Fare",
             "seats": "Seats (free / total)", "status": "Status"},
            {"no": 50, "id": 90, "journey": 340, "time": 120,
             "fare": 110, "seats": 170, "status": 150},
        )

    def refresh_routes(self):
        for row in self.routes_tree.get_children():
            self.routes_tree.delete(row)

        only = self.routes_only.get()
        shown = 0
        for r in routes:
            if only and r["available"] == 0:
                continue
            shown += 1
            self.routes_tree.insert("", "end", values=(
                shown, r["route_id"], journey(r), r["time"],
                money(r["fare"]), seat_text(r), status_text(r)))

        if shown == 0:
            self.routes_tree.insert("", "end",
                values=("", "—", "No routes with seats available.", "",
                        "", "", ""))

    def _build_search_page(self, parent):
        self.page_header(parent, "Search Routes",
                         "Search by route ID, departure city, or destination city.")

        bar = self.card(parent)
        bar.pack(fill="x", pady=(0, 14))

        row = tk.Frame(bar, bg=CARD)
        row.pack(fill="x")

        self.search_var = tk.StringVar()
        entry = self.entry(row, self.search_var)
        entry.configure(font=("Segoe UI", 11))
        entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))
        entry.bind("<Return>", lambda e: self.do_search())

        self.primary_button(row, "Search", self.do_search).pack(side="left")

        self.search_msg = tk.StringVar(value="")
        tk.Label(parent, textvariable=self.search_msg,
                 bg=BG, fg=MUTED, font=("Segoe UI", 10)
                 ).pack(anchor="w", pady=(0, 10))

        self.search_tree = self.make_table(
            parent,
            ("id", "journey", "time", "fare", "seats", "status"),
            {"id": "Route", "journey": "Journey", "time": "Departure",
             "fare": "Fare", "seats": "Seats", "status": "Status"},
            {"id": 90, "journey": 320, "time": 120, "fare": 110,
             "seats": 110, "status": 150},
        )

    def do_search(self):
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)

        term = self.search_var.get().strip()
        if term == "":
            self.search_msg.set("Please type something to search.")
            return

        key = term.lower()
        matches = []

        for r in routes:
            if r["route_id"].lower() == key:
                matches.append(r)
                break
            if key in r["departure"].lower() or key in r["destination"].lower():
                matches.append(r)
        else:
            if not matches:
                self.search_msg.set('No routes matched "' + term + '".')
                return

        for r in matches:
            self.search_tree.insert("", "end", values=(
                r["route_id"], journey(r), r["time"],
                money(r["fare"]), seat_text(r), status_text(r)))

        self.search_msg.set(str(len(matches)) + " route(s) found.")
        self.set_status("Search '" + term + "' → " + str(len(matches)) + " route(s).")

    def _build_book_page(self, parent):
        self.page_header(parent, "Book a Ticket",
                         "Fill in the passenger details and confirm.")

        form_card = self.card(parent)
        form_card.pack(fill="x", pady=(0, 14))

        form = tk.Frame(form_card, bg=CARD)
        form.pack(fill="x")

        self.name_var  = tk.StringVar()
        self.age_var   = tk.StringVar()
        self.route_var = tk.StringVar()
        self.seats_var = tk.StringVar()

        label_style = {"bg": CARD, "fg": MUTED, "font": ("Segoe UI", 9)}
        row_style   = {"pady": 8}          # only grid-valid options

        # Row 0 — Name
        tk.Label(form, text="PASSENGER NAME", **label_style
                 ).grid(row=0, column=0, sticky="w")
        self.entry(form, self.name_var).grid(
            row=1, column=0, sticky="ew", ipady=8, **row_style)

        # Row 1 — Age + Route side by side
        tk.Label(form, text="AGE", **label_style
                 ).grid(row=0, column=1, sticky="w", padx=(20, 0))
        self.entry(form, self.age_var).grid(
            row=1, column=1, sticky="ew", ipady=8, padx=(20, 0), **row_style)

        tk.Label(form, text="ROUTE", **label_style
                 ).grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.route_combo = ttk.Combobox(form, textvariable=self.route_var,
                                        state="readonly", font=("Segoe UI", 10))
        self.route_combo.grid(row=1, column=2, sticky="ew", ipady=5,
                              padx=(20, 0), **row_style)

        # Row 2 — Seats + Book button
        tk.Label(form, text="NUMBER OF SEATS", **label_style
                 ).grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.entry(form, self.seats_var).grid(
            row=3, column=0, sticky="ew", ipady=8, pady=(0, 4))

        self.primary_button(form, "Confirm Booking", self.do_book
                            ).grid(row=3, column=1, columnspan=2,
                                   sticky="e", padx=(20, 0), pady=(0, 4))

        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=2)

        self.book_msg = tk.StringVar(value="")
        self.book_msg_label = tk.Label(parent, textvariable=self.book_msg,
                                       bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.book_msg_label.pack(anchor="w", pady=(4, 10))

        tk.Label(parent, text="TICKET", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")

        self.ticket = tk.Text(parent, height=9, font=("Consolas", 10),
                              bg=DARK, fg="#e2e8f0",
                              relief="flat", bd=0, padx=18, pady=14)
        self.ticket.pack(fill="both", expand=True, pady=(4, 0))
        self.ticket.configure(state="disabled")

    def set_ticket(self, text):
        self.ticket.configure(state="normal")
        self.ticket.delete("1.0", "end")
        if text:
            self.ticket.insert("1.0", text)
        self.ticket.configure(state="disabled")

    def _book_error(self, message):
        self.book_msg_label.configure(fg=RED)
        self.book_msg.set(message)

    def do_book(self):
        name = self.name_var.get().strip()
        if name == "":
            return self._book_error("Passenger name cannot be empty.")

        try:
            age = int(self.age_var.get().strip())
        except ValueError:
            return self._book_error("Age must be a whole number.")
        if age <= 0:
            return self._book_error("Age must be more than zero.")

        if self.route_var.get() == "":
            return self._book_error("Please choose a route.")
        route = find_route(self.route_var.get().split(" | ")[0])
        if route is None:
            return self._book_error("That route no longer exists.")

        try:
            seats = int(self.seats_var.get().strip())
        except ValueError:
            return self._book_error("Seats must be a whole number.")
        if seats <= 0:
            return self._book_error("Seats must be more than zero.")
        if seats > route["available"]:
            return self._book_error(
                "Only " + str(route["available"]) + " seat(s) left on "
                + route["route_id"] + ".")

        booking_id = make_booking_id()
        fare = route["fare"] * seats

        bookings.append({
            "booking_id": booking_id,
            "name": name, "age": age,
            "route_id": route["route_id"],
            "seats": seats, "fare": fare,
            "status": "Confirmed",
        })
        route["available"] -= seats

        self.refresh_all()
        self.book_msg_label.configure(fg=GREEN)
        self.book_msg.set("Booking " + booking_id + " confirmed.")

        self.set_ticket(
            "BOOKING CONFIRMED\n"
            "────────────────────────────────\n"
            "Booking ID : " + booking_id + "\n"
            "Passenger  : " + name + "  (age " + str(age) + ")\n"
            "Route      : " + route["route_id"] + "  |  "
            + journey(route) + "  |  " + route["time"] + "\n"
            "Seats      : " + str(seats) + "\n"
            "Total fare : " + money(fare) + "\n"
            "Seats left : " + str(route["available"])
            + " / " + str(route["total"]) + "\n"
        )

        self.name_var.set("")
        self.age_var.set("")
        self.seats_var.set("")
        self.set_status("Booking " + booking_id + " confirmed for " + name + ".")

    def refresh_route_combo(self):
        values = []
        for r in routes:
            values.append(
                r["route_id"] + " | " + journey(r) + " | " + r["time"]
                + "  (" + str(r["available"]) + " seats left)")
        self.route_combo["values"] = values
        if self.route_var.get() not in values:
            self.route_var.set("")

    def _build_bookings_page(self, parent):
        self.page_header(parent, "My Bookings",
                         "All bookings — cancelled records stay for history.")

        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.secondary_button(bar, "Refresh", self.refresh_all).pack(side="right")

        self.bookings_tree = self.make_table(
            parent,
            ("no", "id", "name", "age", "journey", "seats", "fare", "status"),
            {"no": "#", "id": "Booking ID", "name": "Passenger", "age": "Age",
             "journey": "Journey", "seats": "Seats", "fare": "Fare",
             "status": "Status"},
            {"no": 50, "id": 100, "name": 160, "age": 60, "journey": 300,
             "seats": 80, "fare": 120, "status": 130},
        )

    def refresh_bookings(self):
        for row in self.bookings_tree.get_children():
            self.bookings_tree.delete(row)

        if len(bookings) == 0:
            self.bookings_tree.insert("", "end",
                values=("", "—", "No bookings found.", "", "", "", "", ""))
            return

        for index, b in enumerate(bookings, start=1):
            route = find_route(b["route_id"])
            text = journey(route) if route else b["route_id"]
            tag = ("cancelled",) if b["status"] == "Cancelled" else ()
            self.bookings_tree.insert("", "end", tags=tag, values=(
                index, b["booking_id"], b["name"], b["age"], text,
                b["seats"], money(b["fare"]), b["status"]))

    def _build_cancel_page(self, parent):
        self.page_header(parent, "Cancel a Booking",
                         "Only Confirmed bookings can be cancelled. "
                         "Seats are restored once.")

        card = self.card(parent)
        card.pack(fill="x", pady=(0, 14))

        tk.Label(card, text="CHOOSE A CONFIRMED BOOKING",
                 bg=CARD, fg=MUTED, font=("Segoe UI", 9)
                 ).pack(anchor="w", pady=(0, 6))

        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x")

        self.cancel_var = tk.StringVar()
        self.cancel_combo = ttk.Combobox(row, textvariable=self.cancel_var,
                                         font=("Segoe UI", 10), state="readonly")
        self.cancel_combo.pack(side="left", fill="x", expand=True, ipady=6,
                               padx=(0, 12))

        self.primary_button(row, "Cancel Booking", self.do_cancel
                            ).pack(side="left")

        self.cancel_msg = tk.StringVar(value="")
        self.cancel_msg_label = tk.Label(parent, textvariable=self.cancel_msg,
                                         bg=BG, fg=MUTED, font=("Segoe UI", 10))
        self.cancel_msg_label.pack(anchor="w", pady=8)

    def refresh_cancel_options(self):
        values = []
        for b in bookings:
            if b["status"] == "Confirmed":
                values.append(b["booking_id"] + "  —  " + b["name"]
                              + "  (" + str(b["seats"]) + " seat(s), "
                              + b["route_id"] + ")")
        self.cancel_combo["values"] = values
        if self.cancel_var.get() not in values:
            self.cancel_var.set("")

    def _cancel_error(self, message):
        self.cancel_msg_label.configure(fg=RED)
        self.cancel_msg.set(message)

    def do_cancel(self):
        raw = self.cancel_var.get().strip()
        if raw == "":
            return self._cancel_error("Please choose a booking to cancel.")

        booking_id = raw.split(" ")[0].upper()

        found = None
        for b in bookings:
            if b["booking_id"] == booking_id:
                found = b
                break

        if found is None:
            return self._cancel_error("Booking " + booking_id
                                      + " not found. Nothing changed.")

        if found["status"] == "Cancelled":
            return self._cancel_error("Booking " + booking_id
                                      + " is already cancelled — seats NOT restored again.")

        route = find_route(found["route_id"])

        # Set status FIRST, then restore seats — guarantees one-time restore.
        found["status"] = "Cancelled"
        if route is not None:
            route["available"] += found["seats"]

        self.cancel_var.set("")
        self.refresh_all()

        message = ("Booking " + booking_id + " cancelled. "
                   + str(found["seats"]) + " seat(s) restored.")
        if route is not None:
            message += (" Route " + route["route_id"] + " now has "
                        + str(route["available"]) + " / "
                        + str(route["total"]) + " seats free.")
        self.cancel_msg_label.configure(fg=GREEN)
        self.cancel_msg.set(message)
        self.set_status(message)

    def _build_availability_page(self, parent):
        self.page_header(parent, "Seat Availability",
                         "Live view of seats on every route.")

        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(0, 12))

        self.avail_only = tk.BooleanVar(value=False)
        tk.Checkbutton(bar, text="Only routes with seats",
                       variable=self.avail_only,
                       command=self.refresh_availability,
                       bg=BG, fg=TEXT, font=("Segoe UI", 10),
                       activebackground=BG, selectcolor="white",
                       cursor="hand2").pack(side="left")

        self.secondary_button(bar, "Refresh", self.refresh_all).pack(side="right")

        self.avail_tree = self.make_table(
            parent,
            ("id", "journey", "seats", "capacity", "status"),
            {"id": "Route", "journey": "Journey", "seats": "Seats free",
             "capacity": "Capacity", "status": "Status"},
            {"id": 100, "journey": 340, "seats": 130, "capacity": 110,
             "status": 160},
        )

    def refresh_availability(self):
        for row in self.avail_tree.get_children():
            self.avail_tree.delete(row)

        only = self.avail_only.get()
        shown = 0
        for r in routes:
            if only and r["available"] == 0:
                continue
            shown += 1
            self.avail_tree.insert("", "end", values=(
                r["route_id"], journey(r), seat_text(r),
                str(r["total"]), status_text(r)))

        if shown == 0:
            self.avail_tree.insert("", "end",
                values=("—", "No routes to show", "", "", ""))

    def _build_report_page(self, parent):
        self.page_header(parent, "Booking Report",
                         "Confirmed revenue only — cancelled bookings are excluded.")

        cards = tk.Frame(parent, bg=BG)
        cards.pack(fill="x", pady=(0, 22))

        fields = [
            ("total",     "Total Bookings"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
            ("seats",     "Seats Reserved"),
            ("revenue",   "Confirmed Revenue"),
            ("full",      "Fully Booked Routes"),
        ]

        self.report_vars = {}
        for i, (key, label) in enumerate(fields):
            card = tk.Frame(cards, bg=CARD, padx=22, pady=16,
                            highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=i // 3, column=i % 3, sticky="nsew",
                      padx=6, pady=6)

            tk.Label(card, text=label, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w")

            var = tk.StringVar(value="0")
            tk.Label(card, textvariable=var, bg=CARD, fg=TEXT,
                     font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(4, 0))
            self.report_vars[key] = var

        for i in range(3):
            cards.columnconfigure(i, weight=1)

        tk.Label(parent, text="Confirmed bookings by route",
                 bg=BG, fg=TEXT, font=("Segoe UI", 12, "bold")
                 ).pack(anchor="w", pady=(0, 8))

        self.report_tree = self.make_table(
            parent,
            ("id", "journey", "seats", "revenue"),
            {"id": "Route", "journey": "Journey",
             "seats": "Seats booked", "revenue": "Revenue"},
            {"id": 100, "journey": 380, "seats": 140, "revenue": 180},
        )

    def refresh_report(self):
        total = len(bookings)
        confirmed = 0
        cancelled = 0
        reserved = 0
        revenue = 0

        for b in bookings:
            if b["status"] == "Confirmed":
                confirmed += 1
                reserved += b["seats"]
                revenue += b["fare"]
            else:
                cancelled += 1

        fully_booked = 0
        for r in routes:
            if r["available"] == 0:
                fully_booked += 1

        self.report_vars["total"].set(str(total))
        self.report_vars["confirmed"].set(str(confirmed))
        self.report_vars["cancelled"].set(str(cancelled))
        self.report_vars["seats"].set(str(reserved))
        self.report_vars["revenue"].set(money(revenue))
        self.report_vars["full"].set(str(fully_booked))

        for row in self.report_tree.get_children():
            self.report_tree.delete(row)

        any_row = False
        for r in routes:
            seats_on_route = 0
            money_on_route = 0
            for b in bookings:
                if b["status"] == "Confirmed" and b["route_id"] == r["route_id"]:
                    seats_on_route += b["seats"]
                    money_on_route += b["fare"]
            if seats_on_route > 0:
                any_row = True
                self.report_tree.insert("", "end", values=(
                    r["route_id"], journey(r), seats_on_route,
                    money(money_on_route)))

        if not any_row:
            self.report_tree.insert("", "end",
                values=("—", "No confirmed bookings yet", "", ""))

    def _build_schedule_page(self, parent):
        self.page_header(parent, "Route Schedule",
                         "Departures grouped by city (uses nested loops).")

        wrapper = tk.Frame(parent, bg=CARD,
                           highlightthickness=1, highlightbackground=BORDER)
        wrapper.pack(fill="both", expand=True)

        self.schedule_text = tk.Text(wrapper, font=("Consolas", 11),
                                     bg=CARD, fg=TEXT,
                                     relief="flat", bd=0,
                                     padx=22, pady=18)
        scroll = ttk.Scrollbar(wrapper, orient="vertical",
                               command=self.schedule_text.yview)
        self.schedule_text.configure(yscrollcommand=scroll.set)

        self.schedule_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def refresh_schedule(self):
        self.schedule_text.configure(state="normal")
        self.schedule_text.delete("1.0", "end")

        # configure tag once before use
        self.schedule_text.tag_configure("city", foreground=ACCENT,
                                         font=("Consolas", 11, "bold"))

        for city in cities:
            self.schedule_text.insert("end", city.upper() + "\n", "city")

            found = False
            for r in routes:
                if r["departure"].lower() != city.lower():
                    continue
                found = True
                self.schedule_text.insert(
                    "end",
                    "   " + r["route_id"] + "   →   " + r["destination"]
                    + "   |   " + r["time"] + "\n")
            if not found:
                self.schedule_text.insert("end", "   No scheduled departures.\n")
            self.schedule_text.insert("end", "\n")

        self.schedule_text.configure(state="disabled")

    def refresh_all(self):
        self.refresh_routes()
        self.refresh_availability()
        self.refresh_bookings()
        self.refresh_cancel_options()
        self.refresh_report()
        self.refresh_schedule()
        self.refresh_route_combo()

if __name__ == "__main__":
    App().mainloop()