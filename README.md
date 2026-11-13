# SmartReco

SmartReco is a local Apache Spark prototype for product recommendations using the UCI Online Retail workbook. It cleans purchase transactions, creates implicit customer-product strengths (`log1p(total positive quantity)`), trains Spark MLlib implicit ALS, evaluates future interactions, computes a popularity fallback, and calculates product co-purchase associations.

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
