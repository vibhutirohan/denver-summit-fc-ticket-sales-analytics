"""Generate realistic synthetic data for the Denver Summit FC portfolio project.

The script is deterministic: rerunning it with the same seed recreates the same
CSV files. All names, email addresses, purchases, and engagement events are
fictional and intended only for analytics practice.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20250628
RNG = np.random.default_rng(SEED)
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"

FIRST_NAMES = [
    "Avery", "Jordan", "Taylor", "Morgan", "Cameron", "Riley", "Casey",
    "Quinn", "Parker", "Reese", "Drew", "Emerson", "Hayden", "Rowan",
    "Skyler", "Alex", "Jamie", "Sam", "Nico", "Maya", "Elena", "Mateo",
    "Sofia", "Luis", "Diego", "Priya", "Noah", "Mia", "Ethan", "Zoe",
]
LAST_NAMES = [
    "Garcia", "Martinez", "Johnson", "Brown", "Wilson", "Anderson", "Thomas",
    "Moore", "Jackson", "White", "Harris", "Clark", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Lopez", "Hill", "Scott",
    "Green", "Adams", "Baker", "Nelson", "Carter", "Mitchell", "Perez", "Nguyen",
]

SEGMENT_CONFIG = {
    "Season Ticket Member": {"weight": 0.20, "renewal_base": 0.82},
    "Multi-Match Buyer": {"weight": 0.21, "renewal_base": 0.66},
    "Single-Match Buyer": {"weight": 0.25, "renewal_base": 0.45},
    "Group Organizer": {"weight": 0.13, "renewal_base": 0.61},
    "Premium Client": {"weight": 0.07, "renewal_base": 0.76},
    "Lapsed Fan": {"weight": 0.14, "renewal_base": 0.24},
}

MATCH_SCHEDULE = [
    ("2025-03-08", "Sacramento Republic FC", "Regular Season", 1.05, False),
    ("2025-03-22", "Colorado Springs Switchbacks", "Regular Season", 1.38, True),
    ("2025-04-05", "Las Vegas Lights FC", "Regular Season", 0.96, False),
    ("2025-04-19", "New Mexico United", "Regular Season", 1.29, True),
    ("2025-04-30", "Northern Colorado Hailstorm", "U.S. Open Cup", 1.12, True),
    ("2025-05-10", "Phoenix Rising FC", "Regular Season", 1.22, False),
    ("2025-05-24", "Oakland Roots SC", "Regular Season", 1.01, False),
    ("2025-06-07", "San Antonio FC", "Regular Season", 1.08, False),
    ("2025-06-21", "Orange County SC", "Regular Season", 0.94, False),
    ("2025-07-04", "Colorado Springs Switchbacks", "Regular Season", 1.55, True),
    ("2025-07-12", "Monterey Bay FC", "Regular Season", 0.91, False),
    ("2025-07-26", "Louisville City FC", "Regular Season", 1.24, False),
    ("2025-08-06", "Real Salt Lake", "Club Friendly", 1.34, False),
    ("2025-08-16", "FC Tulsa", "Regular Season", 0.89, False),
    ("2025-08-30", "El Paso Locomotive FC", "Regular Season", 0.98, False),
    ("2025-09-13", "New Mexico United", "Regular Season", 1.31, True),
    ("2025-09-24", "Memphis 901 FC", "Regular Season", 0.87, False),
    ("2025-10-04", "Tampa Bay Rowdies", "Regular Season", 1.10, False),
    ("2025-10-18", "Detroit City FC", "Regular Season", 1.18, False),
    ("2025-10-25", "Indy Eleven", "Playoffs", 1.43, False),
]


def random_date(start: pd.Timestamp, end: pd.Timestamp) -> pd.Timestamp:
    """Return a random date between two timestamps, inclusive."""
    start = pd.Timestamp(start).normalize()
    end = pd.Timestamp(end).normalize()
    if end <= start:
        return start
    return start + pd.Timedelta(days=int(RNG.integers(0, (end - start).days + 1)))


def build_customers(n_customers: int = 3_200) -> pd.DataFrame:
    """Create a CRM-style customer table."""
    segment_names = list(SEGMENT_CONFIG)
    segment_weights = [SEGMENT_CONFIG[name]["weight"] for name in segment_names]
    segments = RNG.choice(segment_names, n_customers, p=segment_weights)

    cities = ["Denver", "Aurora", "Lakewood", "Arvada", "Littleton", "Westminster", "Boulder", "Golden"]
    city_weights = [0.43, 0.14, 0.10, 0.09, 0.08, 0.07, 0.05, 0.04]
    preferred_channels = RNG.choice(["Email", "SMS", "Social"], n_customers, p=[0.56, 0.27, 0.17])

    records: list[dict] = []
    for index in range(n_customers):
        first = str(RNG.choice(FIRST_NAMES))
        last = str(RNG.choice(LAST_NAMES))
        segment = str(segments[index])
        join_date = random_date(pd.Timestamp("2021-01-01"), pd.Timestamp("2025-02-15"))
        score = float(
            np.clip(
                SEGMENT_CONFIG[segment]["renewal_base"] + RNG.normal(0, 0.11),
                0.05,
                0.98,
            )
        )
        renewed = (
            int(RNG.random() < score)
            if segment == "Season Ticket Member"
            else pd.NA
        )
        customer_id = f"C{index + 1:06d}"
        email_slug = f"{first}.{last}.{index + 1}".lower()
        records.append(
            {
                "customer_id": customer_id,
                "first_name": first,
                "last_name": last,
                "email": f"{email_slug}@example.com",
                "phone": f"303-555-{1000 + (index % 9000):04d}",
                "city": str(RNG.choice(cities, p=city_weights)),
                "state": "CO",
                "zip_code": int(RNG.integers(80002, 80240)),
                "customer_segment": segment,
                "join_date": join_date.date().isoformat(),
                "preferred_channel": str(preferred_channels[index]),
                "renewal_likelihood": round(score * 100, 1),
                "renewed_season_ticket": renewed,
                "lifetime_value": 0.0,  # Updated after ticket purchases are generated.
            }
        )
    return pd.DataFrame(records)


def build_matches() -> pd.DataFrame:
    """Create the fictional club's 2025 home schedule."""
    results = [
        "W 2-0", "D 1-1", "W 3-1", "L 0-1", "W 2-1", "D 2-2", "W 1-0",
        "L 1-2", "W 2-1", "W 3-0", "D 0-0", "L 1-3", "D 2-2", "W 2-0",
        "W 1-0", "L 0-2", "W 3-2", "D 1-1", "W 2-1", "W 1-0",
    ]
    records = []
    for index, (date_text, opponent, competition, demand, rivalry) in enumerate(MATCH_SCHEDULE):
        match_date = pd.Timestamp(date_text)
        weekend = match_date.dayofweek >= 5
        kickoff = "7:30 PM" if match_date.month >= 5 else "6:00 PM"
        if match_date.dayofweek == 6:
            kickoff = "4:00 PM"
        records.append(
            {
                "match_id": f"M{index + 1:03d}",
                "season": 2025,
                "match_date": match_date.date().isoformat(),
                "kickoff_time": kickoff,
                "opponent": opponent,
                "competition": competition,
                "venue": "Summit Park",
                "capacity": 8_200,
                "rivalry_match": int(rivalry),
                "weekend_match": int(weekend),
                "base_demand_index": demand,
                "result": results[index],
            }
        )
    return pd.DataFrame(records)


def ticket_profile(segment: str, demand: float, rivalry: bool) -> tuple[float, str, np.ndarray, np.ndarray]:
    """Return purchase probability, ticket type, quantities, and weights by segment."""
    demand_boost = max(demand - 0.85, 0) * 0.22
    rivalry_boost = 0.05 if rivalry else 0.0
    profiles = {
        "Season Ticket Member": (0.96, "Season Ticket", [1, 2, 3, 4], [0.45, 0.40, 0.11, 0.04]),
        "Multi-Match Buyer": (0.31 + demand_boost, "Single Match", [1, 2, 3, 4], [0.28, 0.49, 0.13, 0.10]),
        "Single-Match Buyer": (0.09 + demand_boost, "Single Match", [1, 2, 3, 4], [0.32, 0.48, 0.12, 0.08]),
        "Group Organizer": (0.12 + demand_boost, "Group", [8, 10, 12, 16, 20, 25, 30], [0.12, 0.16, 0.20, 0.22, 0.16, 0.09, 0.05]),
        "Premium Client": (0.33 + demand_boost, "Premium", [1, 2, 3, 4, 6], [0.18, 0.42, 0.17, 0.17, 0.06]),
        "Lapsed Fan": (0.025 + demand_boost * 0.45, "Single Match", [1, 2, 3, 4], [0.35, 0.48, 0.11, 0.06]),
    }
    probability, ticket_type, quantities, weights = profiles[segment]
    return min(probability + rivalry_boost, 0.98), ticket_type, np.array(quantities), np.array(weights)


def build_tickets(customers: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Create ticket order lines tied to customers and home matches."""
    records: list[dict] = []
    ticket_counter = 1
    section_options = {
        "Season Ticket": (["Supporters' End", "East Sideline", "West Sideline", "Club Level"], [0.33, 0.34, 0.25, 0.08]),
        "Single Match": (["Supporters' End", "East Sideline", "West Sideline", "Family Zone"], [0.27, 0.29, 0.27, 0.17]),
        "Group": (["North End", "Family Zone", "East Sideline"], [0.37, 0.42, 0.21]),
        "Premium": (["Club Level", "Fieldside", "Summit Suites"], [0.47, 0.35, 0.18]),
    }
    section_multipliers = {
        "Supporters' End": 0.78, "East Sideline": 1.05, "West Sideline": 1.12,
        "Club Level": 1.45, "Family Zone": 0.82, "North End": 0.80,
        "Fieldside": 1.62, "Summit Suites": 1.90,
    }
    base_prices = {"Season Ticket": 33.0, "Single Match": 41.0, "Group": 27.0, "Premium": 118.0}

    customer_rows = customers.to_dict("records")
    for match in matches.to_dict("records"):
        match_date = pd.Timestamp(match["match_date"])
        demand = float(match["base_demand_index"])
        rivalry = bool(match["rivalry_match"])
        sold_for_match = 0
        order = RNG.permutation(len(customer_rows))

        for position in order:
            customer = customer_rows[int(position)]
            probability, ticket_type, quantities, weights = ticket_profile(
                customer["customer_segment"], demand, rivalry
            )
            if RNG.random() > probability:
                continue

            quantity = int(RNG.choice(quantities, p=weights))
            remaining = int(match["capacity"] * 0.97) - sold_for_match
            if remaining <= 0:
                break
            if quantity > remaining:
                if ticket_type == "Group" or remaining == 0:
                    continue
                quantity = remaining

            sections, section_weights = section_options[ticket_type]
            section = str(RNG.choice(sections, p=section_weights))
            discount_code = ""
            discount = 1.0
            if ticket_type == "Season Ticket":
                discount_code, discount = "MEMBER", 0.88
            elif ticket_type == "Group":
                discount_code, discount = "GROUP15", 0.85
            elif RNG.random() < 0.13:
                discount_code, discount = str(RNG.choice(["SUMMIT10", "FAMILY", "WELCOME"])), 0.90

            price_noise = RNG.normal(1.0, 0.035)
            unit_price = round(
                base_prices[ticket_type]
                * section_multipliers[section]
                * (0.88 + 0.13 * demand)
                * discount
                * price_noise,
                2,
            )
            max_lead = 210 if ticket_type == "Season Ticket" else (100 if ticket_type == "Group" else 75)
            earliest = max(
                pd.Timestamp(customer["join_date"]),
                match_date - pd.Timedelta(days=max_lead),
            )
            purchase_date = random_date(earliest, match_date - pd.Timedelta(days=1))
            sales_channel = str(
                RNG.choice(
                    ["Online", "Box Office", "Sales Representative", "Mobile App"],
                    p=[0.48, 0.13, 0.23 if ticket_type in {"Group", "Premium"} else 0.10, 0.16 if ticket_type in {"Group", "Premium"} else 0.29],
                )
            )

            records.append(
                {
                    "ticket_id": f"T{ticket_counter:07d}",
                    "customer_id": customer["customer_id"],
                    "match_id": match["match_id"],
                    "ticket_type": ticket_type,
                    "purchase_date": purchase_date.date().isoformat(),
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_revenue": round(quantity * unit_price, 2),
                    "section": section,
                    "discount_code": discount_code,
                    "sales_channel": sales_channel,
                }
            )
            sold_for_match += quantity
            ticket_counter += 1
    return pd.DataFrame(records)


def build_attendance(tickets: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Simulate turnstile scans for every ticket order line."""
    match_lookup = matches.set_index("match_id").to_dict("index")
    base_scan_rates = {
        "Season Ticket": 0.84,
        "Single Match": 0.91,
        "Group": 0.79,
        "Premium": 0.93,
    }
    gates = ["North Gate", "East Gate", "West Gate", "Premium Entrance"]
    records = []
    for index, ticket in enumerate(tickets.to_dict("records")):
        match = match_lookup[ticket["match_id"]]
        rate = base_scan_rates[ticket["ticket_type"]]
        rate += (float(match["base_demand_index"]) - 1.0) * 0.055
        if bool(match["weekend_match"]):
            rate += 0.018
        rate = float(np.clip(rate + RNG.normal(0, 0.025), 0.58, 0.98))
        scanned = int(RNG.binomial(int(ticket["quantity"]), rate))
        scan_timestamp = ""
        if scanned:
            match_date = pd.Timestamp(match["match_date"])
            minutes_before = int(np.clip(RNG.normal(38, 18), 3, 105))
            kickoff_hour = 19 if "7:30" in match["kickoff_time"] else (18 if "6:00" in match["kickoff_time"] else 16)
            kickoff_minute = 30 if ":30" in match["kickoff_time"] else 0
            kickoff = match_date + pd.Timedelta(hours=kickoff_hour, minutes=kickoff_minute)
            scan_timestamp = (kickoff - pd.Timedelta(minutes=minutes_before)).isoformat(sep=" ")

        status = "Full Scan" if scanned == ticket["quantity"] else ("Partial Scan" if scanned else "No Show")
        records.append(
            {
                "attendance_id": f"A{index + 1:07d}",
                "ticket_id": ticket["ticket_id"],
                "match_id": ticket["match_id"],
                "customer_id": ticket["customer_id"],
                "tickets_issued": int(ticket["quantity"]),
                "tickets_scanned": scanned,
                "scan_timestamp": scan_timestamp,
                "entry_gate": str(RNG.choice(gates, p=[0.31, 0.27, 0.28, 0.14])),
                "attendance_status": status,
            }
        )
    return pd.DataFrame(records)


def build_campaigns() -> pd.DataFrame:
    """Create a season-long marketing campaign calendar."""
    specs = [
        ("Season Ticket Early Bird", "Email", "2024-11-18", "2025-01-31", "Season Ticket Member", 18000, "Renewal"),
        ("New Year, New Summit", "Social", "2025-01-06", "2025-01-26", "All Fans", 12500, "Acquisition"),
        ("Home Opener Countdown", "Email", "2025-02-10", "2025-03-08", "All Fans", 9800, "Ticket Sales"),
        ("Front Range Derby Presale", "SMS", "2025-03-01", "2025-03-20", "Multi-Match Buyer", 6200, "Ticket Sales"),
        ("Family Four-Pack", "Email", "2025-03-24", "2025-04-19", "Single-Match Buyer", 5400, "Ticket Sales"),
        ("Open Cup Push", "Social", "2025-04-20", "2025-04-30", "All Fans", 7400, "Awareness"),
        ("Mile High May", "SMS", "2025-05-01", "2025-05-24", "Lapsed Fan", 4900, "Reactivation"),
        ("Summer Soccer Series", "Email", "2025-05-27", "2025-06-21", "Multi-Match Buyer", 7600, "Ticket Sales"),
        ("Independence Day Derby", "Social", "2025-06-12", "2025-07-04", "All Fans", 14200, "Ticket Sales"),
        ("Derby Last Chance", "SMS", "2025-06-29", "2025-07-04", "All Fans", 6800, "Ticket Sales"),
        ("Group Night Out", "Email", "2025-07-07", "2025-07-26", "Group Organizer", 5100, "Group Sales"),
        ("RSL Friendly Spotlight", "Social", "2025-07-18", "2025-08-06", "Single-Match Buyer", 10600, "Ticket Sales"),
        ("Premium Experience", "Email", "2025-08-01", "2025-08-30", "Premium Client", 7200, "Upsell"),
        ("September Rivalry", "SMS", "2025-08-25", "2025-09-13", "Multi-Match Buyer", 5900, "Ticket Sales"),
        ("Lapsed Fan Win-Back", "Email", "2025-09-01", "2025-09-24", "Lapsed Fan", 5700, "Reactivation"),
        ("Final Regular Season Push", "Social", "2025-09-22", "2025-10-18", "All Fans", 11800, "Ticket Sales"),
        ("Playoff Priority Access", "Email", "2025-10-05", "2025-10-24", "Season Ticket Member", 8900, "Retention"),
        ("2026 Renewal Launch", "SMS", "2025-10-20", "2025-11-14", "Season Ticket Member", 6500, "Renewal"),
    ]
    return pd.DataFrame(
        [
            {
                "campaign_id": f"CMP{index + 1:03d}",
                "campaign_name": name,
                "channel": channel,
                "start_date": start,
                "end_date": end,
                "target_segment": target,
                "audience_size": 0,  # Updated to actual recipients below.
                "budget": budget,
                "objective": objective,
            }
            for index, (name, channel, start, end, target, budget, objective) in enumerate(specs)
        ]
    )


def build_campaign_conversions(
    campaigns: pd.DataFrame,
    customers: pd.DataFrame,
    tickets: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create recipient-level opens, clicks, and attributed conversions."""
    channel_rates = {
        "Email": {"open": 0.49, "click": 0.20, "convert": 0.24},
        "SMS": {"open": 0.91, "click": 0.24, "convert": 0.27},
        "Social": {"open": 0.68, "click": 0.105, "convert": 0.17},
    }
    segment_lift = {
        "Season Ticket Member": 1.18,
        "Multi-Match Buyer": 1.12,
        "Single-Match Buyer": 0.98,
        "Group Organizer": 1.08,
        "Premium Client": 1.20,
        "Lapsed Fan": 0.72,
    }
    tickets_by_customer = (
        tickets.groupby("customer_id")["ticket_id"].apply(list).to_dict()
    )
    records: list[dict] = []
    conversion_counter = 1

    for campaign_index, campaign in campaigns.iterrows():
        if campaign["target_segment"] == "All Fans":
            eligible = customers
            sample_fraction = 0.72
        else:
            eligible = customers[customers["customer_segment"] == campaign["target_segment"]]
            sample_fraction = 0.88
        audience_count = max(1, min(len(eligible), int(len(eligible) * sample_fraction)))
        sampled_indices = RNG.choice(eligible.index.to_numpy(), audience_count, replace=False)
        recipients = eligible.loc[sampled_indices]
        campaigns.loc[campaign_index, "audience_size"] = audience_count

        base = channel_rates[campaign["channel"]]
        start_date = pd.Timestamp(campaign["start_date"])
        end_date = pd.Timestamp(campaign["end_date"])
        for customer in recipients.to_dict("records"):
            lift = segment_lift[customer["customer_segment"]]
            preferred_lift = 1.10 if customer["preferred_channel"] == campaign["channel"] else 1.0
            opened = int(RNG.random() < min(base["open"] * preferred_lift, 0.98))
            clicked = int(opened and RNG.random() < min(base["click"] * lift, 0.80))
            converted = int(clicked and RNG.random() < min(base["convert"] * lift, 0.75))
            attributed_ticket = ""
            revenue = 0.0
            conversion_date = ""
            if converted:
                customer_tickets = tickets_by_customer.get(customer["customer_id"], [])
                attributed_ticket = str(RNG.choice(customer_tickets)) if customer_tickets else ""
                revenue_base = {
                    "Season Ticket Member": 125,
                    "Multi-Match Buyer": 92,
                    "Single-Match Buyer": 74,
                    "Group Organizer": 310,
                    "Premium Client": 245,
                    "Lapsed Fan": 58,
                }[customer["customer_segment"]]
                revenue = round(max(25, RNG.normal(revenue_base, revenue_base * 0.34)), 2)
                conversion_date = random_date(start_date, end_date).date().isoformat()

            records.append(
                {
                    "conversion_id": f"CV{conversion_counter:07d}",
                    "campaign_id": campaign["campaign_id"],
                    "customer_id": customer["customer_id"],
                    "sent": 1,
                    "opened": opened,
                    "clicked": clicked,
                    "converted": converted,
                    "conversion_date": conversion_date,
                    "revenue": revenue,
                    "attributed_ticket_id": attributed_ticket,
                }
            )
            conversion_counter += 1
    campaigns["audience_size"] = campaigns["audience_size"].astype(int)
    return campaigns, pd.DataFrame(records)


def update_customer_value(customers: pd.DataFrame, tickets: pd.DataFrame) -> pd.DataFrame:
    """Derive customer lifetime value from current-season purchases plus history."""
    spend = tickets.groupby("customer_id")["total_revenue"].sum()
    match_count = tickets.groupby("customer_id")["match_id"].nunique()
    customers = customers.copy()
    customers["current_season_revenue"] = customers["customer_id"].map(spend).fillna(0)
    customers["matches_purchased"] = customers["customer_id"].map(match_count).fillna(0).astype(int)
    historical_multiplier = customers["join_date"].map(
        lambda value: max(1.0, (pd.Timestamp("2025-12-31") - pd.Timestamp(value)).days / 510)
    )
    baseline = customers["customer_segment"].map(
        {
            "Season Ticket Member": 520,
            "Multi-Match Buyer": 210,
            "Single-Match Buyer": 75,
            "Group Organizer": 680,
            "Premium Client": 920,
            "Lapsed Fan": 45,
        }
    )
    customers["lifetime_value"] = (
        customers["current_season_revenue"] * historical_multiplier
        + baseline
        + RNG.normal(0, 55, len(customers))
    ).clip(lower=20).round(2)
    return customers


def save_datasets() -> None:
    """Build and save every required CSV dataset."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    customers = build_customers()
    matches = build_matches()
    tickets = build_tickets(customers, matches)
    attendance = build_attendance(tickets, matches)
    customers = update_customer_value(customers, tickets)
    campaigns = build_campaigns()
    campaigns, conversions = build_campaign_conversions(campaigns, customers, tickets)

    datasets = {
        "customers.csv": customers,
        "tickets.csv": tickets,
        "matches.csv": matches,
        "attendance.csv": attendance,
        "campaigns.csv": campaigns,
        "campaign_conversions.csv": conversions,
    }
    for filename, dataframe in datasets.items():
        dataframe.to_csv(DATA_DIR / filename, index=False)
        print(f"Created {filename:<28} {len(dataframe):>8,} rows")

    total_revenue = tickets["total_revenue"].sum()
    tickets_sold = tickets["quantity"].sum()
    scan_rate = attendance["tickets_scanned"].sum() / attendance["tickets_issued"].sum()
    print("\nSynthetic season summary")
    print(f"  Ticket revenue: ${total_revenue:,.0f}")
    print(f"  Tickets sold:   {tickets_sold:,}")
    print(f"  Scan rate:      {scan_rate:.1%}")


if __name__ == "__main__":
    save_datasets()

