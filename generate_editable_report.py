from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "SmartReco_BDA_Project_Report_Editable.docx"


def shade(cell, fill):
    props = cell._tc.get_or_add_tcPr()
    element = OxmlElement("w:shd")
    element.set(qn("w:fill"), fill)
    props.append(element)


def set_cell_text(cell, text, bold=False):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    run = p.add_run(str(text))
    run.bold = bold
    run.font.size = Pt(9)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER


def add_table(doc, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(rows[0]))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = "Table Grid"
    for i, value in enumerate(rows[0]):
        set_cell_text(t.rows[0].cells[i], value, True)
        shade(t.rows[0].cells[i], "D9E5F3")
    for row in rows[1:]:
        cells = t.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)
    if widths:
        for row in t.rows:
            for i, width in enumerate(widths):
                row.cells[i].width = Inches(width)
    doc.add_paragraph()
    return t


def add_para(doc, text, bold_prefix=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(8)
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix):])
    else:
        p.add_run(text)
    return p


def add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    return p


def add_code(doc, text):
    p = doc.add_paragraph()
    p.style = "No Spacing"
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    p.paragraph_format.space_after = Pt(10)
    run = p.add_run(text)
    run.font.name = "Courier New"
    run.font.size = Pt(8)
    return p


def page_title(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(18)
    return p


def page_break(doc):
    doc.add_page_break()


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(0.75)
    sec.left_margin = Inches(0.8)
    sec.right_margin = Inches(0.8)
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    normal.paragraph_format.line_spacing = 1.15

    # Footer page numbers
    footer = sec.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("SmartReco - BDA Mini Project Report | ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)

    # 1. Cover
    for _ in range(2): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("BDA Mini Project Report"); r.bold = True; r.font.size = Pt(24)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("SmartReco - E-Commerce Product Recommendation System"); r.bold = True; r.font.size = Pt(22)
    for text in ["Submitted in fulfilment of the requirements of the", "BDA Mini Project Semester VII in degree of", "Bachelor of Computer Engineering", "", "BY", "", "Vinit Vishwakarma (Roll no. 48)", "Utkarsh Yadav (Roll no. 68)", "Amit Yadav (Roll no. 54)", "", "Guide", "", "Ms. Praniti Patil", "", "Department Of Computer Engineering", "Shree L. R. Tiwari College Of Engineering", "Kanakia Park, Mira Road (E), Thane - 401 107, Maharashtra.", "", "2025-26"]:
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run(text)
    page_break(doc)

    # 2. Approval
    page_title(doc, "BDA Mini Project Report Approval")
    add_para(doc, "This project report entitled \"SmartReco - E-Commerce Product Recommendation System\" by Vinit Vishwakarma (Roll No. 48), Utkarsh Yadav (Roll No. 68), and Amit Yadav (Roll No. 54) is approved for the Mini Project Semester VII project work of B.E CMPN at Shree L. R. Tiwari College of Engineering, in the academic year 2025-2026.")
    for _ in range(9): doc.add_paragraph()
    add_para(doc, "Internal Examiner")
    page_break(doc)

    # 3. Declaration
    page_title(doc, "Declaration")
    add_para(doc, "We declare that this written submission represents our ideas in our own words and where others' ideas or words have been included, we have adequately cited and referenced the original sources. We also declare that we have adhered to all principles of academic honesty and integrity and have not misrepresented, fabricated, or falsified any idea, data, fact, or source in this submission. We understand that any violation of these principles may result in disciplinary action by the Institute.")
    for _ in range(3): doc.add_paragraph()
    add_para(doc, "--------------------------------------\nSignature\n\nVinit Vishwakarma (Roll No. 48)\n\n\n--------------------------------------\nSignature\n\nUtkarsh Yadav (Roll No. 68)\n\n\n--------------------------------------\nSignature\n\nAmit Yadav (Roll No. 54)\n\n\nDate:\n\nPlace:")
    page_break(doc)

    # 4. Contents
    page_title(doc, "Table of Contents")
    for line in ["1. Introduction", "2. System Architecture", "3. Implementation", "4. Results", "5. Conclusion", "6. References"]:
        p = doc.add_paragraph(line); p.paragraph_format.left_indent = Inches(0.3); p.paragraph_format.space_after = Pt(10)
    page_break(doc)

    # 5
    page_title(doc, "1. Introduction")
    add_heading(doc, "1.1 Background", 2)
    add_para(doc, "Modern e-commerce platforms record every invoice, product interaction, quantity, price, and customer purchase. This information is valuable because it describes what customers actually choose, but the volume of transactions makes manual analysis difficult. A customer may have purchased many products, and the next useful product is not always the most globally popular one. A recommendation system uses historical behaviour to rank products that may be relevant to each customer.")
    add_para(doc, "SmartReco is a Big Data Analytics prototype that applies this idea to the UCI Online Retail transaction workbook. The application ingests raw invoice data, cleans invalid and cancelled transactions, aggregates customer-product interactions, learns latent preferences using Spark MLlib implicit ALS, evaluates recommendations against future purchases, and presents the output in a Streamlit dashboard.")
    add_heading(doc, "1.2 Problem Statement", 2)
    add_para(doc, "Retail transaction data usually arrives as a large spreadsheet with mixed identifiers, text, dates, numeric quantities, and monetary values. A business analyst needs to identify reliable purchases, remove returns and duplicates, calculate product demand, discover co-purchased products, and recommend products to individual customers. Spreadsheet-based methods are slow, difficult to reproduce, and unsuitable for ranking thousands of possible products for thousands of customers.")
    add_para(doc, "The project solves this problem by creating a repeatable Spark pipeline that transforms raw retail rows into clean interaction data and persisted recommendation outputs. The dashboard then allows a user to inspect summary statistics, product performance, customer recommendations, association rules, and model evaluation without rerunning the model during every page load.")
    page_break(doc)

    # 6
    page_title(doc, "1. Introduction")
    add_heading(doc, "1.3 Objectives", 2)
    for item in ["Design a complete batch analytics workflow for online retail transactions.", "Clean the source workbook and report missing, duplicate, cancelled, and invalid records.", "Build customer-product implicit feedback strengths from positive purchase quantities.", "Train an implicit ALS model using Spark MLlib and generate top-10 recommendations.", "Evaluate recommendation quality with Precision@K and Recall@K using a temporal split.", "Calculate support, confidence, and lift for frequently co-purchased products.", "Develop a Streamlit dashboard that makes the results easy to inspect."]:
        doc.add_paragraph(item, style="List Bullet")
    add_heading(doc, "1.4 Scope and Limitations", 2)
    add_para(doc, "The system is designed for structured retail transaction data containing invoice number, stock code, description, quantity, invoice date, unit price, customer ID, and country. Positive, non-cancelled transactions with valid identifiers, dates, quantities, and prices are retained. The project treats a purchase as positive implicit feedback. An item that is not observed is not treated as a confirmed negative because the customer may not have seen it, needed it, or had the opportunity to purchase it.")
    add_para(doc, "The current implementation is a local academic prototype. It does not provide live inventory, user authentication, online learning, or a production recommendation API. It is intended to demonstrate the complete analytics lifecycle and to provide a foundation for future model tuning and deployment.")
    page_break(doc)

    # 7
    page_title(doc, "1. Introduction")
    add_heading(doc, "1.5 Relevance to Big Data Analytics", 2)
    add_para(doc, "SmartReco reflects the major characteristics of Big Data at prototype scale. Volume is shown by the 541,909 source rows in the Online Retail workbook. Variety is shown by the combination of invoice identifiers, stock codes, product descriptions, timestamps, customer identifiers, quantities, prices, and country values. Velocity is represented by a repeatable batch pipeline that can process the workbook and refresh the generated outputs. Value is created by converting raw rows into recommendations and product relationships that can support cross-selling and merchandising decisions.")
    add_para(doc, "The project follows the analytics lifecycle of ingestion, validation, cleaning, feature engineering, model training, evaluation, association analysis, output persistence, and visualisation. Apache Spark is used for DataFrame transformations and MLlib modelling, while PyArrow is used to write Parquet outputs in a Windows-friendly way without requiring Hadoop winutils.exe.")
    add_heading(doc, "1.6 Organisation of the Report", 2)
    add_para(doc, "Section 2 describes the system architecture, data flow, input schema, recommendation model, and generated outputs. Section 3 explains the implementation modules and technologies. Section 4 presents the data-quality results, product analytics, recommendations, evaluation metrics, associations, and dashboard modules. Section 5 concludes the work and lists future scope. Section 6 provides the references used during development and documentation.")
    page_break(doc)

    # 8
    page_title(doc, "2. System Architecture")
    add_heading(doc, "2.1 Architectural Overview", 2)
    add_para(doc, "SmartReco follows a layered batch analytics architecture. The data layer reads the Online Retail workbook. The processing layer validates and cleans records using Spark DataFrames. The feature layer aggregates transactions and assigns stable integer IDs. The modelling layer trains implicit ALS and generates recommendations. The association layer finds products that frequently occur together. Finally, the presentation layer reads persisted Parquet and JSON outputs in Streamlit.")
    add_table(doc, [["Layer", "Main component", "Responsibility"], ["Data", "Online Retail.xlsx", "Source invoice and product transaction records"], ["Processing", "Spark DataFrames", "Validation, filtering, typing, and aggregation"], ["Features", "feature_engineering.py", "Interaction strength and stable IDs"], ["Model", "Spark MLlib ALS", "Implicit customer-product recommendation"], ["Analysis", "association_rules.py", "Support, confidence, and lift"], ["Presentation", "app.py / Streamlit", "Charts, tables, and recommendation display"]], [1.2, 2.0, 3.6])
    add_para(doc, "The architecture keeps computation separate from presentation. Once the pipeline has generated Parquet and JSON files, the dashboard reads those outputs and does not retrain the model. This makes the interface quicker to open and ensures that displayed results correspond to a persisted pipeline run.")
    page_break(doc)

    # 9
    page_title(doc, "2. System Architecture")
    add_heading(doc, "2.2 Data Flow", 2)
    add_para(doc, "The pipeline begins by loading the Excel workbook with an explicit schema. The cleaning stage creates canonical lower-case fields, derives transaction amount, identifies cancellation invoices, removes invalid records, and reports quality statistics. The feature stage groups valid purchases by customer and product, calculates total quantity and purchase frequency, records the latest purchase date, and creates a logarithmic interaction strength.")
    add_para(doc, "The resulting interaction table receives stable numeric user and item identifiers. The training data is sent to ALS with implicit preferences enabled. The model generates candidate recommendations, and a left-anti join removes products already purchased by each customer. Recommendations are written with product metadata so that the dashboard can display product codes and descriptions directly.")
    add_table(doc, [["Step", "Input", "Output"], ["1. Load", "Online Retail.xlsx", "Spark DataFrame with source schema"], ["2. Clean", "Raw transaction rows", "Positive, valid purchases"], ["3. Aggregate", "Purchases", "Customer-product interactions"], ["4. Encode", "Customer and product keys", "Stable user and item IDs"], ["5. Train", "Interaction strengths", "ALS model"], ["6. Recommend", "Model and users", "Ranked top-10 products"], ["7. Persist", "DataFrames and metrics", "Parquet and JSON outputs"]], [1.0, 2.5, 3.3])
    add_heading(doc, "2.3 Presentation Layer", 2)
    add_para(doc, "The Streamlit interface contains overview, product analytics, personalised recommendations, and evaluation and association areas. A customer selector maps the original customer ID to the stable internal user ID and displays the generated ranked products. Product analytics are calculated from cleaned purchases, while recommendation and evaluation views use persisted model outputs.")
    page_break(doc)

    # 10
    page_title(doc, "2. System Architecture")
    add_heading(doc, "2.4 Dataset and Input Schema", 2)
    add_table(doc, [["Column", "Meaning", "Role"], ["InvoiceNo", "Invoice or transaction number", "Cancellation detection and basket identity"], ["StockCode", "Product identifier", "Item identity"], ["Description", "Product description", "Dashboard display"], ["Quantity", "Units in invoice line", "Purchase strength"], ["InvoiceDate", "Transaction timestamp", "Temporal analysis"], ["UnitPrice", "Unit price", "Revenue calculation"], ["CustomerID", "Customer identifier", "User identity"], ["Country", "Customer country", "Source context"]], [1.4, 2.8, 2.6])
    add_para(doc, "The inspected workbook contains 541,909 rows and the required fields used by the cleaning module. The output summary reports 18,532 unique transactions, 4,338 customers, 3,665 products, 5,152,002 positive units, and revenue of approximately 8,887,208.89 in the source currency.")
    add_heading(doc, "2.5 Generated Outputs", 2)
    add_table(doc, [["Output", "Purpose"], ["cleaned_purchases", "Validated transaction records"], ["interactions", "Aggregated customer-product strengths and metadata"], ["all_customers", "Ranked recommendations for all users"], ["product_associations", "Frequently co-purchased products"], ["summary.json", "Counts, quantities, and revenue"], ["data_quality.json", "Cleaning and retention statistics"], ["evaluation.json", "Precision, recall, and model details"]], [2.4, 4.4])
    page_break(doc)

    # 11
    page_title(doc, "2. System Architecture")
    add_heading(doc, "2.6 Recommendation Model", 2)
    add_para(doc, "SmartReco uses Spark MLlib Alternating Least Squares with implicitPrefs=True. Unlike an explicit rating model, the system does not require star ratings. Instead, the amount and frequency of positive purchases are transformed into an interaction strength. ALS learns latent representations for customers and products and estimates a compatibility score used to rank candidate products.")
    add_para(doc, "The configured model uses rank 10, eight maximum iterations, regularisation parameter 0.1, alpha 1.0, top_k 10, and seed 42. A popularity fallback is available when the data has too few distinct users or items for ALS training. This makes the pipeline more robust for small or sparse datasets.")
    add_heading(doc, "2.7 Association Analysis", 2)
    add_para(doc, "Association analysis views transactions as baskets. Support measures how often a pair of products appears together in all baskets. Confidence measures how often product B appears when product A appears. Lift compares the observed conditional probability with the probability expected if the products were independent. A lift greater than one indicates a stronger-than-independent relationship and can support cross-selling suggestions.")
    page_break(doc)

    # 12
    page_title(doc, "3. Implementation")
    add_heading(doc, "3.1 Project Structure", 2)
    add_table(doc, [["Module", "Responsibility"], ["main.py", "Starts Spark and runs the pipeline"], ["data_loader.py", "Reads the workbook with an explicit schema"], ["data_cleaning.py", "Validates, types, filters, and reports data quality"], ["feature_engineering.py", "Builds interactions and stable IDs"], ["recommendation_model.py", "ALS training and recommendation generation"], ["association_rules.py", "Product co-purchase metrics"], ["evaluation.py", "Precision and recall calculations"], ["output_writer.py", "Windows-friendly Parquet persistence"], ["app.py", "Streamlit dashboard"]], [2.3, 4.5])
    add_heading(doc, "3.2 Data Cleaning", 2)
    add_para(doc, "The cleaning module first checks that the expected source columns are present. It casts invoice and stock identifiers to strings, quantities and prices to doubles, customer IDs to long integers, and dates to timestamps. It derives amount as quantity multiplied by unit price and marks invoice numbers beginning with C as cancellations. Valid records require identifiers, dates, positive quantity, and positive unit price. Duplicate records are removed after the validation stage.")
    add_para(doc, "The method records input rows, duplicate rows, cancellations or returns, retained positive purchases, and dropped rows. These values are written to data_quality.json and displayed in the dashboard so that a user can understand how much of the source workbook entered model training.")
    page_break(doc)

    # 13
    page_title(doc, "3. Implementation")
    add_heading(doc, "Listing 3.1: Data cleaning and canonical fields", 2)
    add_code(doc, '''typed = (\n    df.withColumn("invoice_no", F.trim(F.col("InvoiceNo").cast("string")))\n      .withColumn("stock_code", F.trim(F.col("StockCode").cast("string")))\n      .withColumn("description", F.trim(F.col("Description").cast("string")))\n      .withColumn("quantity", F.col("Quantity").cast("double"))\n      .withColumn("unit_price", F.col("UnitPrice").cast("double"))\n      .withColumn("customer_id", F.col("CustomerID").cast("long"))\n      .withColumn("invoice_date", F.to_timestamp("InvoiceDate"))\n      .withColumn("amount", F.col("quantity") * F.col("unit_price"))\n)\n\npurchases = valid.filter(\n    (F.col("quantity") > 0) & (F.col("unit_price") > 0)\n).dropDuplicates()''')
    add_para(doc, "This implementation keeps validation close to ingestion and gives all later modules a stable schema. The same canonical names are used by feature engineering, pipeline persistence, and the Streamlit dashboard, reducing the possibility of mismatched column names between stages.")
    add_heading(doc, "3.3 Quality Reporting", 2)
    add_para(doc, "Quality reporting is not treated as an optional log. It is part of the generated project output because a recommendation model is only meaningful when the analyst knows which source rows were retained. In this run, 149,217 rows were dropped from the original workbook after duplicate, cancellation, invalid, and non-positive filters were applied.")
    page_break(doc)

    # 14
    page_title(doc, "3. Implementation")
    add_heading(doc, "Listing 3.2: Interaction feature engineering", 2)
    add_code(doc, '''interactions = (\n    purchases.groupBy("customer_id", "stock_code")\n    .agg(\n        F.sum("quantity").alias("total_quantity"),\n        F.countDistinct("invoice_no").alias("purchase_frequency"),\n        F.max("invoice_date").alias("last_purchase"),\n        F.first("description", ignorenulls=True).alias("description"),\n    )\n    .withColumn("strength", F.log1p("total_quantity"))\n)''')
    add_para(doc, "The interaction table compresses many invoice lines into one customer-product record. Total quantity captures purchase volume, purchase frequency captures repeated invoices, last purchase supports temporal evaluation, and description preserves readable product metadata. The log1p transformation reduces the dominance of very large quantity values while retaining the distinction between low and high engagement.")
    add_heading(doc, "Listing 3.3: Stable ID generation", 2)
    add_code(doc, '''users = interactions.select("customer_id").distinct().withColumn(\n    "user", F.row_number().over(Window.orderBy("customer_id")).cast("int")\n)\nitems = interactions.select("stock_code").distinct().withColumn(\n    "item", F.row_number().over(Window.orderBy("stock_code")).cast("int")\n)''')
    add_para(doc, "Stable integer mappings allow the model to work with compact numeric identifiers while retaining original customer IDs and stock codes for interpretation in the application.")
    page_break(doc)

    # 15
    page_title(doc, "3. Implementation")
    add_heading(doc, "Listing 3.4: ALS configuration", 2)
    add_code(doc, '''ALS(\n    userCol="user", itemCol="item", ratingCol="strength",\n    rank=10, maxIter=8, regParam=0.1, alpha=1.0,\n    implicitPrefs=True, coldStartStrategy="drop", seed=42\n)''')
    add_heading(doc, "3.4 Evaluation and Persistence", 2)
    add_para(doc, "The evaluation split is temporal. The maximum last-purchase timestamp is identified, earlier interactions form the training data, and the latest interaction is used as future evidence. Recommendations are compared with the held-out future products. Precision@K measures relevant observed future products per recommendation slot, while Recall@K measures how much of a customer's observed future activity was recovered.")
    add_para(doc, "The pipeline writes Spark DataFrames as Parquet directories through a PyArrow streaming writer. This design avoids requiring Hadoop's Windows-specific winutils.exe. JSON files store summary statistics, data-quality results, and evaluation metrics. The Streamlit dashboard reads these outputs and does not retrain the model.")
    add_heading(doc, "3.5 Technologies Used", 2)
    add_table(doc, [["Layer", "Technology", "Role"], ["Processing", "Apache Spark", "DataFrame transformations"], ["Machine learning", "Spark MLlib ALS", "Implicit recommendations"], ["Data handling", "pandas, PyArrow, openpyxl", "Inspection and file handling"], ["Presentation", "Streamlit", "Interactive dashboard"], ["Language", "Python 3", "Pipeline and application code"]], [1.5, 2.2, 3.1])
    page_break(doc)

    # 16
    page_title(doc, "4. Results")
    add_heading(doc, "4.1 Data Quality and Portfolio Summary", 2)
    add_para(doc, "The complete Online Retail workbook contained 541,909 source rows. The cleaning stage detected 5,268 duplicate rows and 8,905 cancellation or return rows. After validation, filtering, and deduplication, 392,692 positive purchase records were retained for feature engineering and model training.")
    add_table(doc, [["Indicator", "Value", "Meaning"], ["Input rows", "541,909", "Rows in source workbook"], ["Duplicate rows", "5,268", "Duplicates reported before removal"], ["Cancellations or returns", "8,905", "Excluded from positive training data"], ["Retained purchases", "392,692", "Valid positive purchase rows"], ["Customers", "4,338", "Distinct customer IDs"], ["Products", "3,665", "Distinct stock codes"], ["Unique transactions", "18,532", "Invoice count in retained data"], ["Positive quantity", "5,152,002", "Total retained units"]], [2.1, 1.5, 3.2])
    add_para(doc, "The output summary reports revenue of approximately 8,887,208.89 and an average retained line value of approximately 22.63. These values demonstrate that the pipeline processes a substantial retail history and not merely a small demonstration table.")
    page_break(doc)

    # 17
    page_title(doc, "4. Results")
    add_heading(doc, "4.2 Product Analytics", 2)
    add_para(doc, "The Product analytics view groups cleaned purchases by stock code and description. It ranks products by total quantity sold and separately ranks products by total revenue. A customer purchase-volume chart groups the retained amount by customer ID and highlights customers with the highest historical spend.")
    add_para(doc, "These views provide a business baseline before personalised recommendations are examined. Global popularity helps a retailer understand demand concentration, while the personalised recommendation view tests whether a customer's history can identify products beyond only the globally most popular items.")
    add_heading(doc, "4.3 Personalised Recommendations", 2)
    add_para(doc, "The recommendation view allows the user to select a customer from the interaction table. The selected customer is mapped to the internal ALS user identifier, and the generated rows are sorted by model rank. The display includes rank, stock code, description, and score. Already purchased products are removed by the recommendation pipeline before the data reaches the dashboard.")
    add_para(doc, "Recommendations are read from data/recommendations/all_customers. This persisted contract makes the dashboard independent of Spark execution and allows the user to inspect results even after the modelling process has completed.")
    page_break(doc)

    # 18
    page_title(doc, "4. Results")
    add_heading(doc, "4.4 Model Evaluation", 2)
    add_table(doc, [["Metric", "Value", "Interpretation"], ["Algorithm", "Implicit ALS", "Spark MLlib recommendation model"], ["Precision@10", "0.00002359", "Observed future items per recommendation slot"], ["Recall@10", "0.07142857", "Observed future items recovered"], ["Evaluated users", "4,239", "Users included in temporal evaluation"]], [2.0, 1.6, 3.2])
    add_para(doc, "The Precision@10 result is very small and Recall@10 is approximately 7.14 percent. These results should not be interpreted as a complete judgement of the usefulness of the system. The evaluation counts only observed future purchases as positive evidence. An item that was recommended but not purchased is not necessarily a true negative because the customer may not have seen it, needed it, or had the opportunity to buy it.")
    add_para(doc, "The single temporal split and sparse customer-product matrix also make ranking difficult. The metrics are valuable as a reproducible baseline for future experiments involving model tuning, recency weighting, minimum activity filters, product popularity comparisons, and repeated time-window evaluation.")
    page_break(doc)

    # 19
    page_title(doc, "4. Results")
    add_heading(doc, "4.5 Association Rules", 2)
    add_para(doc, "The association module discovers products that occur together in the same invoice basket. The dashboard lets the user choose a product code and then displays related pairs sorted by lift. This creates a complementary view of retail behaviour: ALS models a customer-product preference across history, while associations describe product combinations within baskets.")
    add_table(doc, [["Measure", "Definition", "Business interpretation"], ["Support", "Baskets containing A and B divided by all baskets", "How common the pair is"], ["Confidence", "Baskets containing A and B divided by baskets containing A", "How often B occurs with A"], ["Lift", "Confidence(A -> B) divided by Support(B)", "Strength above independent occurrence"]], [1.3, 3.7, 2.6])
    add_para(doc, "Association rules can support cross-selling suggestions, bundle design, product placement, and campaign planning. They should be interpreted with product frequency in mind because extremely common products can produce high confidence without necessarily being highly distinctive. Lift helps separate general popularity from a stronger relationship between two products.")
    page_break(doc)

    # 20
    page_title(doc, "4. Results")
    add_heading(doc, "4.6 Dashboard Views", 2)
    add_table(doc, [["View", "Displayed information"], ["Overview", "Transactions, customers, products, revenue, and data quality"], ["Product analytics", "Best-selling products, revenue leaders, and customer volume"], ["Personalised recommendations", "Customer selector and ranked top-10 products"], ["Evaluation and associations", "Ranking metrics and co-purchased products"]], [2.4, 4.4])
    add_para(doc, "The dashboard uses a wide layout so charts and tables remain readable. The overview presents metrics from summary.json and quality information from data_quality.json. The product analytics view uses cleaned purchases. The recommendation view uses the persisted recommendation Parquet output. The evaluation view displays JSON metrics and association tables.")
    add_para(doc, "A fallback mode is available when generated Spark outputs are not present. It reads the workbook directly and shows live transaction analytics while clearly stating that it does not train ALS or claim personalised recommendations. This makes initial setup easier without confusing exploratory charts with model-generated results.")
    page_break(doc)

    # 21
    page_title(doc, "4. Results")
    add_heading(doc, "4.7 Discussion", 2)
    add_para(doc, "The project completes the full BDA workflow from ingestion to presentation. The source workbook is cleaned without changing the original file, aggregated into customer-product features, used to train an implicit recommendation model, evaluated with a temporal split, and persisted for dashboard use. Each stage has a defined output that can be inspected independently.")
    add_para(doc, "The separation between model computation and presentation is an important practical result. A new pipeline run can refresh Parquet and JSON outputs while the Streamlit interface continues to use the same schema. This makes the prototype easier to test, explain, and extend with future algorithms.")
    add_para(doc, "The evaluation result also encourages an honest interpretation. Since unobserved products are unknown rather than confirmed negatives, Precision@10 should not be presented as a conventional classification accuracy. SmartReco is best described as a recommendation-system prototype and Big Data Analytics demonstration with a measured but limited offline baseline.")
    page_break(doc)

    # 22
    page_title(doc, "4. Results")
    add_heading(doc, "4.8 Reliability and Reproducibility", 2)
    add_para(doc, "The ALS configuration uses a fixed random seed of 42. Stable IDs are generated with deterministic ordering over customer and product identifiers. Input and output directories are defined centrally in config.py. Summary, quality, and evaluation JSON files make the pipeline result inspectable without opening the dashboard.")
    add_table(doc, [["Check", "Result"], ["Source workbook schema", "Validated by the data loader"], ["Positive purchase filtering", "392,692 retained rows"], ["Stable customer and product IDs", "Implemented and tested"], ["Parquet outputs", "Written using PyArrow"], ["Recommendation display fields", "rank, stock_code, description, score"], ["Dashboard syntax", "Validated with Python compilation"]], [2.8, 4.0])
    add_para(doc, "The existing test verifies that interaction aggregation combines repeated customer-product purchases, generates stable user identifiers, and produces a positive interaction strength. For deployment, additional integration tests would be useful for the full pipeline, output schemas, dashboard loading, and empty or sparse datasets.")
    page_break(doc)

    # 23
    page_title(doc, "4. Results")
    add_heading(doc, "4.9 Limitations", 2)
    add_para(doc, "The current system uses transaction history but does not include product categories, customer demographics, stock availability, marketing exposure, seasonality, or changing prices. A customer with no history is difficult to recommend for, and a newly introduced product has no interaction evidence. ALS quality also depends on sufficient customer and product activity.")
    add_para(doc, "The evaluation uses one temporal split and only observed future purchases. A stronger study would use multiple temporal windows, minimum activity thresholds, MAP@K, NDCG@K, catalogue coverage, diversity, novelty, and business-level conversion outcomes. The current results are therefore a baseline for experimentation rather than a production quality guarantee.")
    add_para(doc, "The association analysis also needs careful interpretation. A high support value can reflect a globally common product, while a high lift value may occur for a pair with small absolute support. Recommendations should combine statistical measures with business knowledge and, in a deployed system, with inventory and policy constraints.")
    page_break(doc)

    # 24
    page_title(doc, "5. Conclusion")
    add_para(doc, "This mini project presented SmartReco, a local Big Data Analytics application for e-commerce product recommendations. The system reads the UCI Online Retail workbook, validates and cleans transactions, aggregates customer-product interactions, trains an implicit Spark ALS model, evaluates future-item recovery, computes product associations, and presents the results through Streamlit.")
    add_para(doc, "The pipeline processed 541,909 source rows and retained 392,692 positive purchase records from 4,338 customers and 3,665 products. It generated ranked recommendations for customers and recorded Recall@10 of 0.07142857 for 4,239 evaluated users. The project demonstrates how raw retail data can be transformed into a reproducible recommendation workflow with data-quality reporting and an accessible user interface.")
    add_para(doc, "The system should be understood as a prototype baseline. Its strongest contribution is the complete, modular analytics lifecycle: ingestion, cleaning, feature engineering, recommendation modelling, evaluation, association analysis, persistence, and visual presentation. This foundation can support more advanced modelling and deployment in future work.")
    page_break(doc)

    # 25
    page_title(doc, "5. Conclusion")
    add_heading(doc, "Future Scope", 2)
    for item in ["Tune ALS rank, regularisation, alpha, iteration count, and recommendation size.", "Introduce recency and frequency weighting so recent customer activity has stronger influence.", "Compare ALS with item-item collaborative filtering, popularity, and content-based methods.", "Add product categories, country, seasonality, price, and stock information for hybrid recommendations.", "Evaluate with repeated time splits, MAP@K, NDCG@K, coverage, diversity, and novelty.", "Add a database and authenticated API for multi-user deployment.", "Schedule Spark jobs or use structured streaming for continuously arriving retail transactions.", "Add explainable reasons such as frequently bought together or similar customer behaviour."]:
        doc.add_paragraph(item, style="List Bullet")
    add_para(doc, "With these extensions, SmartReco could develop from a local academic prototype into a monitored recommendation service while preserving the current separation between data preparation, model generation, persisted outputs, and presentation.")
    page_break(doc)

    # 26
    page_title(doc, "6. References")
    refs = [
        "[1] UCI Machine Learning Repository, Online Retail Data Set, University of California, Irvine.",
        "[2] X. Meng et al., MLlib: Machine Learning in Apache Spark, Journal of Machine Learning Research, vol. 17, no. 34, 2016.",
        "[3] Y. Koren, R. Bell, and C. Volinsky, Matrix Factorization Techniques for Recommender Systems, IEEE Computer, vol. 42, no. 8, pp. 30-37, 2009.",
        "[4] R. M. Bell and Y. Koren, Lessons from the Netflix Prize Challenge, SIGKDD Explorations, vol. 9, no. 2, 2007.",
        "[5] Apache Spark Documentation, Spark MLlib Collaborative Filtering.",
        "[6] pandas Documentation, DataFrame and Parquet interfaces.",
        "[7] Streamlit Documentation, Data Apps in Python.",
        "[8] PyArrow Documentation, Parquet file format and Python API.",
        "[9] W. McKinney, Python for Data Analysis, O'Reilly Media.",
        "[10] SmartReco project source code and generated outputs, BDA Mini Project repository, accessed October 2026.",
    ]
    for ref in refs:
        add_para(doc, ref)
    doc.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build()
