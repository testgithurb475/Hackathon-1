# Smart Bus Ticket Booking & Reservation System

A beginner-friendly Python 3 console application that manages bus routes,
seat reservations, cancellations, schedules, and reports.

## Requirements
- Python 3.x
- No external libraries

## How to run
    python main.py

## Menu
1. View Available Routes - list routes, seats, and Fully Booked status
2. Search for a Route - by route ID, departure city, or destination city
3. Book a Ticket - validate details, issue a booking ID, update seats
4. View My Bookings - all records, including Cancelled ones
5. Cancel a Booking - Confirmed bookings only; seats restored once
6. View Seat Availability - Available / Partially Booked / Fully Booked
7. Generate Booking Report - counts, reserved seats, confirmed revenue
8. View Route Schedule - departures grouped by city (nested loops)
9. Exit

## Sample workflow
1. Choose 3, enter `Ahmed`, age `24`, route `R101`, seats `2`.
   Booking `B1001` is confirmed for Rs.2,400 and R101 drops to 38 seats.
2. Choose 5, enter `B1001`. Status becomes Cancelled and 2 seats return.
3. Choose 5 again with `B1001`. Rejected - seats are not restored twice.
4. Choose 7. Cancelled bookings are counted but excluded from revenue.

## Storage limitation
All routes and bookings are held **in memory only**. Nothing is written to
disk, so every record is lost when the program closes. Persistence, payments,
and external services are out of scope.

## Constraints
Console interface only, built-in Python only, no database, no GUI.

## Notes
The PRD's menu screenshot shows 8 items, but Feature 10 (Route Schedule)
must be reachable, so it was added as option 8 and Exit moved to 9.