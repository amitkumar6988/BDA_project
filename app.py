import json
from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATASET = ROOT / "dataset" / "Online Retail.xlsx"
OUTPUT = ROOT / "output"
RECS = ROOT / "data" / "recommendations" / "all_customers"
PROCESSED = ROOT / "data" / "processed"

st.set_page_config(page_title="SmartReco", layout="wide")
st.title("SmartReco: E-Commerce Recommendations")
evaluation = OUTPUT / "evaluation.json"
summary = OUTPUT / "summary.json"
generated_parquet_dirs = (
    PROCESSED / "cleaned_purchases",
    PROCESSED / "interactions",
    RECS,
    PROCESSED / "product_associations",
)


def generated_outputs_ready() -> bool:
    return (
        evaluation.exists()
        and summary.exists()
        and (OUTPUT / "data_quality.json").exists()
        and all(
            folder.is_dir() and any(folder.glob("*.parquet"))
            for folder in generated_parquet_dirs
        )
    )


@st.cache_data
def load_source() -> pd.DataFrame:
    frame = pd.read_excel(DATASET)
    frame["InvoiceNo"] = frame["InvoiceNo"].astype("string").str.strip()
    frame["StockCode"] = frame["StockCode"].astype("string").str.strip()
    frame["Description"] = frame["Description"].astype("string").str.strip()
    frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"], errors="coerce")
    frame["Amount"] = frame["Quantity"] * frame["UnitPrice"]
    return frame


@st.cache_data
def load_parquet(folder: Path) -> pd.DataFrame:
    return pd.read_parquet(folder)


def show_source_fallback() -> None:
    st.info(
        "Generated Spark outputs are not available yet. Showing live analytics from "
        "`dataset/Online Retail.xlsx`; run `python main.py` for ALS recommendations."
    )
    frame = load_source()
    valid = frame[
        frame["CustomerID"].notna()
        & frame["StockCode"].notna()
        & (frame["Quantity"] > 0)
        & (frame["UnitPrice"] > 0)
        & ~frame["InvoiceNo"].str.upper().str.startswith("C", na=False)
    ].copy()
    cols = st.columns(4)
    values = {
        "Transactions": valid["InvoiceNo"].nunique(),
        "Customers": valid["CustomerID"].nunique(),
        "Products": valid["StockCode"].nunique(),
        "Revenue": valid["Amount"].sum(),
    }
    for col, (label, value) in zip(cols, values.items()):
        col.metric(label, f"£{value:,.2f}" if label == "Revenue" else f"{value:,}")
    left, right = st.columns(2)
    with left:
        st.subheader("Best-selling products")
        popular = (
            valid.groupby(["StockCode", "Description"], dropna=False)["Quantity"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="quantity_sold")
        )
        popular["product"] = popular["StockCode"] + " - " + popular["Description"].fillna("Unknown")
        st.bar_chart(popular.set_index("product")[["quantity_sold"]])
    with right:
        st.subheader("Revenue by product")
        revenue = (
            valid.groupby(["StockCode", "Description"], dropna=False)["Amount"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="revenue")
        )
        revenue["product"] = revenue["StockCode"] + " - " + revenue["Description"].fillna("Unknown")
        st.bar_chart(revenue.set_index("product")[["revenue"]])
    st.subheader("Data quality")
    st.json({
        "input_rows": int(len(frame)),
        "missing_customer_ids": int(frame["CustomerID"].isna().sum()),
        "cancellations_or_returns": int(
            (frame["InvoiceNo"].str.upper().str.startswith("C", na=False) | (frame["Quantity"] < 0)).sum()
        ),
        "retained_positive_purchases": int(len(valid)),
    })
    st.caption("This fallback does not train ALS and does not claim personalized recommendations.")


if not generated_outputs_ready():
    if DATASET.exists():
        show_source_fallback()
    else:
        st.error("Dataset not found. Place Online Retail.xlsx in the dataset folder.")
    st.stop()

overview = json.loads(summary.read_text(encoding="utf-8"))
quality = json.loads((OUTPUT / "data_quality.json").read_text(encoding="utf-8"))
cols = st.columns(4)
for col, label in zip(cols, ("transactions", "customers", "products", "revenue")):
    col.metric(label.title(), f"{overview.get(label, 0):,.2f}" if label == "revenue" else f"{overview.get(label, 0):,}")

cleaned = load_parquet(PROCESSED / "cleaned_purchases")
interactions = load_parquet(PROCESSED / "interactions")
recommendations = load_parquet(RECS)
associations = load_parquet(PROCESSED / "product_associations")
cleaned["InvoiceDate"] = pd.to_datetime(cleaned["invoice_date"], errors="coerce")

overview_tab, analytics_tab, recommendations_tab, evaluation_tab = st.tabs(
    ["Overview", "Product analytics", "Personalized recommendations", "Evaluation & associations"]
)
with overview_tab:
    st.subheader("Data quality")
    st.json(quality)
    st.subheader("Revenue over time")
    monthly = cleaned.set_index("InvoiceDate").resample("MS")["amount"].sum().rename("revenue")
    st.line_chart(monthly)

with analytics_tab:
    left, right = st.columns(2)
    with left:
        st.subheader("Best-selling products")
        popular = (
            cleaned.groupby(["stock_code", "description"], dropna=False)["quantity"]
            .sum().nlargest(10).reset_index(name="quantity_sold")
        )
        popular["product"] = popular["stock_code"].astype(str) + " - " + popular["description"].fillna("Unknown")
        st.bar_chart(popular.set_index("product")[["quantity_sold"]])
    with right:
        st.subheader("Top products by revenue")
        revenue = (
            cleaned.groupby(["stock_code", "description"], dropna=False)["amount"]
            .sum().nlargest(10).reset_index(name="revenue")
        )
        revenue["product"] = revenue["stock_code"].astype(str) + " - " + revenue["description"].fillna("Unknown")
        st.bar_chart(revenue.set_index("product")[["revenue"]])
    st.subheader("Customer purchase volume")
    customer_volume = cleaned.groupby("customer_id")["amount"].sum().nlargest(20).rename("spend")
    st.bar_chart(customer_volume)

with recommendations_tab:
    st.subheader("Personalized top-10 recommendations")
    customer_map = interactions[["customer_id", "user"]].drop_duplicates().sort_values("customer_id")
    customer = st.selectbox("Select a customer", customer_map["customer_id"].tolist(), format_func=str)
    selected_user = int(customer_map.loc[customer_map["customer_id"] == customer, "user"].iloc[0])
    selected = recommendations[recommendations["user"] == selected_user].sort_values("rank").head(10).copy()
    if selected.empty:
        st.info("No generated recommendations are available for this customer.")
    else:
        st.dataframe(
            selected[["rank", "stock_code", "description", "score"]].rename(
                columns={"rank": "Rank", "stock_code": "Product", "description": "Description", "score": "Score"}
            ),
            hide_index=True,
            use_container_width=True,
        )

with evaluation_tab:
    st.subheader("Model evaluation")
    st.json(json.loads(evaluation.read_text(encoding="utf-8")))
    st.caption("Precision and recall count observed future purchases; unobserved products are not treated as confirmed negatives.")
    st.subheader("Frequently co-purchased products")
    if associations.empty:
        st.info("No association results are available.")
    else:
        association_product = st.selectbox("Select a product code", sorted(
            set(associations["product_a"]) | set(associations["product_b"])
        ))
        related = associations[
            (associations["product_a"] == association_product)
            | (associations["product_b"] == association_product)
        ].sort_values("lift", ascending=False).head(10)
        st.dataframe(related, hide_index=True, use_container_width=True)

st.caption("Recommendations are read from persisted Parquet output; the dashboard never retrains the model.")
