"""
===============================================================================
 SALES / E-COMMERCE DATASET GENERATOR
 Generates a realistic sample dataset for the Power BI Dashboard project.
===============================================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# ── CONFIG ───────────────────────────────────────────────────────────────────
NUM_RECORDS = 5000
OUTPUT_RAW = os.path.join(os.path.dirname(__file__), "data", "raw_sales_data.csv")
SEED = 42

np.random.seed(SEED)
random.seed(SEED)

# ── REFERENCE DATA ───────────────────────────────────────────────────────────
CATEGORIES = {
    "Technology": {
        "sub": ["Phones", "Laptops", "Tablets", "Accessories", "Monitors"],
        "price_range": (50, 2500),
        "margin": (0.05, 0.25),
    },
    "Furniture": {
        "sub": ["Chairs", "Tables", "Desks", "Bookcases", "Storage"],
        "price_range": (30, 1500),
        "margin": (0.02, 0.20),
    },
    "Office Supplies": {
        "sub": ["Paper", "Binders", "Pens", "Envelopes", "Labels"],
        "price_range": (2, 200),
        "margin": (0.10, 0.45),
    },
    "Clothing": {
        "sub": ["Shirts", "Pants", "Jackets", "Shoes", "Accessories"],
        "price_range": (10, 500),
        "margin": (0.15, 0.55),
    },
}

REGIONS = {
    "West":    {"states": ["California", "Washington", "Oregon", "Nevada", "Arizona"], "weight": 0.32},
    "East":    {"states": ["New York", "Pennsylvania", "New Jersey", "Connecticut", "Massachusetts"], "weight": 0.28},
    "Central": {"states": ["Illinois", "Texas", "Ohio", "Michigan", "Minnesota"], "weight": 0.22},
    "South":   {"states": ["Florida", "Georgia", "Virginia", "North Carolina", "Tennessee"], "weight": 0.18},
}

SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SHIP_WEIGHTS = [0.55, 0.20, 0.15, 0.10]

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.31, 0.17]

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Emily", "Sophia",
    "Olivia", "Ava", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
]

CITIES = {
    "California": ["Los Angeles", "San Francisco", "San Diego", "Sacramento"],
    "Washington": ["Seattle", "Spokane", "Tacoma"],
    "Oregon": ["Portland", "Eugene", "Salem"],
    "Nevada": ["Las Vegas", "Reno"],
    "Arizona": ["Phoenix", "Tucson", "Mesa"],
    "New York": ["New York City", "Buffalo", "Rochester"],
    "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown"],
    "New Jersey": ["Newark", "Jersey City", "Trenton"],
    "Connecticut": ["Hartford", "New Haven", "Stamford"],
    "Massachusetts": ["Boston", "Worcester", "Springfield"],
    "Illinois": ["Chicago", "Aurora", "Naperville"],
    "Texas": ["Houston", "Dallas", "Austin", "San Antonio"],
    "Ohio": ["Columbus", "Cleveland", "Cincinnati"],
    "Michigan": ["Detroit", "Grand Rapids", "Ann Arbor"],
    "Minnesota": ["Minneapolis", "Saint Paul", "Rochester"],
    "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
    "Georgia": ["Atlanta", "Savannah", "Augusta"],
    "Virginia": ["Richmond", "Virginia Beach", "Norfolk"],
    "North Carolina": ["Charlotte", "Raleigh", "Durham"],
    "Tennessee": ["Nashville", "Memphis", "Knoxville"],
}


def generate_orders(n: int) -> pd.DataFrame:
    """Generate n order records with realistic distributions."""
    records = []
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range_days = (end_date - start_date).days

    customer_pool = [
        f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        for _ in range(350)
    ]

    region_names = list(REGIONS.keys())
    region_weights = [REGIONS[r]["weight"] for r in region_names]

    for i in range(1, n + 1):
        # Order metadata
        order_date = start_date + timedelta(days=random.randint(0, date_range_days))
        # Add seasonal spikes (Q4 holiday season)
        if random.random() < 0.15 and order_date.month not in [11, 12]:
            new_month = random.choice([11, 12])
            import calendar
            max_day = calendar.monthrange(order_date.year, new_month)[1]
            order_date = order_date.replace(month=new_month, day=min(order_date.day, max_day))

        order_id = f"ORD-{order_date.year}-{i:05d}"

        # Customer
        customer = random.choice(customer_pool)
        segment = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS, k=1)[0]

        # Region / Location
        region = random.choices(region_names, weights=region_weights, k=1)[0]
        state = random.choice(REGIONS[region]["states"])
        city = random.choice(CITIES[state])

        # Shipping
        ship_mode = random.choices(SHIP_MODES, weights=SHIP_WEIGHTS, k=1)[0]
        ship_days = {"Standard Class": random.randint(4, 7),
                     "Second Class": random.randint(3, 5),
                     "First Class": random.randint(1, 3),
                     "Same Day": 0}[ship_mode]
        ship_date = order_date + timedelta(days=ship_days)

        # Product
        category = random.choice(list(CATEGORIES.keys()))
        cat_info = CATEGORIES[category]
        sub_category = random.choice(cat_info["sub"])
        product_name = f"{sub_category} - Model {random.choice('ABCDEFGHIJKLMNOP')}{random.randint(100,999)}"

        # Financials
        quantity = random.randint(1, 12)
        unit_price = round(random.uniform(*cat_info["price_range"]), 2)
        discount = random.choice([0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30])
        sales = round(unit_price * quantity * (1 - discount), 2)
        margin = random.uniform(*cat_info["margin"])
        profit = round(sales * margin, 2)
        # Some orders lose money (returns / heavy discounts)
        if discount >= 0.25 and random.random() < 0.4:
            profit = -abs(profit) * random.uniform(0.3, 1.0)
            profit = round(profit, 2)

        shipping_cost = round(random.uniform(2, 50) * (1 if ship_mode != "Same Day" else 2.5), 2)

        records.append({
            "Order ID": order_id,
            "Order Date": order_date.strftime("%m/%d/%Y"),
            "Ship Date": ship_date.strftime("%Y-%m-%d"),  # intentionally different format
            "Ship Mode": ship_mode,
            "Customer ID": f"CUST-{abs(hash(customer)) % 10000:04d}",
            "Customer Name": customer,
            "Segment": segment,
            "City": city,
            "State": state,
            "Region": region,
            "Category": category,
            "Sub-Category": sub_category,
            "Product Name": product_name,
            "Quantity": quantity,
            "Unit Price": unit_price,
            "Discount": discount,
            "Sales": sales,
            "Profit": profit,
            "Shipping Cost": shipping_cost,
        })

    return pd.DataFrame(records)


def inject_data_quality_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Inject realistic data-quality problems for the cleaning script to fix."""
    df = df.copy()
    n = len(df)
    rng = np.random.default_rng(SEED)

    # 1. Null values (~3 % of rows across various columns)
    for col in ["Customer Name", "Sales", "Profit", "Region", "Category"]:
        mask = rng.random(n) < 0.03
        df.loc[mask, col] = np.nan

    # 2. Duplicate rows (~1 %)
    dup_idx = rng.choice(n, size=int(n * 0.01), replace=False)
    dups = df.iloc[dup_idx].copy()
    df = pd.concat([df, dups], ignore_index=True)

    # 3. Mixed date formats (already partially done in generator)
    # Some extra messy dates
    messy_idx = rng.choice(len(df), size=50, replace=False)
    for idx in messy_idx:
        try:
            d = pd.to_datetime(df.at[idx, "Order Date"])
            df.at[idx, "Order Date"] = d.strftime("%d-%b-%Y")  # e.g. 15-Jan-2023
        except Exception:
            pass

    # 4. Whitespace / casing issues in categorical columns
    noise_idx = rng.choice(len(df), size=80, replace=False)
    for idx in noise_idx:
        col = rng.choice(["Region", "Category", "Ship Mode"])
        val = df.at[idx, col]
        if pd.notna(val):
            transform = rng.choice(["upper", "lower", "space"])
            if transform == "upper":
                df.at[idx, col] = val.upper()
            elif transform == "lower":
                df.at[idx, col] = val.lower()
            else:
                df.at[idx, col] = f"  {val}  "

    # 5. Negative quantities (invalid)
    neg_idx = rng.choice(len(df), size=15, replace=False)
    df.loc[neg_idx, "Quantity"] = -abs(df.loc[neg_idx, "Quantity"])

    return df


def main():
    print("🔧  Generating raw sales dataset ...")
    os.makedirs(os.path.dirname(OUTPUT_RAW), exist_ok=True)

    df = generate_orders(NUM_RECORDS)
    df = inject_data_quality_issues(df)
    df.to_csv(OUTPUT_RAW, index=False)

    print(f"✅  Raw dataset saved → {OUTPUT_RAW}")
    print(f"    Rows : {len(df):,}")
    print(f"    Cols : {df.shape[1]}")
    print(f"    Nulls: {df.isnull().sum().sum()}")
    print(f"    Dupes: {df.duplicated().sum()}")


if __name__ == "__main__":
    main()
