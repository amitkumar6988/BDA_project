# SmartReco

## What the project is

SmartReco is a local batch analytics and recommendation application for the
UCI Online Retail dataset. It turns historical invoices into customer-product
interactions, learns implicit product preferences with Apache Spark MLlib ALS,
and presents the results in a Streamlit dashboard.

The project is intended as a Big Data Analytics prototype and teaching/demo
application, not as a production recommender service. It runs the complete
workflow locally, persists intermediate results as Parquet and JSON, and
serves those persisted results without retraining when the dashboard opens.

The application provides:

- Data cleaning and data-quality reporting for retail transactions
- Customer-product interaction strengths based on positive purchase quantity
- Implicit ALS recommendations and a popularity fallback
- Precision@K and Recall@K evaluation using a per-customer temporal holdout
- Product co-purchase associations with support, confidence, and lift
- Streamlit views for overview metrics, product analytics, recommendations,
  evaluation, and associations

## Architecture

```mermaid
flowchart LR
    A[Online Retail.xlsx] --> B[Data loader\nopenpyxl + Spark schema]
    B --> C[Data cleaning\nvalidation, returns, duplicates]
    C --> D[Purchase data]
    D --> E[Interaction builder\ncustomer-product aggregation]
    E --> F[Stable integer IDs]
    F --> G[Per-customer temporal split]
    G --> H[Implicit ALS]
    H --> I[Top-k recommendations]
    I --> J[Remove purchased items\nand re-rank]
    J --> K[Recommendation Parquet]
    G --> L[Precision@K / Recall@K]
    D --> M[Product associations]
    D --> N[Summary and quality metrics]
    K --> O[Streamlit dashboard]
    L --> P[Evaluation JSON]
    M --> O
    N --> O
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| `src/data_loader.py` | Reads the Excel workbook with `openpyxl` and creates a typed Spark DataFrame. |
| `src/data_cleaning.py` | Validates fields, removes invalid purchases, cancellations, returns, and duplicate rows. |
| `src/feature_engineering.py` | Aggregates purchases by customer and product, calculates interaction strength, and assigns stable IDs. |
| `src/evaluation.py` | Creates the latest-item-per-customer holdout and calculates ranking metrics. |
| `src/recommendation_model.py` | Trains implicit ALS, creates recommendations, removes purchased products, and re-ranks results. |
| `src/association_rules.py` | Calculates product co-purchase associations. |
| `src/pipeline.py` | Orchestrates the batch workflow and writes generated outputs. |
| `app.py` | Reads persisted outputs and displays the Streamlit dashboard. |

The main entry point is `main.py`. It creates a Spark session and calls the
pipeline. The dashboard in `app.py` is a read-only presentation layer: it
does not retrain ALS.

## Dataset and schema

Place `Online Retail.xlsx` in `dataset/`. The inspected workbook contains 541,909 rows and these columns: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`. The original workbook is never written to.

## Windows setup

Use Python 3.10+ and Java 17. Keep the project in a normal local folder when
possible; OneDrive can mark generated Parquet folders as read-only or
reparse points and prevent Spark from replacing them.

In the VS Code terminal:

```powershell
python -m venv bdavenv
.\bdavenv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python main.py
python -m streamlit run app.py
```

Always use `python -m pip`, `python -m pytest`, and `python -m streamlit` so
that installation, testing, and execution use the same interpreter. Confirm
that PySpark is available before running the project:

```powershell
python -c "import sys, pyspark; print(sys.executable); print(pyspark.__version__)"
java -version
```

The existing environment uses Python 3.13 and Java 17. The loader uses `openpyxl` and an explicit schema, so no Spark Excel connector is required. Parquet outputs are written with a streaming PyArrow fallback, so Windows does not require Hadoop's `winutils.exe` or `HADOOP_HOME`.

## Running order and troubleshooting

Run the tests first, then run `main.py` to generate all Parquet and JSON
outputs, and only then start Streamlit. The dashboard checks that all required
generated files exist; if they are incomplete, it shows source-data analytics
instead of personalized recommendations.

If the pipeline reports `WinError 5` while replacing a folder under
`data/processed/`, close running Spark or Streamlit processes and move the
project outside OneDrive before rerunning. Do not start the dashboard from a
partially generated output directory.

## Outputs

Generated files are under `data/processed/`, `data/recommendations/`, and `output/`: cleaned purchases, aggregated interactions, product associations, evaluation metrics, summary statistics, and data-quality JSON. Generated directories use overwrite mode on each run.

## Method and limitations

Positive, non-cancelled lines with valid customer/product IDs, dates, quantities, and prices are retained. Invoice numbers beginning with `C`, negative quantities, invalid prices, missing identifiers, and duplicates are reported and excluded from training. Returns are not confirmed negative feedback. ALS uses stable integer mappings and implicit feedback. Evaluation holds out each eligible customer's latest product interaction, trains on the remaining interactions, and re-ranks recommendations after removing products already purchased by that customer. Customers with only one interaction are excluded from evaluation because they have no training history. Precision@K and Recall@K count observed future purchases only, so unobserved products are unknown rather than confirmed negatives. Association support is basket share, confidence is conditional co-purchase probability, and lift compares that probability with independence.
