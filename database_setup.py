"""Load Denver Summit FC CSV datasets into a local SQLite database."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "denver_summit_fc.db"
TABLE_FILES = {
    "customers": "customers.csv",
    "tickets": "tickets.csv",
    "matches": "matches.csv",
    "attendance": "attendance.csv",
    "campaigns": "campaigns.csv",
    "campaign_conversions": "campaign_conversions.csv",
}


def build_database() -> None:
    """Replace database tables with the latest generated CSV data."""
    missing = [filename for filename in TABLE_FILES.values() if not (DATA_DIR / filename).exists()]
    if missing:
        missing_text = ", ".join(missing)
        raise FileNotFoundError(
            f"Missing CSV files: {missing_text}. Run `python generate_data.py` first."
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        for table_name, filename in TABLE_FILES.items():
            dataframe = pd.read_csv(DATA_DIR / filename)
            dataframe.to_sql(table_name, connection, if_exists="replace", index=False)
            print(f"Loaded {table_name:<24} {len(dataframe):>8,} rows")

        connection.executescript(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_id
                ON customers(customer_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_tickets_id
                ON tickets(ticket_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_customer
                ON tickets(customer_id);
            CREATE INDEX IF NOT EXISTS idx_tickets_match
                ON tickets(match_id);
            CREATE UNIQUE INDEX IF NOT EXISTS idx_matches_id
                ON matches(match_id);
            CREATE INDEX IF NOT EXISTS idx_attendance_match
                ON attendance(match_id);
            CREATE INDEX IF NOT EXISTS idx_campaign_conversions_campaign
                ON campaign_conversions(campaign_id);
            CREATE INDEX IF NOT EXISTS idx_campaign_conversions_customer
                ON campaign_conversions(customer_id);

            DROP VIEW IF EXISTS ticket_sales_detail;
            CREATE VIEW ticket_sales_detail AS
            SELECT
                t.ticket_id,
                t.customer_id,
                c.customer_segment,
                t.match_id,
                m.match_date,
                m.opponent,
                t.ticket_type,
                t.quantity,
                t.unit_price,
                t.total_revenue,
                t.sales_channel,
                a.tickets_scanned
            FROM tickets AS t
            JOIN customers AS c ON c.customer_id = t.customer_id
            JOIN matches AS m ON m.match_id = t.match_id
            LEFT JOIN attendance AS a ON a.ticket_id = t.ticket_id;
            """
        )
        connection.commit()

    print(f"\nSQLite database created at: {DATABASE_PATH}")


if __name__ == "__main__":
    build_database()
