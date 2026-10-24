SUPPORTED_CITIES = (
    "Karachi",
    "Hyderabad",
    "Sukkur",
    "Mirpur Khas",
    "Lahore",
)

routes = [
    {
        "route_id": "R101",
        "departure": "Karachi",
        "destination": "Hyderabad",
        "departure_time": "08:00 AM",
        "fare": 1200,
        "total_seats": 40,
        "available_seats": 40,
    },
    {
        "route_id": "R102",
        "departure": "Karachi",
        "destination": "Sukkur",
        "departure_time": "09:30 AM",
        "fare": 2000,
        "total_seats": 36,
        "available_seats": 36,
    },
    {
        "route_id": "R103",
        "departure": "Hyderabad",
        "destination": "Mirpur Khas",
        "departure_time": "11:00 AM",
        "fare": 800,
        "total_seats": 32,
        "available_seats": 32,
    },
    {
        "route_id": "R104",
        "departure": "Karachi",
        "destination": "Lahore",
        "departure_time": "07:00 PM",
        "fare": 5000,
        "total_seats": 45,
        "available_seats": 45,
    },
    {
        "route_id": "R105",
        "departure": "Sukkur",
        "destination": "Hyderabad",
        "departure_time": "02:00 PM",
        "fare": 1500,
        "total_seats": 30,
        "available_seats": 30,
    },
]

bookings = []

issued_ids = set()
next_booking_number = 1001


def money(amount):
    """Format a rupee amount, e.g. 2400 -> 'Rs.2,400'."""
    return "Rs." + format(amount, ",")


def parse_positive_int(text):
    """Return a positive int, or None if the text is not a positive integer."""
    try:
        value = int(text.strip())
    except ValueError:
        return None
    if value <= 0:
        return None
    return value


def find_route(route_id):
    """Return the route dictionary for an ID (case-insensitive), or None."""
    wanted = route_id.strip().lower()
    for route in routes:
        if route["route_id"].lower() == wanted:
            return route
    return None


def generate_booking_id():
    """Issue a unique booking ID after checking the issued_ids set."""
    global next_booking_number
    while True:
        candidate = "B" + str(next_booking_number)
        next_booking_number += 1
        if candidate not in issued_ids:
            issued_ids.add(candidate)
            return candidate


def route_status(route):
    """Classify a route's seat state."""
    if route["available_seats"] == 0:
        return "Fully Booked"
    if route["available_seats"] == route["total_seats"]:
        return "Available"
    return "Partially Booked"


def print_routes_table(route_list):
    """Print a route table with a sequence number (uses enumerate)."""
    print()
    print("{:<5}{:<8}{:<28}{:<12}{:<12}{:<16}".format(
        "No.", "Route", "Journey", "Depart", "Fare", "Seats"))
    print("-" * 80)
    for index, route in enumerate(route_list, start=1):
        journey = route["departure"] + " - " + route["destination"]
        if route["available_seats"] == 0:
            seat_text = "Fully Booked"
        else:
            seat_text = "{}/{}".format(route["available_seats"], route["total_seats"])
        print("{:<5}{:<8}{:<28}{:<12}{:<12}{:<16}".format(
            index,
            route["route_id"],
            journey,
            route["departure_time"],
            money(route["fare"]),
            seat_text,
        ))
    print("-" * 80)


def show_menu():
    print()
    print("SMART BUS RESERVATION SYSTEM")
    print("=" * 30)
    print("1. View Available Routes")
    print("2. Search for a Route")
    print("3. Book a Ticket")
    print("4. View My Bookings")
    print("5. Cancel a Booking")
    print("6. View Seat Availability")
    print("7. Generate Booking Report")
    print("8. View Route Schedule")
    print("9. Exit")
    print("=" * 30)


def view_routes():
    choice = input("Show only routes with seats available? (y/n): ").strip().lower()
    available_only = choice.startswith("y")

    print("\nAVAILABLE BUS ROUTES")
    print("{:<5}{:<8}{:<28}{:<12}{:<12}{:<16}".format(
        "No.", "Route", "Journey", "Depart", "Fare", "Seats"))
    print("-" * 80)

    shown = 0
    for index, route in enumerate(routes, start=1):
        # continue: skip fully booked routes when the filter is on
        if available_only and route["available_seats"] == 0:
            continue

        journey = route["departure"] + " - " + route["destination"]
        if route["available_seats"] == 0:
            seat_text = "Fully Booked"
        else:
            seat_text = "{}/{}".format(route["available_seats"], route["total_seats"])

        print("{:<5}{:<8}{:<28}{:<12}{:<12}{:<16}".format(
            index, route["route_id"], journey,
            route["departure_time"], money(route["fare"]), seat_text))
        shown += 1

    print("-" * 80)
    if shown == 0:
        print("No routes with seats available right now.")


def search_route():
    term = input("Enter route ID, departure city, or destination city: ").strip()
    if term == "":
        print("Search term cannot be empty.")
        return

    key = term.lower()
    matches = []

    # for-else: the else block runs only if the loop finishes without break.
    for route in routes:
        if route["route_id"].lower() == key:
            matches.append(route)
            break  # a route ID is unique, so stop searching
        if key in route["departure"].lower() or key in route["destination"].lower():
            matches.append(route)
    else:
        if not matches:
            print('No routes matched "{}".'.format(term))
            return

    print("\nSEARCH RESULTS")
    for route in matches:
        print("  {} | {} - {} | {} | {} | {} of {} seats free".format(
            route["route_id"],
            route["departure"],
            route["destination"],
            route["departure_time"],
            money(route["fare"]),
            route["available_seats"],
            route["total_seats"],
        ))
    print("{} route(s) found.".format(len(matches)))


def book_ticket():
    print("\nBOOK A TICKET")

    # --- validate everything first; change no state until all checks pass ---
    name = input("Passenger name: ").strip()
    if name == "":
        print("Booking rejected: passenger name cannot be empty.")
        return

    age = parse_positive_int(input("Passenger age: "))
    if age is None:
        print("Booking rejected: age must be a positive whole number.")
        return

    route = find_route(input("Route ID: "))
    if route is None:
        print("Booking rejected: that route ID does not exist.")
        return

    seats = parse_positive_int(input("Number of seats: "))
    if seats is None:
        print("Booking rejected: seat quantity must be a positive whole number.")
        return

    if seats > route["available_seats"]:
        print("Booking rejected: only {} seat(s) available on {}.".format(
            route["available_seats"], route["route_id"]))
        return

    booking_id = generate_booking_id()
    total_fare = route["fare"] * seats

    bookings.append({
        "booking_id": booking_id,
        "passenger_name": name,
        "passenger_age": age,
        "route_id": route["route_id"],
        "seats": seats,
        "total_fare": total_fare,
        "status": "Confirmed",
    })

    route["available_seats"] -= seats

    print("\nBOOKING CONFIRMED")
    print("  Booking ID : {}".format(booking_id))
    print("  Passenger  : {} (age {})".format(name, age))
    print("  Route      : {} | {} - {} | {}".format(
        route["route_id"], route["departure"], route["destination"],
        route["departure_time"]))
    print("  Seats      : {}".format(seats))
    print("  Total fare : {}".format(money(total_fare)))
    print("  Seats left : {} of {}".format(
        route["available_seats"], route["total_seats"]))


def view_bookings():
    print("\nALL BOOKINGS")
    if len(bookings) == 0:
        print("No bookings found.")
        return

    for index, booking in enumerate(bookings, start=1):
        route = find_route(booking["route_id"])
        if route is None:
            journey = booking["route_id"]
        else:
            journey = "{} - {}".format(route["departure"], route["destination"])
        print("  {}. {} | {} (age {}) | {} | {} seat(s) | {} | {}".format(
            index,
            booking["booking_id"],
            booking["passenger_name"],
            booking["passenger_age"],
            journey,
            booking["seats"],
            money(booking["total_fare"]),
            booking["status"],
        ))


def cancel_booking():
    booking_id = input("Enter booking ID to cancel: ").strip().upper()

    found = None
    for booking in bookings:
        if booking["booking_id"] == booking_id:
            found = booking
            break

    if found is None:
        print("Booking {} not found. Nothing was changed.".format(booking_id))
        return

    if found["status"] == "Cancelled":
        print("Booking {} is already cancelled. No seats were restored.".format(booking_id))
        return

    route = find_route(found["route_id"])

    # Status change and seat restoration happen together, exactly once.
    found["status"] = "Cancelled"
    if route is not None:
        route["available_seats"] += found["seats"]

    print("Booking {} has been cancelled.".format(booking_id))
    print("Seats restored: {}".format(found["seats"]))
    if route is not None:
        print("Route {} available seats: {} of {}".format(
            route["route_id"], route["available_seats"], route["total_seats"]))

def view_availability():
    choice = input("Show only routes with seats available? (y/n): ").strip().lower()
    available_only = choice.startswith("y")

    print("\nSEAT AVAILABILITY")
    print("{:<8}{:<28}{:<12}{:<18}{:<16}".format(
        "Route", "Journey", "Seats", "Status", "Capacity"))
    print("-" * 82)

    shown = 0
    for route in routes:
        if available_only and route["available_seats"] == 0:
            continue  # continue: skip fully booked routes
        journey = route["departure"] + " - " + route["destination"]
        print("{:<8}{:<28}{:<12}{:<18}{:<16}".format(
            route["route_id"],
            journey,
            "{}/{}".format(route["available_seats"], route["total_seats"]),
            route_status(route),
            str(route["total_seats"]),
        ))
        shown += 1

    print("-" * 82)
    if shown == 0:
        print("No routes with seats available right now.")


def generate_report():
    total_bookings = len(bookings)
    confirmed_count = 0
    cancelled_count = 0
    reserved_seats = 0
    confirmed_revenue = 0

    for booking in bookings:
        if booking["status"] == "Confirmed":
            confirmed_count += 1
            reserved_seats += booking["seats"]
            confirmed_revenue += booking["total_fare"]
        else:
            cancelled_count += 1

    fully_booked_routes = 0
    for route in routes:
        if route["available_seats"] == 0:
            fully_booked_routes += 1

    print("\nBOOKING REPORT")
    print("Total bookings created: {}".format(total_bookings))
    print("Confirmed bookings: {}".format(confirmed_count))
    print("Cancelled bookings: {}".format(cancelled_count))
    print("Seats currently reserved: {}".format(reserved_seats))
    print("Confirmed revenue: {}".format(money(confirmed_revenue)))
    print("Fully booked routes: {}".format(fully_booked_routes))

    print("\nCONFIRMED BOOKINGS BY ROUTE")
    any_confirmed = False
    for route in routes:
        route_seats = 0
        route_revenue = 0
        for booking in bookings:
            if booking["status"] == "Confirmed" and booking["route_id"] == route["route_id"]:
                route_seats += booking["seats"]
                route_revenue += booking["total_fare"]
        if route_seats > 0:
            any_confirmed = True
            print("  {} {} - {}: {} seat(s), {}".format(
                route["route_id"], route["departure"], route["destination"],
                route_seats, money(route_revenue)))
    if not any_confirmed:
        print("  No confirmed bookings yet.")


def show_schedule():
    print("\nROUTE SCHEDULE BY DEPARTURE CITY")

    # Outer loop over cities, inner loop over routes.
    for city in SUPPORTED_CITIES:
        print("\n{}".format(city))
        found = False
        for route in routes:
            if route["departure"].lower() != city.lower():
                continue  # continue: only print matching departures
            found = True
            print("  {} -> {} | {}".format(
                route["route_id"], route["destination"], route["departure_time"]))
        if not found:
            print("  No scheduled departures.")

def main():
    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            view_routes()
        elif choice == "2":
            search_route()
        elif choice == "3":
            book_ticket()
        elif choice == "4":
            view_bookings()
        elif choice == "5":
            cancel_booking()
        elif choice == "6":
            view_availability()
        elif choice == "7":
            generate_report()
        elif choice == "8":
            show_schedule()
        elif choice == "9":
            print("Thank you for using the Smart Bus Reservation System. Goodbye!")
            break
        else:
            print('"{}" is not a valid choice. Enter a number from 1 to 9.'.format(choice))


if __name__ == "__main__":
    main()