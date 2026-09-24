# Personal Finance Management App — SQLAlchemy Implementation

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, ForeignKey,
    func, case, literal
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=False)
Base = declarative_base()


# ── Models ────────────────────────────────────────────────────────────────────

class CurrencyRate(Base):
    __tablename__ = 'currency_rates'
    currency        = Column(String, primary_key=True)
    conversion_rate = Column(Float,  nullable=False)

    def __repr__(self):
        return f"<CurrencyRate({self.currency}: {self.conversion_rate})>"


class Category(Base):
    __tablename__ = 'categories'
    category    = Column(String,  primary_key=True)
    description = Column(String,  nullable=False)
    percentage  = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<Category({self.category}: {self.percentage}%)>"


class PayingResource(Base):
    __tablename__ = 'paying_resources'
    id              = Column(Integer, primary_key=True)
    card_number     = Column(String)
    currency        = Column(String, ForeignKey('currency_rates.currency'), nullable=False)
    expiration_date = Column(String)

    def __repr__(self):
        return f"<PayingResource({self.id}: {self.card_number or 'Cash'} {self.currency})>"


class DailyLog(Base):
    __tablename__ = 'daily_logs'
    id          = Column(Integer, primary_key=True, autoincrement=True)
    date        = Column(String,  nullable=False)
    amount      = Column(Float,   nullable=False)
    currency    = Column(String,  ForeignKey('currency_rates.currency'), nullable=False)
    category    = Column(String,  ForeignKey('categories.category'),     nullable=False)
    state       = Column(String,  nullable=False)
    description = Column(String)
    source      = Column(Integer, ForeignKey('paying_resources.id'),     nullable=False)
    rationality = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<DailyLog({self.date} {self.state} {self.amount}{self.currency} [{self.category}])>"


# ── Create tables & session ───────────────────────────────────────────────────

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


# ── Insert data ───────────────────────────────────────────────────────────────

session.add_all([
    CurrencyRate(currency='USD', conversion_rate=1.0),
    CurrencyRate(currency='EUR', conversion_rate=1.08),
    CurrencyRate(currency='UAH', conversion_rate=0.024),
    CurrencyRate(currency='JPY', conversion_rate=0.0067),
])

session.add_all([
    Category(category='income',        description='Any income transaction: salary, freelance, gifts, refunds',                   percentage=0),
    Category(category='savings',       description='Money set aside for future goals, emergency fund, investments',              percentage=20),
    Category(category='food',          description='Groceries, dining out, coffee shops, food delivery',                        percentage=15),
    Category(category='housing',       description='Rent, mortgage, utilities, home maintenance and repairs',                   percentage=25),
    Category(category='transport',     description='Public transit, fuel, car maintenance, ride-sharing services',              percentage=8),
    Category(category='health',        description='Doctor visits, pharmacy, gym membership, mental health services',           percentage=5),
    Category(category='entertainment', description='Movies, games, streaming subscriptions, concerts, hobbies',                 percentage=5),
    Category(category='education',     description='Courses, books, tutoring, school supplies, workshops',                      percentage=5),
    Category(category='clothing',      description='Clothes, shoes, accessories, laundry and dry cleaning',                     percentage=4),
    Category(category='personal_care', description='Hygiene products, haircuts, skincare, cosmetics',                           percentage=3),
    Category(category='gifts',         description='Presents for others, charitable donations, holiday spending',               percentage=5),
    Category(category='miscellaneous', description='Anything that does not fit other categories: fees, fines, unexpected costs', percentage=5),
])

session.add_all([
    PayingResource(id=1, card_number='4111-1111-1111-1234', currency='USD', expiration_date='2027-09'),
    PayingResource(id=2, card_number='5200-8282-8282-5678', currency='EUR', expiration_date='2026-12'),
    PayingResource(id=3, card_number='4000-1234-5678-9012', currency='UAH', expiration_date='2028-03'),
    PayingResource(id=4, card_number='3530-1113-3330-0000', currency='JPY', expiration_date='2027-06'),
    PayingResource(id=5, card_number='4916-3388-2200-7749', currency='USD', expiration_date='2026-08'),
    PayingResource(id=6, card_number=None, currency='USD', expiration_date=None),
    PayingResource(id=7, card_number=None, currency='EUR', expiration_date=None),
    PayingResource(id=8, card_number=None, currency='UAH', expiration_date=None),
    PayingResource(id=9, card_number=None, currency='JPY', expiration_date=None),
])
session.commit()

session.add_all([
    # Income
    DailyLog(date='2025-01-05', amount=3200.00, currency='USD', category='income',        state='income',  description='Monthly salary',                          source=1, rationality=1),
    DailyLog(date='2025-01-12', amount=500.00,  currency='EUR', category='income',        state='income',  description='Freelance web design project',            source=2, rationality=1),
    DailyLog(date='2025-01-20', amount=45000.00,currency='UAH', category='income',        state='income',  description='Part-time tutoring payout',               source=3, rationality=1),
    DailyLog(date='2025-01-28', amount=150.00,  currency='USD', category='income',        state='income',  description='Birthday gift from grandma',              source=6, rationality=1),
    # Food
    DailyLog(date='2025-01-03', amount=62.40,   currency='USD', category='food',          state='expense', description='Weekly groceries at Walmart',             source=1, rationality=1),
    DailyLog(date='2025-01-08', amount=34.50,   currency='USD', category='food',          state='expense', description='Dinner with friends at restaurant',       source=1, rationality=0),
    DailyLog(date='2025-01-14', amount=1200.00, currency='UAH', category='food',          state='expense', description='Groceries from local market',             source=3, rationality=1),
    DailyLog(date='2025-01-19', amount=2500.00, currency='JPY', category='food',          state='expense', description='Sushi takeout',                           source=4, rationality=1),
    DailyLog(date='2025-01-25', amount=18.90,   currency='USD', category='food',          state='expense', description='Coffee and pastry',                       source=6, rationality=0),
    # Housing
    DailyLog(date='2025-01-01', amount=950.00,  currency='USD', category='housing',       state='expense', description='Monthly rent payment',                    source=1, rationality=1),
    DailyLog(date='2025-01-15', amount=85.00,   currency='USD', category='housing',       state='expense', description='Electricity and water bill',              source=5, rationality=1),
    # Transport
    DailyLog(date='2025-01-06', amount=45.00,   currency='USD', category='transport',     state='expense', description='Monthly metro pass',                      source=6, rationality=1),
    DailyLog(date='2025-01-18', amount=28.50,   currency='EUR', category='transport',     state='expense', description='Uber ride to airport',                    source=2, rationality=1),
    DailyLog(date='2025-01-22', amount=600.00,  currency='UAH', category='transport',     state='expense', description='Taxi across city',                        source=8, rationality=0),
    # Health
    DailyLog(date='2025-01-10', amount=120.00,  currency='USD', category='health',        state='expense', description='Doctor visit copay',                      source=1, rationality=1),
    DailyLog(date='2025-01-17', amount=35.00,   currency='USD', category='health',        state='expense', description='Pharmacy — cold medicine',                source=6, rationality=1),
    DailyLog(date='2025-01-24', amount=50.00,   currency='USD', category='health',        state='expense', description='Monthly gym membership',                  source=5, rationality=1),
    # Entertainment
    DailyLog(date='2025-01-07', amount=15.99,   currency='USD', category='entertainment', state='expense', description='Netflix subscription',                    source=1, rationality=1),
    DailyLog(date='2025-01-13', amount=45.00,   currency='EUR', category='entertainment', state='expense', description='Concert tickets',                         source=2, rationality=0),
    DailyLog(date='2025-01-21', amount=9.99,    currency='USD', category='entertainment', state='expense', description='Spotify premium',                         source=5, rationality=1),
    DailyLog(date='2025-01-29', amount=60.00,   currency='USD', category='entertainment', state='expense', description='Video game purchase',                     source=1, rationality=0),
    # Education
    DailyLog(date='2025-01-04', amount=29.99,   currency='USD', category='education',     state='expense', description='Udemy course on Python',                  source=1, rationality=1),
    DailyLog(date='2025-01-16', amount=42.00,   currency='EUR', category='education',     state='expense', description='Programming textbook',                    source=2, rationality=1),
    # Clothing
    DailyLog(date='2025-01-09', amount=89.00,   currency='USD', category='clothing',      state='expense', description='Winter jacket on sale',                   source=1, rationality=1),
    DailyLog(date='2025-01-26', amount=3500.00, currency='UAH', category='clothing',      state='expense', description='New pair of boots',                       source=3, rationality=0),
    # Personal care
    DailyLog(date='2025-01-11', amount=25.00,   currency='USD', category='personal_care', state='expense', description='Haircut',                                 source=6, rationality=1),
    DailyLog(date='2025-01-23', amount=18.50,   currency='USD', category='personal_care', state='expense', description='Skincare products',                       source=1, rationality=1),
    # Gifts
    DailyLog(date='2025-01-15', amount=75.00,   currency='USD', category='gifts',         state='expense', description='Birthday present for a friend',           source=1, rationality=1),
    # Savings
    DailyLog(date='2025-01-30', amount=400.00,  currency='USD', category='savings',       state='expense', description='Monthly transfer to savings account',     source=1, rationality=1),
    # Miscellaneous
    DailyLog(date='2025-01-27', amount=150.00,  currency='USD', category='miscellaneous', state='expense', description='Phone screen repair',                     source=5, rationality=1),
])
session.commit()


# ── Queries ───────────────────────────────────────────────────────────────────

# ── Query 1: Total income and total expenses for January 2025 in USD ──────────
# Joins daily_logs → currency_rates; WHERE restricts to the target month and
# GROUP BY state produces exactly two rows (income / expense).
print("=" * 70)
print("QUERY 1  Total income and expenses for January 2025 (USD)")
print("=" * 70)

q1 = (
    session.query(
        DailyLog.state,
        func.round(func.sum(DailyLog.amount * CurrencyRate.conversion_rate), 2).label('total_usd'),
    )
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.date >= '2025-01-01', DailyLog.date < '2025-02-01')
    .group_by(DailyLog.state)
    .all()
)
for row in q1:
    print(row)


# ── Query 2: Categories where spending exceeded the planned budget ─────────────
# Step 1: compute total monthly income as a scalar (one SQLAlchemy query).
# Step 2: aggregate expenses per category in a subquery.
# Step 3: join with categories and filter WHERE spent > planned, entirely in SQL.
print("\n" + "=" * 70)
print("QUERY 2  Categories over budget in January 2025")
print("=" * 70)

total_income = (
    session.query(func.sum(DailyLog.amount * CurrencyRate.conversion_rate))
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'income', DailyLog.date >= '2025-01-01', DailyLog.date < '2025-02-01')
    .scalar()
)

spending_sq = (
    session.query(
        DailyLog.category.label('category'),
        func.sum(DailyLog.amount * CurrencyRate.conversion_rate).label('spent_usd'),
    )
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense', DailyLog.date >= '2025-01-01', DailyLog.date < '2025-02-01')
    .group_by(DailyLog.category)
    .subquery()
)

q2 = (
    session.query(
        spending_sq.c.category,
        func.round(spending_sq.c.spent_usd, 2).label('spent_usd'),
        Category.percentage.label('planned_pct'),
        func.round(total_income * Category.percentage / 100.0, 2).label('planned_usd'),
        func.round(spending_sq.c.spent_usd - total_income * Category.percentage / 100.0, 2).label('over_by_usd'),
    )
    .select_from(spending_sq)
    .join(Category, spending_sq.c.category == Category.category)
    .filter(spending_sq.c.spent_usd > total_income * Category.percentage / 100.0)
    .order_by(func.round(spending_sq.c.spent_usd - total_income * Category.percentage / 100.0, 2).desc())
    .all()
)
for row in q2:
    print(row)


# ── Query 3: Category with the highest total spending (all time) ──────────────
# Aggregates all expense rows by category; LIMIT 1 inside the database returns
# exactly the top spender without pulling all rows into Python.
print("\n" + "=" * 70)
print("QUERY 3  Category with the most spending (all time)")
print("=" * 70)

q3 = (
    session.query(
        DailyLog.category,
        func.round(func.sum(DailyLog.amount * CurrencyRate.conversion_rate), 2).label('total_spent_usd'),
    )
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense')
    .group_by(DailyLog.category)
    .order_by(func.sum(DailyLog.amount * CurrencyRate.conversion_rate).desc())
    .first()
)
print(q3)


# ── Query 4: Irrational spending — summary and per-transaction detail ─────────
# Total expenses are computed first (scalar) so the percentage is calculated
# entirely inside the database; no Python-side arithmetic on result rows.
print("\n" + "=" * 70)
print("QUERY 4  Irrational spending summary and detail")
print("=" * 70)

total_expense = (
    session.query(func.sum(DailyLog.amount * CurrencyRate.conversion_rate))
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense')
    .scalar()
)

q4_summary = (
    session.query(
        func.round(func.sum(DailyLog.amount * CurrencyRate.conversion_rate), 2).label('irrational_total_usd'),
        func.round(
            func.sum(DailyLog.amount * CurrencyRate.conversion_rate) * 100.0 / total_expense,
        2).label('irrational_pct'),
    )
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense', DailyLog.rationality == 0)
    .one()
)
print("Summary:", q4_summary)

q4_detail = (
    session.query(
        DailyLog.date,
        DailyLog.description,
        DailyLog.category,
        func.round(DailyLog.amount * CurrencyRate.conversion_rate, 2).label('amount_usd'),
    )
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense', DailyLog.rationality == 0)
    .order_by(func.round(DailyLog.amount * CurrencyRate.conversion_rate, 2).desc())
    .all()
)
print("Detail:")
for row in q4_detail:
    print(" ", row)


# ── Query 5: Spending by payment source ───────────────────────────────────────
# CASE expression inside the database labels each row as 'Cash (CCY)' or the
# card number; grouping and ordering happen entirely in SQL.
print("\n" + "=" * 70)
print("QUERY 5  Spending by payment source")
print("=" * 70)

payment_label = case(
    (PayingResource.card_number == None, literal('Cash (') + PayingResource.currency + literal(')')),
    else_=PayingResource.card_number,
).label('payment_source')

q5 = (
    session.query(
        payment_label,
        PayingResource.currency.label('source_currency'),
        func.count(DailyLog.id).label('num_transactions'),
        func.round(func.sum(DailyLog.amount * CurrencyRate.conversion_rate), 2).label('total_spent_usd'),
    )
    .join(PayingResource, DailyLog.source == PayingResource.id)
    .join(CurrencyRate, DailyLog.currency == CurrencyRate.currency)
    .filter(DailyLog.state == 'expense')
    .group_by(DailyLog.source)
    .order_by(func.sum(DailyLog.amount * CurrencyRate.conversion_rate).desc())
    .all()
)
for row in q5:
    print(row)

session.close()
