from pathlib import Path
import pandas as pd
from api.app.data_access.Controlled_file import DatasetRepository


OUTPUT_PATH = Path("data/processed/kpi_snapshot.parquet")


DATASET_NAMES = [
    "customers",
    "products",
    "transactions",
    "customer_support",
    "marketing_campaigns",
]


def load_datasets(
        repository: DatasetRepository,
) -> dict[str, pd.DataFrame]:
    """Load approved VANTAGE360 datasets through the data-access layer."""

    datasets = {}

    for dataset_name in DATASET_NAMES:
        data = repository.read_dataset(dataset_name)
        datasets[dataset_name] = pd.DataFrame(data)

    return datasets


def prepare_data(
        datasets: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Convert numeric fields from CSV strings to numeric values."""

    transactions = datasets["transactions"].copy()
    marketing = datasets["marketing_campaigns"].copy()
    support = datasets["customer_support"].copy()

    transaction_numeric_columns = [
        "quantity",
        "unit_price",
        "discount_pct",
        "final_amount",
        "delivery_days",
    ]

    for column in transaction_numeric_columns:
        transactions[column] = pd.to_numeric(
            transactions[column],
            errors="coerce",
        )

    marketing_numeric_columns = [
        "budget_inr",
        "impressions",
        "clicks",
        "conversions",
        "revenue_generated",
    ]

    for column in marketing_numeric_columns:
        marketing[column] = pd.to_numeric(
            marketing[column],
            errors="coerce",
        )

    support_numeric_columns = [
        "csat_score",
        "response_time_hrs",
    ]

    for column in support_numeric_columns:
        support[column] = pd.to_numeric(
            support[column],
            errors="coerce",
        )

    datasets["transactions"] = transactions
    datasets["marketing_campaigns"] = marketing
    datasets["customer_support"] = support

    return datasets


# Answers:
# Which regions are driving revenue?


def calculate_regional_revenue(
        transactions: pd.DataFrame,
        customers: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate realized revenue by customer region."""

    delivered = transactions[
        transactions["status"] == "Delivered"
        ].copy()

    merged = delivered.merge(
        customers[["customer_id", "region"]],
        on="customer_id",
        how="left",
    )

    result = (
        merged.groupby("region", as_index=False)
        .agg(
            revenue=("final_amount", "sum"),
            orders=("transaction_id", "count"),
        )
    )

    return result


# Answers:
# Which products have the highest return rates?


def calculate_product_returns(
        transactions: pd.DataFrame,
        products: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate return rates by product."""

    merged = transactions.merge(
        products[
            ["product_id", "product_name", "category"]
        ],
        on="product_id",
        how="left",
    )

    result = (
        merged.groupby(
            [
                "product_id",
                "product_name",
                "category",
            ],
            as_index=False,
        )
        .agg(
            total_orders=("transaction_id", "count"),
            returned_orders=(
                "status",
                lambda values: (
                        values == "Returned"
                ).sum(),
            ),
        )
    )

    result["return_rate"] = (
            result["returned_orders"]
            / result["total_orders"]
    )

    return result


# Answers:
# Which marketing channels are producing
# the strongest ROI?


def calculate_marketing_roi(
        marketing: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate revenue-to-budget ROI proxy by campaign type."""

    result = (
        marketing.groupby(
            "campaign_type",
            as_index=False,
        )
        .agg(
            budget_inr=("budget_inr", "sum"),
            revenue_generated=(
                "revenue_generated",
                "sum",
            ),
        )
    )

    result["roi_proxy"] = (
            result["revenue_generated"]
            / result["budget_inr"].replace(0, pd.NA)
    )

    return result


# Answers:
# What are the most important operational issues?


def calculate_operational_issues(
        support: pd.DataFrame,
) -> pd.DataFrame:
    """Calculate operational support indicators."""

    result = (
        support.groupby(
            "issue_type",
            as_index=False,
        )
        .agg(
            ticket_count=("ticket_id", "count"),
            avg_response_time_hrs=(
                "response_time_hrs",
                "mean",
            ),
            avg_csat=("csat_score", "mean"),
            escalated_tickets=(
                "resolution",
                lambda values: (
                        values == "Escalated"
                ).sum(),
            ),
        )
    )

    result["escalation_rate"] = (
            result["escalated_tickets"]
            / result["ticket_count"]
    )

    return result


def create_kpi_snapshot(
        regional_revenue: pd.DataFrame,
        product_returns: pd.DataFrame,
        marketing_roi: pd.DataFrame,
        operational_issues: pd.DataFrame,
) -> pd.DataFrame:
    """Create one standardized KPI snapshot."""

    rows = []

    # Regional revenue
    for _, row in regional_revenue.iterrows():
        rows.append(
            {
                "dimension": "region",
                "dimension_value": row["region"],
                "metric": "revenue",
                "value": row["revenue"],
            }
        )

        rows.append(
            {
                "dimension": "region",
                "dimension_value": row["region"],
                "metric": "orders",
                "value": row["orders"],
            }
        )

    # Product returns
    for _, row in product_returns.iterrows():
        rows.append(
            {
                "dimension": "product",
                "dimension_value": row["product_id"],
                "metric": "return_rate",
                "value": row["return_rate"],
            }
        )

        rows.append(
            {
                "dimension": "product",
                "dimension_value": row["product_id"],
                "metric": "returned_orders",
                "value": row["returned_orders"],
            }
        )

    # Marketing ROI
    for _, row in marketing_roi.iterrows():
        rows.append(
            {
                "dimension": "campaign_type",
                "dimension_value": row["campaign_type"],
                "metric": "roi_proxy",
                "value": row["roi_proxy"],
            }
        )

        rows.append(
            {
                "dimension": "campaign_type",
                "dimension_value": row["campaign_type"],
                "metric": "revenue_generated",
                "value": row["revenue_generated"],
            }
        )

    # Operational issues
    for _, row in operational_issues.iterrows():
        rows.append(
            {
                "dimension": "issue_type",
                "dimension_value": row["issue_type"],
                "metric": "ticket_count",
                "value": row["ticket_count"],
            }
        )

        rows.append(
            {
                "dimension": "issue_type",
                "dimension_value": row["issue_type"],
                "metric": "avg_response_time_hrs",
                "value": row["avg_response_time_hrs"],
            }
        )

        rows.append(
            {
                "dimension": "issue_type",
                "dimension_value": row["issue_type"],
                "metric": "avg_csat",
                "value": row["avg_csat"],
            }
        )

        rows.append(
            {
                "dimension": "issue_type",
                "dimension_value": row["issue_type"],
                "metric": "escalation_rate",
                "value": row["escalation_rate"],
            }
        )

    snapshot = pd.DataFrame(rows)

    if snapshot.empty:
        raise ValueError(
            "KPI snapshot cannot be empty."
        )

    snapshot["snapshot_date"] = (
        pd.Timestamp.now().normalize()
    )

    snapshot["value"] = pd.to_numeric(
        snapshot["value"],
        errors="coerce",
    )

    return snapshot[
        [
            "snapshot_date",
            "dimension",
            "dimension_value",
            "metric",
            "value",
        ]
    ]


def run_kpi_snapshot(
        repository: DatasetRepository,
        output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:
    """Run the complete VANTAGE360 KPI snapshot workflow."""

    # 1. Load approved datasets
    datasets = load_datasets(repository)

    # 2. Prepare data types
    datasets = prepare_data(datasets)

    # 3. Calculate BI metrics
    regional_revenue = calculate_regional_revenue(
        datasets["transactions"],
        datasets["customers"],
    )

    product_returns = calculate_product_returns(
        datasets["transactions"],
        datasets["products"],
    )

    marketing_roi = calculate_marketing_roi(
        datasets["marketing_campaigns"],
    )

    operational_issues = calculate_operational_issues(
        datasets["customer_support"],
    )

    # 4. Create standardized snapshot
    snapshot = create_kpi_snapshot(
        regional_revenue,
        product_returns,
        marketing_roi,
        operational_issues,
    )

    # 5. Save snapshot
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot.to_parquet(
        output_path,
        index=False,
    )

    return snapshot



