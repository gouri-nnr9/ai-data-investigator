import os
import random
from datetime import date, timedelta

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import execute_values


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

random.seed(42)

START_DATE = date(2025, 1, 1)
END_DATE = date(2025, 12, 31)

BATCH_SIZE = 5000


def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
    )


def load_reference_data(conn):
    with conn.cursor() as cur:

        cur.execute("""
            SELECT id, category
            FROM products
            ORDER BY id;
        """)
        products = cur.fetchall()

        cur.execute("""
            SELECT id, region
            FROM stores
            ORDER BY id;
        """)
        stores = cur.fetchall()

    return products, stores


def generate_inventory(products, stores):

    rows = []

    current_date = START_DATE

    while current_date <= END_DATE:

        # Weekly snapshots
        for product_id, category in products:

            for store_id, region in stores:

                # -----------------------------------------
                # Normal stock levels
                # -----------------------------------------

                if category == "Electronics":
                    base_stock = random.randint(40, 140)
                elif category == "Home":
                    base_stock = random.randint(50, 180)
                elif category == "Fashion":
                    base_stock = random.randint(60, 220)
                elif category == "Grocery":
                    base_stock = random.randint(100, 400)
                elif category == "Beauty":
                    base_stock = random.randint(70, 250)
                else:  # Sports
                    base_stock = random.randint(50, 200)

                stock = base_stock

                # -----------------------------------------
                # JULY INVENTORY PROBLEM
                # -----------------------------------------

                is_july = current_date.month == 7

                if is_july and category == "Electronics":

                    if region == "North":
                        stock = random.randint(0, 10)

                    elif region == "East":
                        stock = random.randint(0, 15)

                    elif region == "West":
                        stock = random.randint(10, 35)

                    elif region == "South":
                        stock = random.randint(20, 50)

                # -----------------------------------------
                # Small realistic variation
                # -----------------------------------------

                variation = random.randint(-5, 10)

                stock = max(
                    0,
                    stock + variation
                )

                rows.append(
                    (
                        product_id,
                        store_id,
                        current_date,
                        stock,
                    )
                )

        current_date += timedelta(days=7)

    return rows


def insert_inventory(conn, rows):

    print(
        f"Inserting {len(rows):,} inventory records..."
    )

    with conn.cursor() as cur:

        execute_values(
            cur,
            """
            INSERT INTO inventory
                (
                    product_id,
                    store_id,
                    inventory_date,
                    stock_available
                )
            VALUES %s
            """,
            rows,
            page_size=BATCH_SIZE,
        )

    conn.commit()

    print("Inventory inserted successfully.")


def main():

    conn = get_connection()

    try:

        # -----------------------------------------
        # Reset inventory only
        # -----------------------------------------

        with conn.cursor() as cur:
            cur.execute("""
                TRUNCATE TABLE inventory
                RESTART IDENTITY CASCADE;
            """)

        conn.commit()

        print("Inventory table reset.")

        # -----------------------------------------
        # Load existing data
        # -----------------------------------------

        products, stores = load_reference_data(conn)

        print(
            f"Loaded {len(products)} products "
            f"and {len(stores)} stores."
        )

        # -----------------------------------------
        # Generate
        # -----------------------------------------

        rows = generate_inventory(
            products,
            stores,
        )

        # -----------------------------------------
        # Insert
        # -----------------------------------------

        insert_inventory(
            conn,
            rows,
        )

        print("\n✅ INVENTORY GENERATION COMPLETE")
        print(
            f"Inventory records: {len(rows):,}"
        )

    except Exception as exc:

        conn.rollback()

        print("\n❌ ERROR:")
        print(exc)

        raise

    finally:

        conn.close()


if __name__ == "__main__":
    main()