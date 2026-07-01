"""Streamlit dashboard for Denver Summit FC ticket sales and fan engagement."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "denver_summit_fc.db"

NAVY = "#102A43"
BLUE = "#1F5E8C"
SKY = "#38A3DB"
GOLD = "#F2B84B"
TEAL = "#1F9D8A"
RED = "#D95D5D"
SLATE = "#627D98"
LIGHT = "#F4F7FA"
COLOR_SEQUENCE = [BLUE, SKY, GOLD, TEAL, "#7E6BB6", RED]


st.set_page_config(
    page_title="Denver Summit FC | Analytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    f"""
    <style>
        .stApp {{ background: {LIGHT}; }}
        [data-testid="stHeader"] {{ background: {LIGHT}; }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {NAVY} 0%, #173F5F 100%);
        }}
        [data-testid="stSidebar"] * {{ color: #F7FAFC; }}
        [data-testid="stSidebar"] [data-baseweb="select"] * {{ color: {NAVY}; }}
        [data-testid="stSidebar"] .stMultiSelect span {{ color: {NAVY}; }}
        [data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid #D9E2EC;
            border-radius: 12px;
            padding: 16px 18px;
            box-shadow: 0 4px 14px rgba(16, 42, 67, 0.05);
        }}
        [data-testid="stMetricLabel"] {{ color: {SLATE}; }}
        [data-testid="stMetricValue"] {{ color: {NAVY}; }}
        .hero {{
            background: linear-gradient(115deg, {NAVY} 0%, {BLUE} 72%, #277AAE 100%);
            border-radius: 16px;
            padding: 26px 30px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 8px 24px rgba(16, 42, 67, 0.16);
        }}
        .hero-kicker {{
            color: #A7D8F0;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
        }}
        .hero h1 {{
            color: white;
            font-size: 2rem;
            margin: 5px 0 4px 0;
            line-height: 1.2;
        }}
        .hero p {{ color: #D9EAF3; margin: 0; font-size: 0.98rem; }}
        .section-label {{
            color: {BLUE};
            font-size: 0.76rem;
            font-weight: 800;
            letter-spacing: 0.11em;
            margin-top: 10px;
            text-transform: uppercase;
        }}
        .insight-card {{
            background: #FFFFFF;
            border-left: 4px solid {GOLD};
            border-radius: 10px;
            min-height: 112px;
            padding: 16px 17px;
            box-shadow: 0 3px 12px rgba(16, 42, 67, 0.06);
        }}
        .insight-card .label {{
            color: {SLATE};
            font-size: 0.70rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }}
        .insight-card .copy {{
            color: {NAVY};
            font-size: 0.95rem;
            line-height: 1.45;
            margin-top: 7px;
        }}
        .sidebar-brand {{
            border-bottom: 1px solid rgba(255,255,255,0.18);
            margin-bottom: 14px;
            padding: 4px 0 18px 0;
        }}
        .sidebar-brand .club {{
            font-size: 1.2rem;
            font-weight: 800;
            letter-spacing: 0.02em;
        }}
        .sidebar-brand .sub {{
            color: #A7D8F0;
            font-size: 0.76rem;
            letter-spacing: 0.09em;
            margin-top: 2px;
            text-transform: uppercase;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid #D9E2EC;
            border-radius: 10px;
            overflow: hidden;
        }}
        h2, h3 {{ color: {NAVY}; }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data(database_path: str) -> dict[str, pd.DataFrame]:
    """Read dashboard source tables from SQLite."""
    with sqlite3.connect(database_path) as connection:
        tables = {
            name: pd.read_sql_query(f"SELECT * FROM {name}", connection)
            for name in [
                "customers",
                "tickets",
                "matches",
                "attendance",
                "campaigns",
                "campaign_conversions",
            ]
        }

    for column in ["join_date"]:
        tables["customers"][column] = pd.to_datetime(tables["customers"][column])
    for column in ["purchase_date"]:
        tables["tickets"][column] = pd.to_datetime(tables["tickets"][column])
    tables["matches"]["match_date"] = pd.to_datetime(tables["matches"]["match_date"])
    for column in ["start_date", "end_date"]:
        tables["campaigns"][column] = pd.to_datetime(tables["campaigns"][column])
    tables["campaign_conversions"]["conversion_date"] = pd.to_datetime(
        tables["campaign_conversions"]["conversion_date"], errors="coerce"
    )
    return tables


def style_chart(figure: go.Figure, height: int = 370) -> go.Figure:
    """Apply a consistent, presentation-ready chart style."""
    figure.update_layout(
        height=height,
        margin=dict(l=10, r=12, t=52, b=10),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial, sans-serif", color=NAVY, size=12),
        title=dict(font=dict(size=17, color=NAVY), x=0.02, xanchor="left"),
        legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, x=0.02),
        hoverlabel=dict(bgcolor=NAVY, font_color="white"),
    )
    figure.update_xaxes(showgrid=False, linecolor="#D9E2EC")
    figure.update_yaxes(gridcolor="#E9EFF4", zeroline=False)
    return figure


def hero(title: str, description: str) -> None:
    """Render a branded page header."""
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-kicker">2025 Season • Commercial Intelligence</div>
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def insight_card(label: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="label">{label}</div>
            <div class="copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def compact_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


if not DATABASE_PATH.exists():
    st.error(
        "The SQLite database is missing. Run `python generate_data.py`, then "
        "`python database_setup.py`, and refresh this page."
    )
    st.stop()

data = load_data(str(DATABASE_PATH))
customers = data["customers"]
tickets = data["tickets"]
matches = data["matches"]
attendance = data["attendance"]
campaigns = data["campaigns"]
conversions = data["campaign_conversions"]

ticket_detail = (
    tickets.merge(
        customers[["customer_id", "customer_segment", "renewal_likelihood"]],
        on="customer_id",
        how="left",
    )
    .merge(
        matches[["match_id", "match_date", "opponent", "competition", "capacity"]],
        on="match_id",
        how="left",
    )
)

st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <div class="club">▲ DENVER SUMMIT FC</div>
        <div class="sub">Ticketing & Fan Analytics</div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.sidebar.radio(
    "Dashboard",
    [
        "Executive Overview",
        "Ticket Sales",
        "Fan Engagement",
        "Campaign Performance",
        "Retention & Renewals",
    ],
)

st.sidebar.markdown("### Filters")
min_date = matches["match_date"].min().date()
max_date = matches["match_date"].max().date()
date_selection = st.sidebar.date_input(
    "Match date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_selection, (tuple, list)) and len(date_selection) == 2:
    selected_start, selected_end = date_selection
else:
    selected_start, selected_end = min_date, max_date

all_segments = sorted(customers["customer_segment"].unique())
selected_segments = st.sidebar.multiselect(
    "Customer segments",
    all_segments,
    default=all_segments,
)
all_ticket_types = sorted(tickets["ticket_type"].unique())
selected_ticket_types = st.sidebar.multiselect(
    "Ticket types",
    all_ticket_types,
    default=all_ticket_types,
)

date_mask = ticket_detail["match_date"].dt.date.between(selected_start, selected_end)
filtered_tickets = ticket_detail[
    date_mask
    & ticket_detail["customer_segment"].isin(selected_segments)
    & ticket_detail["ticket_type"].isin(selected_ticket_types)
].copy()
selected_match_ids = matches[
    matches["match_date"].dt.date.between(selected_start, selected_end)
]["match_id"]
filtered_attendance = attendance[
    attendance["match_id"].isin(selected_match_ids)
    & attendance["customer_id"].isin(
        customers[customers["customer_segment"].isin(selected_segments)]["customer_id"]
    )
].copy()

st.sidebar.caption(
    f"{selected_start:%b %d} – {selected_end:%b %d, %Y}  •  "
    f"{filtered_tickets['quantity'].sum():,.0f} tickets"
)
st.sidebar.markdown("---")
st.sidebar.caption("Synthetic data • Built with Python, SQLite, Streamlit & Plotly")


def filtered_match_sales() -> pd.DataFrame:
    """Aggregate the active ticket filters to match level."""
    sales = (
        filtered_tickets.groupby("match_id", as_index=False)
        .agg(tickets_sold=("quantity", "sum"), revenue=("total_revenue", "sum"))
    )
    frame = matches[matches["match_id"].isin(selected_match_ids)].merge(
        sales, on="match_id", how="left"
    )
    frame[["tickets_sold", "revenue"]] = frame[["tickets_sold", "revenue"]].fillna(0)
    frame["inventory_sold_pct"] = 100 * frame["tickets_sold"] / frame["capacity"]
    return frame.sort_values("match_date")


def attendance_by_match() -> pd.DataFrame:
    """Aggregate the active attendance filters to match level."""
    scans = (
        filtered_attendance.groupby("match_id", as_index=False)
        .agg(tickets_issued=("tickets_issued", "sum"), tickets_scanned=("tickets_scanned", "sum"))
    )
    frame = matches[matches["match_id"].isin(selected_match_ids)].merge(
        scans, on="match_id", how="left"
    )
    frame[["tickets_issued", "tickets_scanned"]] = frame[
        ["tickets_issued", "tickets_scanned"]
    ].fillna(0)
    frame["scan_rate"] = (
        100 * frame["tickets_scanned"] / frame["tickets_issued"].replace(0, pd.NA)
    ).fillna(0)
    return frame.sort_values("match_date")


match_sales = filtered_match_sales()
match_attendance = attendance_by_match()


def render_overview() -> None:
    hero(
        "Executive Overview",
        "A front-office view of ticket revenue, inventory, attendance, and customer value.",
    )
    total_revenue = filtered_tickets["total_revenue"].sum()
    tickets_sold = filtered_tickets["quantity"].sum()
    avg_price = total_revenue / tickets_sold if tickets_sold else 0
    capacity = matches[matches["match_id"].isin(selected_match_ids)]["capacity"].sum()
    sold_pct = 100 * tickets_sold / capacity if capacity else 0
    scans = filtered_attendance["tickets_scanned"].sum()
    issued = filtered_attendance["tickets_issued"].sum()
    scan_rate = 100 * scans / issued if issued else 0

    buyer_matches = filtered_tickets.groupby("customer_id")["match_id"].nunique()
    repeat_rate = 100 * (buyer_matches > 1).mean() if len(buyer_matches) else 0

    kpis = [
        ("Total revenue", compact_currency(total_revenue), "Ticket sales"),
        ("Tickets sold", f"{tickets_sold:,.0f}", "Across selected matches"),
        ("Avg. ticket price", f"${avg_price:,.2f}", "Revenue per seat"),
        ("Inventory sold", f"{sold_pct:.1f}%", f"{capacity - tickets_sold:,.0f} seats open"),
        ("Matchday scan rate", f"{scan_rate:.1f}%", f"{scans:,.0f} scans"),
        ("Repeat buyer rate", f"{repeat_rate:.1f}%", "2+ matches purchased"),
    ]
    for row_start in (0, 3):
        kpi_columns = st.columns(3)
        for column, (label, value, help_text) in zip(
            kpi_columns, kpis[row_start : row_start + 3]
        ):
            column.metric(label, value, help=help_text)

    section_label("Revenue & inventory")
    left, right = st.columns([1.7, 1])
    with left:
        revenue_trend = px.line(
            match_sales,
            x="match_date",
            y="revenue",
            markers=True,
            title="Revenue trend by match date",
            labels={"match_date": "", "revenue": "Ticket revenue", "opponent": "Opponent"},
            hover_data={"opponent": True, "revenue": ":$,.0f", "match_date": "|%b %d"},
            color_discrete_sequence=[BLUE],
        )
        revenue_trend.update_traces(line_width=3, marker_size=8, fill="tozeroy", fillcolor="rgba(56,163,219,0.12)")
        revenue_trend.update_yaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(style_chart(revenue_trend), use_container_width=True)
    with right:
        revenue_type = (
            filtered_tickets.groupby("ticket_type", as_index=False)["total_revenue"]
            .sum()
            .sort_values("total_revenue", ascending=False)
        )
        type_chart = px.pie(
            revenue_type,
            names="ticket_type",
            values="total_revenue",
            hole=0.58,
            title="Revenue by ticket type",
            color="ticket_type",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        type_chart.update_traces(textposition="inside", textinfo="percent", hovertemplate="%{label}<br>$%{value:,.0f}<extra></extra>")
        st.plotly_chart(style_chart(type_chart), use_container_width=True)

    section_label("Business insights")
    top_type = (
        filtered_tickets.groupby("ticket_type")["total_revenue"].sum().sort_values(ascending=False)
    )
    segment_value = (
        filtered_tickets.groupby("customer_segment")["total_revenue"].sum().sort_values(ascending=False)
    )
    channel_perf = (
        conversions.merge(campaigns[["campaign_id", "channel"]], on="campaign_id")
        .groupby("channel")
        .agg(sent=("sent", "sum"), converted=("converted", "sum"))
    )
    channel_perf["rate"] = 100 * channel_perf["converted"] / channel_perf["sent"]
    attendance_rank = match_attendance.sort_values("scan_rate", ascending=False)
    insight_columns = st.columns(4)
    with insight_columns[0]:
        type_name = top_type.index[0] if len(top_type) else "No ticket type"
        type_share = 100 * top_type.iloc[0] / top_type.sum() if len(top_type) and top_type.sum() else 0
        insight_card(
            "Revenue driver",
            f"<b>{type_name}</b> leads the mix, generating {type_share:.1f}% of filtered ticket revenue.",
        )
    with insight_columns[1]:
        segment_name = segment_value.index[0] if len(segment_value) else "No segment"
        insight_card(
            "Most valuable segment",
            f"<b>{segment_name}</b> contributes the most current-season revenue under these filters.",
        )
    with insight_columns[2]:
        best_channel = channel_perf["rate"].idxmax()
        best_rate = channel_perf.loc[best_channel, "rate"]
        insight_card(
            "Best campaign channel",
            f"<b>{best_channel}</b> has the strongest send-to-conversion rate at {best_rate:.1f}%.",
        )
    with insight_columns[3]:
        if len(attendance_rank):
            strong = attendance_rank.iloc[0]
            weak = attendance_rank.iloc[-1]
            copy = (
                f"<b>{strong['opponent']}</b> led scan rate at {strong['scan_rate']:.1f}%; "
                f"{weak['opponent']} was softest at {weak['scan_rate']:.1f}%."
            )
        else:
            copy = "No attendance records match the current filters."
        insight_card("Matchday attendance", copy)


def render_ticket_sales() -> None:
    hero(
        "Ticket Sales",
        "Revenue pacing, product mix, inventory utilization, and buyer segment performance.",
    )
    total_revenue = filtered_tickets["total_revenue"].sum()
    total_quantity = filtered_tickets["quantity"].sum()
    order_count = filtered_tickets["ticket_id"].nunique()
    avg_order = total_revenue / order_count if order_count else 0
    best_match = match_sales.loc[match_sales["revenue"].idxmax()] if len(match_sales) else None

    columns = st.columns(4)
    columns[0].metric("Ticket revenue", compact_currency(total_revenue))
    columns[1].metric("Tickets sold", f"{total_quantity:,.0f}")
    columns[2].metric("Average order value", f"${avg_order:,.2f}")
    columns[3].metric(
        "Top revenue match",
        str(best_match["opponent"]) if best_match is not None else "—",
        compact_currency(float(best_match["revenue"])) if best_match is not None else None,
    )

    section_label("Sales mix")
    left, right = st.columns(2)
    with left:
        type_sales = (
            filtered_tickets.groupby("ticket_type", as_index=False)
            .agg(revenue=("total_revenue", "sum"), tickets_sold=("quantity", "sum"))
            .sort_values("revenue")
        )
        type_figure = px.bar(
            type_sales,
            x="revenue",
            y="ticket_type",
            orientation="h",
            text_auto="$.3s",
            title="Revenue by ticket type",
            labels={"revenue": "Ticket revenue", "ticket_type": ""},
            color="ticket_type",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        type_figure.update_layout(showlegend=False)
        type_figure.update_xaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(style_chart(type_figure), use_container_width=True)
    with right:
        segment_sales = (
            filtered_tickets.groupby("customer_segment", as_index=False)["quantity"]
            .sum()
            .sort_values("quantity", ascending=False)
        )
        segment_figure = px.bar(
            segment_sales,
            x="customer_segment",
            y="quantity",
            text_auto=",",
            title="Tickets sold by customer segment",
            labels={"customer_segment": "", "quantity": "Tickets sold"},
            color="customer_segment",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        segment_figure.update_layout(showlegend=False)
        segment_figure.update_xaxes(tickangle=-24)
        st.plotly_chart(style_chart(segment_figure), use_container_width=True)

    section_label("Match-by-match inventory")
    inventory_chart = px.bar(
        match_sales,
        x="opponent",
        y="inventory_sold_pct",
        color="inventory_sold_pct",
        color_continuous_scale=["#DDEAF2", SKY, BLUE],
        text_auto=".1f",
        title="Inventory sold percentage by match",
        labels={"opponent": "", "inventory_sold_pct": "Inventory sold (%)"},
        hover_data={"tickets_sold": ":,.0f", "capacity": ":,.0f", "revenue": ":$,.0f"},
    )
    inventory_chart.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    inventory_chart.update_layout(coloraxis_showscale=False)
    inventory_chart.update_xaxes(tickangle=-30)
    inventory_chart.update_yaxes(range=[0, max(100, match_sales["inventory_sold_pct"].max() * 1.12)])
    st.plotly_chart(style_chart(inventory_chart, 410), use_container_width=True)

    table = match_sales[
        ["match_date", "opponent", "competition", "capacity", "tickets_sold", "inventory_sold_pct", "revenue"]
    ].copy()
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "match_date": st.column_config.DateColumn("Match date", format="MMM D, YYYY"),
            "opponent": "Opponent",
            "competition": "Competition",
            "capacity": st.column_config.NumberColumn("Capacity", format="%d"),
            "tickets_sold": st.column_config.NumberColumn("Sold", format="%d"),
            "inventory_sold_pct": st.column_config.ProgressColumn(
                "Inventory sold", format="%.1f%%", min_value=0, max_value=100
            ),
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
        },
    )


def render_fan_engagement() -> None:
    hero(
        "Fan Engagement",
        "Turnstile behavior and CRM composition reveal who shows up—and where engagement can grow.",
    )
    issued = filtered_attendance["tickets_issued"].sum()
    scanned = filtered_attendance["tickets_scanned"].sum()
    rate = 100 * scanned / issued if issued else 0
    full_scan = (filtered_attendance["attendance_status"] == "Full Scan").mean() * 100 if len(filtered_attendance) else 0
    active_buyers = filtered_tickets["customer_id"].nunique()

    columns = st.columns(4)
    columns[0].metric("Tickets scanned", f"{scanned:,.0f}")
    columns[1].metric("Matchday scan rate", f"{rate:.1f}%")
    columns[2].metric("Full-order scan rate", f"{full_scan:.1f}%")
    columns[3].metric("Active buyers", f"{active_buyers:,.0f}")

    section_label("Attendance performance")
    scan_chart = px.bar(
        match_attendance,
        x="opponent",
        y="scan_rate",
        color="scan_rate",
        color_continuous_scale=["#F8D7DA", GOLD, TEAL],
        text_auto=".1f",
        title="Attendance scan rate by match",
        labels={"opponent": "", "scan_rate": "Scan rate (%)"},
        hover_data={"tickets_issued": ":,.0f", "tickets_scanned": ":,.0f"},
    )
    scan_chart.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    scan_chart.update_layout(coloraxis_showscale=False)
    scan_chart.update_xaxes(tickangle=-30)
    scan_chart.update_yaxes(range=[0, 100])
    st.plotly_chart(style_chart(scan_chart, 420), use_container_width=True)

    left, right = st.columns([1, 1.25])
    with left:
        segment_counts = (
            customers[customers["customer_segment"].isin(selected_segments)]
            .groupby("customer_segment", as_index=False)
            .size()
            .rename(columns={"size": "customers"})
        )
        segment_donut = px.pie(
            segment_counts,
            names="customer_segment",
            values="customers",
            hole=0.56,
            title="Customer segment distribution",
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        segment_donut.update_traces(textinfo="percent", hovertemplate="%{label}<br>%{value:,.0f} fans<extra></extra>")
        st.plotly_chart(style_chart(segment_donut), use_container_width=True)
    with right:
        attendance_with_type = filtered_attendance.merge(
            tickets[["ticket_id", "ticket_type"]], on="ticket_id", how="left"
        )
        by_type = (
            attendance_with_type.groupby("ticket_type", as_index=False)
            .agg(issued=("tickets_issued", "sum"), scanned=("tickets_scanned", "sum"))
        )
        by_type["scan_rate"] = 100 * by_type["scanned"] / by_type["issued"]
        type_scan = px.bar(
            by_type.sort_values("scan_rate"),
            x="scan_rate",
            y="ticket_type",
            orientation="h",
            color="ticket_type",
            text_auto=".1f",
            title="Scan rate by ticket type",
            labels={"scan_rate": "Scan rate (%)", "ticket_type": ""},
            color_discrete_sequence=COLOR_SEQUENCE,
        )
        type_scan.update_traces(texttemplate="%{x:.1f}%")
        type_scan.update_layout(showlegend=False)
        type_scan.update_xaxes(range=[0, 100])
        st.plotly_chart(style_chart(type_scan), use_container_width=True)


def campaign_performance_frame() -> pd.DataFrame:
    grouped = (
        conversions.groupby("campaign_id", as_index=False)
        .agg(
            sends=("sent", "sum"),
            opens=("opened", "sum"),
            clicks=("clicked", "sum"),
            conversions=("converted", "sum"),
            revenue=("revenue", "sum"),
        )
    )
    frame = campaigns.merge(grouped, on="campaign_id", how="left")
    frame["open_rate"] = 100 * frame["opens"] / frame["sends"]
    frame["click_rate"] = 100 * frame["clicks"] / frame["sends"]
    frame["conversion_rate"] = 100 * frame["conversions"] / frame["sends"]
    frame["roas"] = frame["revenue"] / frame["budget"]
    return frame


def render_campaigns() -> None:
    hero(
        "Campaign Performance",
        "Channel and campaign funnel results connect fan outreach to conversion and attributed revenue.",
    )
    performance = campaign_performance_frame()
    available_channels = sorted(performance["channel"].unique())
    chosen_channels = st.multiselect(
        "Campaign channels",
        available_channels,
        default=available_channels,
        key="campaign_channel_filter",
    )
    performance = performance[performance["channel"].isin(chosen_channels)]
    selected_campaigns = conversions[
        conversions["campaign_id"].isin(performance["campaign_id"])
    ]
    sends = selected_campaigns["sent"].sum()
    opens = selected_campaigns["opened"].sum()
    clicks = selected_campaigns["clicked"].sum()
    converted = selected_campaigns["converted"].sum()
    revenue = selected_campaigns["revenue"].sum()
    conversion_rate = 100 * converted / sends if sends else 0

    primary_columns = st.columns(3)
    primary_columns[0].metric("Campaign sends", f"{sends:,.0f}")
    primary_columns[1].metric("Open rate", f"{100 * opens / sends if sends else 0:.1f}%")
    primary_columns[2].metric("Click rate", f"{100 * clicks / sends if sends else 0:.1f}%")
    secondary_columns = st.columns(2)
    secondary_columns[0].metric("Conversion rate", f"{conversion_rate:.2f}%")
    secondary_columns[1].metric("Attributed revenue", compact_currency(revenue))

    section_label("Channel comparison")
    left, right = st.columns([1, 1.35])
    with left:
        by_channel = (
            performance.groupby("channel", as_index=False)
            .agg(sends=("sends", "sum"), conversions=("conversions", "sum"), revenue=("revenue", "sum"))
        )
        by_channel["conversion_rate"] = 100 * by_channel["conversions"] / by_channel["sends"]
        channel_chart = px.bar(
            by_channel,
            x="channel",
            y="conversion_rate",
            color="channel",
            text_auto=".2f",
            title="Campaign conversion by channel",
            labels={"channel": "", "conversion_rate": "Conversion rate (%)"},
            color_discrete_map={"Email": BLUE, "SMS": TEAL, "Social": GOLD},
        )
        channel_chart.update_traces(texttemplate="%{y:.2f}%", textposition="outside")
        channel_chart.update_layout(showlegend=False)
        st.plotly_chart(style_chart(channel_chart), use_container_width=True)
    with right:
        campaign_revenue = performance.sort_values("revenue", ascending=True).tail(10)
        revenue_chart = px.bar(
            campaign_revenue,
            x="revenue",
            y="campaign_name",
            orientation="h",
            color="channel",
            text_auto="$.3s",
            title="Revenue by campaign — top 10",
            labels={"revenue": "Attributed revenue", "campaign_name": ""},
            color_discrete_map={"Email": BLUE, "SMS": TEAL, "Social": GOLD},
        )
        revenue_chart.update_xaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(style_chart(revenue_chart), use_container_width=True)

    section_label("Campaign scorecard")
    scorecard = performance[
        [
            "campaign_name", "channel", "target_segment", "sends", "open_rate",
            "click_rate", "conversion_rate", "revenue", "roas",
        ]
    ].sort_values("revenue", ascending=False)
    st.dataframe(
        scorecard,
        use_container_width=True,
        hide_index=True,
        column_config={
            "campaign_name": "Campaign",
            "channel": "Channel",
            "target_segment": "Target segment",
            "sends": st.column_config.NumberColumn("Sends", format="%d"),
            "open_rate": st.column_config.NumberColumn("Open rate", format="%.1f%%"),
            "click_rate": st.column_config.NumberColumn("Click rate", format="%.1f%%"),
            "conversion_rate": st.column_config.NumberColumn("Conversion", format="%.2f%%"),
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "roas": st.column_config.NumberColumn("ROAS", format="%.2fx"),
        },
    )

    if len(by_channel):
        best_channel = by_channel.loc[by_channel["conversion_rate"].idxmax()]
        insight_card(
            "Channel takeaway",
            f"<b>{best_channel['channel']}</b> leads at {best_channel['conversion_rate']:.2f}% conversion. "
            f"Use it for high-intent deadlines while preserving Email for efficient reach and nurture.",
        )


def render_retention() -> None:
    hero(
        "Retention & Renewals",
        "Renewal propensity, repeat purchase behavior, and lifetime value focus outreach on the right fans.",
    )
    customer_filter = customers[customers["customer_segment"].isin(selected_segments)].copy()
    match_counts = (
        filtered_tickets.groupby("customer_id")["match_id"].nunique().rename("matches_bought")
    )
    customer_filter = customer_filter.merge(match_counts, on="customer_id", how="left")
    customer_filter["matches_bought"] = customer_filter["matches_bought"].fillna(0)
    active = customer_filter[customer_filter["matches_bought"] > 0]
    repeat_rate = 100 * (active["matches_bought"] > 1).mean() if len(active) else 0
    avg_score = customer_filter["renewal_likelihood"].mean() if len(customer_filter) else 0
    high_intent = (customer_filter["renewal_likelihood"] >= 75).sum()
    season_members = customer_filter[
        customer_filter["customer_segment"] == "Season Ticket Member"
    ]
    actual_renewal = (
        100 * season_members["renewed_season_ticket"].fillna(0).mean()
        if len(season_members)
        else 0
    )

    columns = st.columns(4)
    columns[0].metric("Repeat buyer rate", f"{repeat_rate:.1f}%")
    columns[1].metric("Avg. renewal likelihood", f"{avg_score:.1f}")
    columns[2].metric("High-intent fans", f"{high_intent:,.0f}", "Score of 75+")
    columns[3].metric("Member renewal rate", f"{actual_renewal:.1f}%")

    section_label("Renewal pipeline")
    left, right = st.columns([1.25, 1])
    with left:
        segment_renewal = (
            customer_filter.groupby("customer_segment", as_index=False)
            .agg(
                avg_renewal_likelihood=("renewal_likelihood", "mean"),
                customers=("customer_id", "nunique"),
                lifetime_value=("lifetime_value", "sum"),
            )
            .sort_values("avg_renewal_likelihood", ascending=False)
        )
        renewal_chart = px.bar(
            segment_renewal,
            x="customer_segment",
            y="avg_renewal_likelihood",
            color="avg_renewal_likelihood",
            color_continuous_scale=["#F6C6C6", GOLD, TEAL],
            text_auto=".1f",
            title="Renewal likelihood by customer segment",
            labels={"customer_segment": "", "avg_renewal_likelihood": "Average score"},
            hover_data={"customers": ":,.0f", "lifetime_value": ":$,.0f"},
        )
        renewal_chart.update_layout(coloraxis_showscale=False)
        renewal_chart.update_traces(textposition="outside")
        renewal_chart.update_xaxes(tickangle=-25)
        renewal_chart.update_yaxes(range=[0, 100])
        st.plotly_chart(style_chart(renewal_chart), use_container_width=True)
    with right:
        customer_filter["likelihood_tier"] = pd.cut(
            customer_filter["renewal_likelihood"],
            bins=[0, 50, 75, 100],
            labels=["Low", "Medium", "High"],
            include_lowest=True,
        )
        tiers = (
            customer_filter.groupby("likelihood_tier", observed=True, as_index=False)
            .agg(customers=("customer_id", "nunique"), lifetime_value=("lifetime_value", "sum"))
        )
        tier_chart = px.pie(
            tiers,
            names="likelihood_tier",
            values="customers",
            hole=0.56,
            title="Renewal likelihood tiers",
            color="likelihood_tier",
            color_discrete_map={"High": TEAL, "Medium": GOLD, "Low": RED},
        )
        tier_chart.update_traces(textinfo="label+percent")
        st.plotly_chart(style_chart(tier_chart), use_container_width=True)

    section_label("Retention actions")
    highest = segment_renewal.iloc[0]
    largest_value = segment_renewal.sort_values("lifetime_value", ascending=False).iloc[0]
    action_columns = st.columns(3)
    with action_columns[0]:
        insight_card(
            "Most likely to renew",
            f"<b>{highest['customer_segment']}</b> leads with an average likelihood score of "
            f"{highest['avg_renewal_likelihood']:.1f}.",
        )
    with action_columns[1]:
        insight_card(
            "Value protection",
            f"<b>{largest_value['customer_segment']}</b> represents the largest lifetime-value pool "
            f"at {compact_currency(largest_value['lifetime_value'])}.",
        )
    with action_columns[2]:
        at_risk = customer_filter[
            (customer_filter["renewal_likelihood"] < 50)
            & (customer_filter["lifetime_value"] >= customer_filter["lifetime_value"].quantile(0.75))
        ]
        insight_card(
            "Priority outreach",
            f"<b>{len(at_risk):,} high-value fans</b> score below 50. Assign this group to personalized "
            f"win-back and sales-rep follow-up.",
        )

    st.markdown("#### High-value fans needing attention")
    risk_table = (
        customer_filter[
            (customer_filter["renewal_likelihood"] < 60)
            & (customer_filter["lifetime_value"] >= customer_filter["lifetime_value"].quantile(0.70))
        ][
            [
                "customer_id", "first_name", "last_name", "customer_segment",
                "matches_bought", "lifetime_value", "renewal_likelihood", "preferred_channel",
            ]
        ]
        .sort_values(["renewal_likelihood", "lifetime_value"], ascending=[True, False])
        .head(30)
    )
    st.dataframe(
        risk_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "customer_id": "Customer ID",
            "first_name": "First",
            "last_name": "Last",
            "customer_segment": "Segment",
            "matches_bought": st.column_config.NumberColumn("Matches", format="%d"),
            "lifetime_value": st.column_config.NumberColumn("Lifetime value", format="$%.2f"),
            "renewal_likelihood": st.column_config.ProgressColumn(
                "Renewal score", format="%.1f", min_value=0, max_value=100
            ),
            "preferred_channel": "Preferred channel",
        },
    )


if page == "Executive Overview":
    render_overview()
elif page == "Ticket Sales":
    render_ticket_sales()
elif page == "Fan Engagement":
    render_fan_engagement()
elif page == "Campaign Performance":
    render_campaigns()
else:
    render_retention()
