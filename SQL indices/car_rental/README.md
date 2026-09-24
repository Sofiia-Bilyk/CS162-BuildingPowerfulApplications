# Car Rental and Fleet Management Platform

## Schema Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                          Branch                             │
│  branch_id PK │ name │ city │ state │ phone │ address       │
└──────┬──────────────────────────────────┬────────────────────┘
       │ (home branch)                    │ (pickup / return)
       │                                  │
       ▼                                  ▼
┌───────────────────────┐      ┌──────────────────────────────┐
│        Vehicle        │      │         Reservation          │
│  vehicle_id   PK      │◄─────│  reservation_id  PK         │
│  branch_id    FK──────┘      │  customer_id     FK ──────┐  │
│  make, model, year    │      │  vehicle_id      FK       │  │
│  license_plate        │      │  pickup_branch   FK       │  │
│  category             │      │  return_branch   FK       │  │
│  daily_rate           │      │  start_date, end_date     │  │
│  status               │      │  status, total_cost       │  │
│  current_mileage      │      └──────┬───────────┬────────┘  │
└──────┬────────────────┘             │           │           │
       │                              │           │           │
       │                              ▼           ▼           │
       │                    ┌──────────┐  ┌──────────────┐   │
       │                    │  Rental  │  │   Payment    │   │
       │                    │──────────│  │──────────────│   │
       │                    │rental_id │  │ payment_id   │   │
       │                    │reserv FK │  │ reserv FK    │   │
       │                    │pickup_tm │  │ amount       │   │
       │                    │return_tm │  │ payment_date │   │
       │                    │mileages  │  │ method       │   │
       │                    │extra_chg │  │ status       │   │
       │                    └──────────┘  └──────────────┘   │
       │                                                      │
       ▼                                              ┌───────┘
┌─────────────────────────┐                  ┌────────▼──────────┐
│   MaintenanceRecord     │                  │     Customer      │
│  record_id     PK       │                  │  customer_id  PK  │
│  vehicle_id    FK───────┘                  │  first_name       │
│  service_date           │                  │  last_name        │
│  service_type, cost     │                  │  email (unique)   │
│  mileage_at_service     │                  │  phone            │
│  next_service_mileage   │                  │  drivers_license  │
│  technician             │                  │  license_expiry   │
└─────────────────────────┘                  └───────────────────┘
```

## Tables (7)

| Table | Purpose |
|---|---|
| `Branch` | Physical rental locations (LAX, SFO, San Diego) |
| `Vehicle` | Individual cars in the fleet, each assigned a home branch |
| `Customer` | Registered renters |
| `Reservation` | A booking linking customer + vehicle + dates + branches |
| `Rental` | Operational record created when the customer physically picks up the car |
| `MaintenanceRecord` | Service history per vehicle; `next_service_mileage` drives overdue alerts |
| `Payment` | Financial transaction per reservation |

## Indexes

| Index | Columns | Query Benefiting |
|---|---|---|
| `idx_vehicle_branch_status` | `(branch_id, status)` | Q1 – availability filter |
| `idx_maintenance_vehicle_date` | `(vehicle_id, service_date)` | Q3 – most recent service record |
| `idx_reservation_vehicle_dates` | `(vehicle_id, start_date, end_date)` | Q1 – overlap detection |
| `idx_reservation_customer` | `(customer_id)` | Q4 – customer history |
| `idx_reservation_branch_date` | `(pickup_branch, start_date)` | Q2 – branch revenue |
| `idx_reservation_status` | `(status)` | Operational filtering |
| `idx_payment_reservation` | `(reservation_id)` | Q2, Q4 – payment joins |

## Questions & Queries

### Q1 — Which vehicles are available at a branch for given dates?
**Why it matters:** This is the primary booking query. Staff or the website UI call it every time a customer requests a quote or reservation.

**Logic:** Filter `Vehicle` to the target branch and exclude `maintenance`/`retired` units, then subtract any vehicle that already has a `confirmed` or `active` reservation whose date range overlaps the requested window. The overlap test is:
```
existing.start_date < requested_end  AND  existing.end_date > requested_start
```
This correctly handles partial overlaps from either direction.

**Sample output (LAX, 5–8 March 2026):**
```
vehicle_id  make    model     category  daily_rate  license_plate
1           Toyota  Camry     economy   45.0        7ABC123
3           Ford    Explorer  suv       89.0        7GHI789
10          Tesla   Model 3   luxury    175.0       7BCD890
2           Honda   Civic     compact   39.0        7DEF456
```

---

### Q2 — Total revenue per branch for a year
**Why it matters:** Management uses this for financial reporting and to evaluate whether a branch justifies its operating costs.

**Sample output (2025):**
```
branch              city           rentals  total_revenue
LAX Airport         Los Angeles    3        715.0
SFO Airport         San Francisco  1        447.0
Downtown San Diego  San Diego      2        410.0
```

---

### Q3 — Which vehicles are overdue for maintenance?
**Why it matters:** Pulling a car for service before breakdown prevents roadside incidents, insurance claims, and customer dissatisfaction. Fleet managers need a live alert list.

**Logic:** For each vehicle, find its most recent `MaintenanceRecord` using a correlated sub-query ordered by `service_date DESC LIMIT 1`. If `current_mileage >= next_service_mileage`, the vehicle is overdue. The `idx_maintenance_vehicle_date` covering index makes the sub-query a single B-tree seek per vehicle.

**Sample output:**
```
vehicle_id  make       model   license_plate  current_mileage  next_service_mileage  miles_overdue
1           Toyota     Camry   7ABC123        27500            26000                 1500
7           Chevrolet  Malibu  7STU901        33200            32000                 1200
```

---

### Q4 — Full rental history for a specific customer
**Why it matters:** Customer service reps need this when handling damage disputes, processing loyalty rewards, or answering billing questions without putting the customer on hold.

**Sample output (Customer 1 – Alice Johnson):**
```
reservation_id  make       model   category  start_date  end_date    status     total_cost  extra_charges  payment_method
4               Chevrolet  Malibu  midsize   2025-07-04  2025-07-08  completed  220.0       25.0           credit_card
1               Toyota     Camry   economy   2025-06-01  2025-06-05  completed  180.0       0.0            credit_card
```

---

### Q5 — Which vehicle category is most popular?
**Why it matters:** Fleet planning — knowing which segments drive the most demand (and revenue) informs purchasing decisions when the fleet needs to grow or be refreshed.

**Sample output:**
```
category  total_reservations  avg_rental_cost  total_revenue
luxury    3                   581.0            1743.0
suv       3                   362.33           1087.0
economy   3                   153.33           460.0
compact   1                   234.0            234.0
midsize   1                   220.0            220.0
```
Luxury and SUV tie on reservation count but luxury generates more than 1.5× the revenue per booking.
