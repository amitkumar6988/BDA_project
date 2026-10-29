# SmartReco

SmartReco is a local Apache Spark prototype for product recommendations using the UCI Online Retail workbook. It cleans purchase transactions, creates implicit customer-product strengths (`log1p(total positive quantity)`), trains Spark MLlib implicit ALS, evaluates future interactions, computes a popularity fallback, and calculates product co-purchase associations.

## Dataset and schema

Place `Online Retail.xlsx` in `dataset/`. The inspected workbook contains 541,909 rows and these columns: `InvoiceNo`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`. The original workbook is never written to.

## Windows setup

Use Python 3.10+ and Java 17. In the VS Code terminal:

```powershell
python -m venv bdavenv
.\bdavenv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
streamlit run app.py
python -m pytest -q
```

The existing environment uses Python 3.13 and Java 17. The loader uses `openpyxl` and an explicit schema, so no Spark Excel connector is required. Parquet outputs are written with a streaming PyArrow fallback, so Windows does not require Hadoop's `winutils.exe` or `HADOOP_HOME`.

## Outputs

Generated files are under `data/processed/`, `data/recommendations/`, and `output/`: cleaned purchases, aggregated interactions, product associations, evaluation metrics, summary statistics, and data-quality JSON. Generated directories use overwrite mode on each run.

## Method and limitations

Positive, non-cancelled lines with valid customer/product IDs, dates, quantities, and prices are retained. Invoice numbers beginning with `C`, negative quantities, invalid prices, missing identifiers, and duplicates are reported and excluded from training. Returns are not confirmed negative feedback. ALS uses stable integer mappings, implicit feedback, and a temporal split based on each customer's last purchase; sparse or insufficient data uses popularity fallback. Precision@K and Recall@K count observed future purchases only, so unobserved products are unknown rather than negatives. Association support is basket share, confidence is conditional co-purchase probability, and lift compares that probability with independence.
