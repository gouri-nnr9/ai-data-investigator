import os
import random
from datetime import datetime, timedelta

import numpy as np
import psycopg2
from faker import Faker
from dotenv import load_dotenv
from psycopg2.extras import execute_values


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

# Reproducible data.
# Running the script again with the same seed produces
# the same business world.
random.seed(42)
np.random.seed(42)

fake = Faker("en_IN")
Faker.seed(42)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31, 23, 59, 59)

NUM_CUSTOMERS = 5_000
NUM_PRODUCTS = 150
NUM_STORES = 8
NUM_ORDERS = 100_000

BATCH_SIZE = 5_000


# ---------------------------------------------------------
# BUSINESS CONFIGURATION
# ---------------------------------------------------------

REGIONS = {
    "North": [
        ("Delhi Central", "Delhi"),
        ("Chandigarh Hub", "Chandigarh"),
    ],
    "South": [
        ("Bengaluru Central", "Bengaluru"),
        ("Hyderabad Hub", "Hyderabad"),
    ],
    "West": [
        ("Mumbai Mall", "Mumbai"),
        ("Pune Central", "Pune"),
    ],
    "East": [
        ("Kolkata Hub", "Kolkata"),
        ("Bhubaneswar Store", "Bhubaneswar"),
    ],
}

CATEGORIES = {
    "Electronics": {
        "weight": 0.20,
        "price_range": (800, 40000),
    },
    "Fashion": {
        "weight": 0.20,
        "price_range": (300, 6000),
    },
    "Home": {
        "weight": 0.15,
        "price_range": (500, 15000),
    },
    "Grocery": {
        "weight": 0.20,
        "price_range": (100, 3000),
    },
    "Beauty": {
        "weight": 0.15,
        "price_range": (200, 5000),
    },
    "Sports": {
        "weight": 0.10,
        "price_range": (400, 12000),
    },
}

PAYMENT_METHODS = [
    "UPI",
    "Credit Card",
    "Debit Card",
    "Net Banking",
    "Wallet",
]

REFUND_REASONS = [
    "Damaged product",
    "Wrong item",
    "Late delivery",
    "Customer changed mind",
    "Product not as expected",
]


# ---------------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
    )


# ---------------------------------------------------------
# RESET DATABASE
# ---------------------------------------------------------

def reset_database(conn):
    """
    Useful while developing.
    WARNING: this deletes all data in these tables.
    """

    with conn.cursor() as cur:
        cur.execute(
            """
            TRUNCATE TABLE
                refunds,
                payments,
                order_items,
                orders,
                products,
                customers,
                stores
            RESTART IDENTITY CASCADE;
            """
        )

    conn.commit()
    print("Database reset complete.")


# ---------------------------------------------------------
# GENERATE STORES
# ---------------------------------------------------------

def generate_stores():
    stores = []

    store_id = 1

    for region, region_stores in REGIONS.items():

        for store_name, city in region_stores:

            stores.append(
                (

                    store_id,  
                    store_name,
                    region,
                    city,
                )
            )

            store_id += 1

    return stores


# ---------------------------------------------------------
# GENERATE PRODUCTS
# ---------------------------------------------------------

def generate_products():
    products = []

    product_names = {
        "Electronics": [
            "Wireless Headphones",
            "Bluetooth Speaker",
            "Smart Watch",
            "Mechanical Keyboard",
            "Wireless Mouse",
            "Power Bank",
            "USB-C Hub",
            "Webcam",
            "Gaming Controller",
            "Portable SSD",
        ],
        "Fashion": [
            "Running Shoes",
            "Casual Shirt",
            "Jeans",
            "Hoodie",
            "Sneakers",
            "T-Shirt",
            "Jacket",
            "Backpack",
            "Sunglasses",
        ],
        "Home": [
            "Coffee Maker",
            "Mixer Grinder",
            "Bedsheet",
            "Desk Lamp",
            "Storage Box",
            "Cookware Set",
            "Water Bottle",
            "Wall Clock",
        ],
        "Grocery": [
            "Rice",
            "Wheat Flour",
            "Cooking Oil",
            "Coffee",
            "Tea",
            "Dry Fruits",
            "Biscuits",
            "Pasta",
            "Cereal",
        ],
        "Beauty": [
            "Face Wash",
            "Moisturizer",
            "Shampoo",
            "Sunscreen",
            "Lip Balm",
            "Perfume",
            "Body Lotion",
        ],
        "Sports": [
            "Yoga Mat",
            "Dumbbells",
            "Cricket Bat",
            "Football",
            "Skipping Rope",
            "Resistance Bands",
            "Sports Shoes",
        ],
    }

    product_id = 1

    for category, config in CATEGORIES.items():

        for _ in range(NUM_PRODUCTS // len(CATEGORIES)):

            base_name = random.choice(product_names[category])

            product_name = f"{base_name} {random.choice(['Pro', 'Plus', 'Max', 'Lite', 'Classic'])}"

            min_price, max_price = config["price_range"]

            price = round(
                random.uniform(min_price, max_price),
                2,
            )

            # Roughly 55-75% of selling price.
            cost = round(
                price * random.uniform(0.50, 0.75),
                2,
            )

            products.append(
                (
                    product_id,
                    product_name,
                    category,
                    price,
                    cost,
                )
            )

            product_id += 1

    return products


# ---------------------------------------------------------
# GENERATE CUSTOMERS
# ---------------------------------------------------------

def generate_customers():
    customers = []

    regions = list(REGIONS.keys())

    for customer_id in range(1, NUM_CUSTOMERS + 1):

        signup_date = fake.date_between(
            start_date="-18M",
            end_date="today",
        )

        region = random.choice(regions)

        city_options = [
            city
            for _, city in REGIONS[region]
        ]

        city = random.choice(city_options)

        customers.append(
            (  

                customer_id,
                fake.name(),
                fake.unique.email(),
                region,
                city,
                signup_date,
            )
        )

    return customers


# ---------------------------------------------------------
# MONTHLY BUSINESS BEHAVIOUR
# ---------------------------------------------------------

def get_monthly_config(month):
    """
    July deliberately contains several hidden business problems.
    """

    config = {
        "order_multiplier": 1.0,
        "avg_items_multiplier": 1.0,
        "payment_failure_rate": 0.02,
        "refund_rate": 0.03,
        "region_weights": {
            "North": 0.25,
            "South": 0.25,
            "West": 0.25,
            "East": 0.25,
        },
        "category_weights": {
            "Electronics": 0.20,
            "Fashion": 0.20,
            "Home": 0.15,
            "Grocery": 0.20,
            "Beauty": 0.15,
            "Sports": 0.10,
        },
    }

    # -----------------------------------------------------
    # THE JULY ANOMALY
    # -----------------------------------------------------

    if month == 7:

        # Fewer transactions
        config["order_multiplier"] = 0.88

        # Smaller baskets
        config["avg_items_multiplier"] = 0.85

        # More payment failures
        config["payment_failure_rate"] = 0.05

        # More refunds
        config["refund_rate"] = 0.08

        # Regional problems
        config["region_weights"] = {
            "North": 0.17,
            "South": 0.32,
            "West": 0.30,
            "East": 0.21,
        }

        # Product mix shifts away from expensive categories
        config["category_weights"] = {
            "Electronics": 0.11,
            "Fashion": 0.24,
            "Home": 0.17,
            "Grocery": 0.12,
            "Beauty": 0.20,
            "Sports": 0.16,
        }

    return config


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def random_date(start, end):
    delta = end - start

    random_seconds = random.randint(
        0,
        int(delta.total_seconds()),
    )

    return start + timedelta(seconds=random_seconds)


def choose_weighted(weights_dict):
    names = list(weights_dict.keys())
    weights = list(weights_dict.values())

    return random.choices(
        names,
        weights=weights,
        k=1,
    )[0]


# ---------------------------------------------------------
# GENERATE ORDERS + ITEMS
# ---------------------------------------------------------

def generate_orders(products, customers, stores):

    products_by_category = {}

    for product in products:

        product_id = product[0]
        category = product[2]

        products_by_category.setdefault(
            category,
            [],
        ).append(product)

    customers_by_region = {}

    for customer in customers:

        customer_id = customer[0]
        region = customer[3]

        customers_by_region.setdefault(
            region,
            [],
        ).append(customer)

    orders = []
    order_items = []
    payments = []
    refunds = []

    order_id = 1
    item_id = 1
    payment_id = 1
    refund_id = 1

    current_month = 1

    base_orders_per_month = NUM_ORDERS // 12

    for month in range(1, 13):

        config = get_monthly_config(month)

        start = datetime(
            2025,
            month,
            1,
        )

        if month == 12:
            end = datetime(
                2025,
                12,
                31,
                23,
                59,
                59,
            )
        else:
            end = datetime(
                2025,
                month + 1,
                1,
            ) - timedelta(seconds=1)

        monthly_orders = int(
            base_orders_per_month
            * config["order_multiplier"]
            * random.uniform(0.95, 1.05)
        )

        print(
            f"Generating month {month}: "
            f"{monthly_orders:,} orders"
        )

        for _ in range(monthly_orders):

            # -----------------------------
            # REGION
            # -----------------------------

            region = choose_weighted(
                config["region_weights"]
            )

            customer = random.choice(
                customers_by_region[region]
            )

            customer_id = customer[0]

            # Pick a store from the same region
            region_store_ids = [
                store[0]
                for store in stores
                if store[2] == region
            ]

            store_id = random.choice(
                region_store_ids
            )

            # -----------------------------
            # ORDER DATE
            # -----------------------------

            order_date = random_date(
                start,
                end,
            )

            # -----------------------------
            # ORDER STATUS
            # -----------------------------

            payment_failed = (
                random.random()
                < config["payment_failure_rate"]
            )

            if payment_failed:

                status = "cancelled"

            else:

                status = random.choices(
                    ["completed", "pending", "cancelled"],
                    weights=[0.96, 0.02, 0.02],
                    k=1,
                )[0]

            # -----------------------------
            # PRODUCTS
            # -----------------------------

            category = choose_weighted(
                config["category_weights"]
            )

            avg_items = 1.7 * config["avg_items_multiplier"]

            number_of_items = max(
                1,
                int(
                    np.random.poisson(avg_items)
                ),
            )

            selected_items = []

            for _ in range(number_of_items):

                product = random.choice(
                    products_by_category[category]
                )

                product_id = product[0]
                product_price = float(product[3])

                quantity = random.choices(
                    [1, 2, 3],
                    weights=[0.70, 0.23, 0.07],
                    k=1,
                )[0]

                selected_items.append(
                    (
                        product_id,
                        product_price,
                        quantity,
                    )
                )

            total_amount = round(
                sum(
                    price * quantity
                    for _, price, quantity
                    in selected_items
                ),
                2,
            )

            # -----------------------------
            # ORDER
            # -----------------------------

            orders.append(
                (
                    order_id,
                    customer_id,
                    store_id,
                    order_date,
                    status,
                    total_amount,
                )
            )

            # -----------------------------
            # ORDER ITEMS
            # -----------------------------

            for product_id, price, quantity in selected_items:

                order_items.append(
                    (
                        item_id,
                        order_id,
                        product_id,
                        quantity,
                        price,
                    )
                )

                item_id += 1

            # -----------------------------
            # PAYMENT
            # -----------------------------

            payment_status = (
                "failed"
                if status == "cancelled"
                else "success"
                if status == "completed"
                else "pending"
            )

            payments.append(
                (
                    payment_id,
                    order_id,
                    order_date,
                    total_amount,
                    random.choice(PAYMENT_METHODS),
                    payment_status,
                )
            )

            payment_id += 1

            # -----------------------------
            # REFUND
            # -----------------------------

            if (
                status == "completed"
                and random.random()
                < config["refund_rate"]
            ):

                refund_amount = round(
                    total_amount
                    * random.uniform(0.30, 1.00),
                    2,
                )

                refund_reason = random.choice(
                    REFUND_REASONS
                )

                # Make electronics refunds more likely
                # to be "Damaged product".
                if category == "Electronics" and month == 7:
                    refund_reason = random.choices(
                        [
                            "Damaged product",
                            "Wrong item",
                            "Late delivery",
                            "Customer changed mind",
                            "Product not as expected",
                        ],
                        weights=[0.55, 0.15, 0.10, 0.10, 0.10],
                        k=1,
                    )[0]

                refund_date = order_date + timedelta(
                    days=random.randint(1, 15)
                )

                refunds.append(
                    (
                        refund_id,
                        order_id,
                        refund_date,
                        refund_amount,
                        refund_reason,
                    )
                )

                refund_id += 1

            order_id += 1

    return orders, order_items, payments, refunds


# ---------------------------------------------------------
# BULK INSERT
# ---------------------------------------------------------

def bulk_insert(conn, query, data, label):

    print(
        f"Inserting {len(data):,} {label}..."
    )

    with conn.cursor() as cur:

        execute_values(
            cur,
            query,
            data,
            page_size=BATCH_SIZE,
        )

    conn.commit()

    print(
        f"{label.capitalize()} inserted."
    )


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    conn = get_connection()

    try:

        # -------------------------------------------------
        # WARNING:
        # Set this to False once you have real data.
        # -------------------------------------------------

        RESET_DATABASE = True

        if RESET_DATABASE:
            reset_database(conn)

        # -------------------------------------------------
        # GENERATE BASIC DATA
        # -------------------------------------------------

        print("\nGenerating stores...")
        stores = generate_stores()

        print("\nGenerating products...")
        products = generate_products()

        print("\nGenerating customers...")
        customers = generate_customers()

        # -------------------------------------------------
        # INSERT BASIC DATA
        # -------------------------------------------------

        bulk_insert(
            conn,
            """
            INSERT INTO stores
                (id, name, region, city)
            OVERRIDING SYSTEM VALUE
            VALUES %s
            """,
            stores,
            "stores",
        )

        bulk_insert(
            conn,
            """
            INSERT INTO products
                (id, name, category, price, cost)
            OVERRIDING SYSTEM VALUE
            VALUES %s
            """,
            products,
            "products",
        )

        bulk_insert(
            conn,
            """
            INSERT INTO customers
                (id, name, email, region, city, signup_date)
            OVERRIDING SYSTEM VALUE    
            VALUES %s
            """,
            customers,
            "customers",
        )

        # -------------------------------------------------
        # GENERATE TRANSACTIONS
        # -------------------------------------------------

        print("\nGenerating orders, items, payments and refunds...")

        orders, order_items, payments, refunds = (
            generate_orders(
                products,
                customers,
                stores,
            )
        )

        # -------------------------------------------------
        # INSERT TRANSACTIONS
        # -------------------------------------------------

        bulk_insert(
            conn,
            """
            INSERT INTO orders
                (
                    id,
                    customer_id,
                    store_id,
                    order_date,
                    status,
                    total_amount
                )
            OVERRIDING SYSTEM VALUE    
            VALUES %s
            """,
            orders,
            "orders",
        )

        bulk_insert(
            conn,
            """
            INSERT INTO order_items
                (
                    id,
                    order_id,
                    product_id,
                    quantity,
                    unit_price
                )
            OVERRIDING SYSTEM VALUE    
            VALUES %s
            """,
            order_items,
            "order items",
        )

        bulk_insert(
            conn,
            """
            INSERT INTO payments
                (
                    id,
                    order_id,
                    payment_date,
                    amount,
                    method,
                    status
                )
            OVERRIDING SYSTEM VALUE    
            VALUES %s
            """,
            payments,
            "payments",
        )

        bulk_insert(
            conn,
            """
            INSERT INTO refunds
                (
                    id,
                    order_id,
                    refund_date,
                    amount,
                    reason
                )
            OVERRIDING SYSTEM VALUE    
            VALUES %s
            """,
            refunds,
            "refunds",
        )

        print("\n✅ DATA GENERATION COMPLETE")

        print("\nSummary:")
        print(f"Customers : {len(customers):,}")
        print(f"Products  : {len(products):,}")
        print(f"Stores    : {len(stores):,}")
        print(f"Orders    : {len(orders):,}")
        print(f"Items     : {len(order_items):,}")
        print(f"Payments  : {len(payments):,}")
        print(f"Refunds   : {len(refunds):,}")

    except Exception as exc:

        conn.rollback()

        print("\n❌ ERROR:")
        print(exc)

        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()