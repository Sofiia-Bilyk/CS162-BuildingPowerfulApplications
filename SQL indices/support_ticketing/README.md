# E-commerce Customer Support Ticketing System

## Schema Diagram

```
┌─────────────────────────────────┐        ┌──────────────────────┐
│           Customer              │        │       Product        │
│  customer_id  PK                │        │  product_id  PK      │
│  name, email (unique)           │        │  name, category      │
│  phone                          │        │  price, sku (unique) │
│  tier (standard/premium/vip)    │        └───────────┬──────────┘
│  joined_at                      │                    │
└──────┬──────────────────────────┘                    │
       │                                               │
       ▼                                               ▼
┌──────────────────────────┐             ┌─────────────────────────┐
│      CustomerOrder       │◄────────────│        OrderItem        │
│  order_id      PK        │             │  item_id    PK          │
│  customer_id   FK ───────┘             │  order_id   FK          │
│  order_date              │             │  product_id FK          │
│  total_amount            │             │  quantity               │
│  status                  │             │  unit_price             │
└──────────┬───────────────┘             └─────────────────────────┘
           │
           │ (optional — ticket may be account-level, not order-level)
           │
           ▼
┌──────────────────────────────────────────┐    ┌──────────────────┐
│                 Ticket                   │    │      Agent       │
│  ticket_id    PK                         │◄───│  agent_id  PK    │
│  customer_id  FK ────────────────────────┘    │  name, email     │
│  order_id     FK (nullable)              │    │  department      │
│  agent_id     FK (nullable) ─────────────┘    └──────────────────┘
│  subject, category, priority             │
│  status (open/in_progress/resolved)      │
│  created_at, resolved_at (nullable)      │
└───────────────────┬──────────────────────┘
                    │
                    ▼
          ┌─────────────────────────┐
          │      TicketMessage      │
          │  message_id  PK         │
          │  ticket_id   FK         │
          │  sender_type            │
          │  sender_id              │
          │  message                │
          │  sent_at                │
          └─────────────────────────┘
```

## Tables (7)

| Table | Purpose |
|---|---|
| `Customer` | Shoppers; `tier` field affects SLA priority |
| `Product` | Store catalogue; price stored here, snapshot stored in `OrderItem` |
| `CustomerOrder` | A purchase transaction (named to avoid the SQL keyword `ORDER`) |
| `OrderItem` | One row per product line per order; stores `unit_price` at purchase time |
| `Agent` | Support staff, grouped by `department` |
| `Ticket` | A support request; `order_id` and `agent_id` may be NULL |
| `TicketMessage` | Individual messages in the ticket thread; `sender_type` = `customer` or `agent` |

## Indexes

| Index | Columns | Query Benefiting |
|---|---|---|
| `idx_ticket_agent_status` | `(agent_id, status)` | Q1 – agent's open queue |
| `idx_ticket_customer_date` | `(customer_id, created_at)` | Q3 – customer ticket volume |
| `idx_ticket_category` | `(category)` | Q2 – resolution time by category |
| `idx_message_ticket_time` | `(ticket_id, sent_at)` | Q5 – message thread (covering index) |
| `idx_orderitem_product` | `(product_id)` | Q4 – product ticket analysis |
| `idx_orderitem_order` | `(order_id)` | Join accelerator |
| `idx_order_customer` | `(customer_id)` | Join accelerator |

`idx_message_ticket_time` is a **covering index** for Q5: the query needs `ticket_id` (WHERE), `sent_at` (ORDER BY), plus the other columns fetched from the table. The index node holds `ticket_id` and `sent_at`, so the sort step requires no table row fetches at all.

## Questions & Queries

### Q1 — What open tickets are in an agent's queue?
**Why it matters:** The first thing an agent does each morning is open their personal queue. The query must be instant even if the system holds millions of tickets.

**Index:** `idx_ticket_agent_status(agent_id, status)` navigates directly to the leaf block for `(agent_id=1, status='open')` — no scan of the full `Ticket` table.

**Sample output (Tom Baker, agent 1):**
```
ticket_id  customer       subject                                   category  priority
6          Sarah Connor   Wrong item delivered in my order          shipping  medium
1          Sarah Connor   Billing charge looks incorrect            billing   high
5          Jessica Davis  Return approved but refund not received   refund    high
```

---

### Q2 — Average resolution time per ticket category
**Why it matters:** Operations managers identify bottlenecks. If `refund` tickets average 56 hours but `general` tickets average 8 hours, staffing is misaligned.

**Logic:** `julianday()` converts ISO-8601 datetime strings to a floating-point day count. Subtracting `created_at` from `resolved_at` gives elapsed days; multiplying by 24 gives hours.

**Sample output:**
```
category   resolved_count  avg_hours_to_resolve
general    1               8.0
technical  1               23.0
billing    1               25.0
shipping   1               51.0
refund     1               56.0
```

---

### Q3 — Which customers have the most open tickets in the last 90 days?
**Why it matters:** A customer with 3+ open tickets in 90 days is a churn risk. Proactive outreach — a direct call from a senior agent — can recover the relationship before a public review is posted.

**Sample output:**
```
customer_id  name           tier      open_tickets
1            Sarah Connor   premium   2
2            John Smith     standard  1
3            Emily Chen     premium   1
5            Jessica Davis  vip       1
```

---

### Q4 — Which products generate the most support tickets?
**Why it matters:** The product team uses this to prioritise quality improvements. Wireless Headphones generating 5× more tickets than Yoga Mats signals a design or manufacturing defect.

**Logic:** `Ticket → CustomerOrder → OrderItem → Product`. A single ticket on a multi-item order counts each product in that order once (`COUNT(DISTINCT ticket_id)` ensures a ticket is not double-counted per product).

**Sample output:**
```
product               category     ticket_count
Wireless Headphones   Electronics  5
Laptop Stand          Electronics  3
Smart Watch           Electronics  2
Running Shoes         Footwear     1
Coffee Maker          Appliances   1
Yoga Mat              Sports       1
Protein Powder        Nutrition    1
```

---

### Q5 — Full conversation thread for a ticket
**Why it matters:** Agents must read the full history before responding. Asking a customer to repeat their problem is one of the top drivers of poor CSAT scores.

**Covering index:** `idx_message_ticket_time(ticket_id, sent_at)` contains `ticket_id` (used in WHERE) and `sent_at` (used in ORDER BY). Both fields are inside the index node itself, so SQLite satisfies the query without ever reading the actual `TicketMessage` table rows — the index is "covering" for this access pattern.

**Sample output (Ticket 3 — Emily's faulty headphones):**
```
sent_at           sender_type  sender_name  message
2026-02-18 10:05  customer     Emily Chen   My headphones have static noise in the left ear...
2026-02-18 11:30  agent        Lisa Park    Could you try resetting them by holding the power button...
2026-02-18 14:00  customer     Emily Chen   I tried that three times and the static is still there...
2026-02-19 09:15  agent        Lisa Park    I am escalating this to a replacement. Expect a prepaid label...
```
