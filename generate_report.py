from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Preformatted, KeepTogether, Flowable
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "SmartReco_BDA_Project_Report.pdf"

PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#1F3A5F")
BLUE = colors.HexColor("#DCE8F5")
GOLD = colors.HexColor("#E8C46A")
GREEN = colors.HexColor("#DFF1E4")
PALE = colors.HexColor("#F7F9FC")
GRAY = colors.HexColor("#666666")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=30, alignment=TA_CENTER, textColor=colors.black, spaceAfter=18))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="Helvetica", fontSize=13, leading=21, alignment=TA_CENTER, spaceAfter=8))
styles.add(ParagraphStyle(name="Chapter", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=19, leading=24, alignment=TA_CENTER, textColor=colors.black, spaceAfter=20))
styles.add(ParagraphStyle(name="Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=17, spaceBefore=8, spaceAfter=8))
styles.add(ParagraphStyle(name="BodyJ", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.4, leading=16, alignment=TA_JUSTIFY, spaceAfter=8))
styles.add(ParagraphStyle(name="Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.4, leading=16, spaceAfter=8))
styles.add(ParagraphStyle(name="Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.5, leading=12, spaceAfter=5))
styles.add(ParagraphStyle(name="Caption", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=9.5, leading=12, alignment=TA_CENTER, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name="CodeBlock", parent=styles["Code"], fontName="Courier", fontSize=7.6, leading=10, leftIndent=8, rightIndent=8, borderColor=colors.lightgrey, borderWidth=0.5, borderPadding=8, backColor=colors.HexColor("#F4F4F4")))
styles.add(ParagraphStyle(name="TOC", parent=styles["BodyText"], fontName="Helvetica", fontSize=11, leading=23, leftIndent=20))


def P(text, style="BodyJ"):
    return Paragraph(text, styles[style])


def table(data, widths=None, header=True, font=8.5):
    converted = []
    for row in data:
        converted.append([cell if isinstance(cell, Flowable) else Paragraph(str(cell), styles["Small"]) for cell in row])
    t = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="CENTER")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#777777")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), BLUE), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
    t.setStyle(TableStyle(commands))
    return t


class FlowDiagram(Flowable):
    def __init__(self, labels, colors_list=None, width=16.5 * cm, height=4.2 * cm):
        super().__init__()
        self.width = width
        self.height = height
        self.labels = labels
        self.colors_list = colors_list or [BLUE] * len(labels)

    def draw(self):
        c = self.canv
        gap = 0.22 * cm
        box_w = (self.width - gap * (len(self.labels) - 1)) / len(self.labels)
        y = self.height * 0.35
        for i, label in enumerate(self.labels):
            x = i * (box_w + gap)
            c.setFillColor(self.colors_list[i])
            c.setStrokeColor(NAVY)
            c.roundRect(x, y, box_w, self.height * 0.38, 6, fill=1, stroke=1)
            c.setFillColor(colors.black)
            lines = label.split("\n")
            for j, line in enumerate(lines):
                c.setFont("Helvetica-Bold" if j == 0 else "Helvetica", 8.5 if j == 0 else 7.3)
                c.drawCentredString(x + box_w / 2, y + self.height * 0.25 - j * 11, line)
            if i < len(self.labels) - 1:
                c.setStrokeColor(NAVY)
                c.setFillColor(NAVY)
                x1 = x + box_w + 2
                x2 = x + box_w + gap - 3
                yy = y + self.height * 0.19
                c.line(x1, yy, x2, yy)
                c.line(x2 - 5, yy + 3, x2, yy)
                c.line(x2 - 5, yy - 3, x2, yy)


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.draw_page_number(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, total):
        if self._pageNumber > 1:
            self.setStrokeColor(colors.HexColor("#BBBBBB"))
            self.line(2 * cm, 1.55 * cm, PAGE_W - 2 * cm, 1.55 * cm)
            self.setFont("Helvetica", 8)
            self.setFillColor(GRAY)
            self.drawCentredString(PAGE_W / 2, 1.05 * cm, str(self._pageNumber - 1))


def build():
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, rightMargin=2 * cm, leftMargin=2 * cm, topMargin=1.65 * cm, bottomMargin=1.9 * cm, title="SmartReco - BDA Mini Project Report", author="Vinit Vishwakarma, Utkarsh Yadav, Amit Yadav")
    story = []

    # Page 1: cover
    story += [Spacer(1, 0.35 * inch), P("BDA Mini Project Report", "CoverTitle"), Spacer(1, 0.25 * inch), P("SmartReco - E-Commerce Product Recommendation System", "CoverTitle"), Spacer(1, 0.25 * inch), P("Submitted in fulfilment of the requirements of the<br/>BDA Mini Project Semester VII in degree of<br/>Bachelor of Computer Engineering", "CoverSub"), Spacer(1, 0.35 * inch), P("BY", "CoverSub"), Spacer(1, 0.12 * inch), P("Vinit Vishwakarma (Roll no. 48)<br/>Utkarsh Yadav (Roll no. 68)<br/>Amit Yadav (Roll no. 54)", "CoverSub"), Spacer(1, 0.35 * inch), P("Guide", "CoverSub"), Spacer(1, 0.12 * inch), P("Ms. Praniti Patil", "CoverSub"), Spacer(1, 0.7 * inch), P("Department Of Computer Engineering<br/>Shree L. R. Tiwari College Of Engineering<br/>Kanakia Park, Mira Road (E), Thane - 401 107, Maharashtra.<br/><br/><b>2025-26</b>", "CoverSub"), PageBreak()]

    # Page 2: approval
    story += [P("BDA Mini Project Report Approval", "Chapter"), Spacer(1, 0.3 * inch), P("This project report entitled <b>\"SmartReco - E-Commerce Product Recommendation System\"</b> by Vinit Vishwakarma (Roll No. 48), Utkarsh Yadav (Roll No. 68), and Amit Yadav (Roll No. 54) is approved for the Mini Project Semester VII project work of B.E CMPN at Shree L. R. Tiwari College of Engineering, in the academic year 2025-2026.", "BodyJ"), Spacer(1, 2.3 * inch), P("Internal Examiner", "Body"), PageBreak()]

    # Page 3: declaration
    story += [P("Declaration", "Chapter"), P("We declare that this written submission represents our ideas in our own words and where others' ideas or words have been included, we have adequately cited and referenced the original sources. We also declare that we have adhered to all principles of academic honesty and integrity and have not misrepresented, fabricated, or falsified any idea, data, fact, or source in this submission. We understand that any violation of these principles may result in disciplinary action by the Institute.", "BodyJ"), Spacer(1, 1.3 * inch), P("--------------------------------------<br/>Signature<br/><br/>Vinit Vishwakarma (Roll No. 48)<br/><br/><br/>--------------------------------------<br/>Signature<br/><br/>Utkarsh Yadav (Roll No. 68)<br/><br/><br/>--------------------------------------<br/>Signature<br/><br/>Amit Yadav (Roll No. 54)<br/><br/><br/>Date:<br/><br/>Place:", "Body"), PageBreak()]

    # Page 4: TOC
    story += [P("Table of Contents", "Chapter"), P("1. Introduction", "TOC"), P("2. System Architecture", "TOC"), P("3. Implementation", "TOC"), P("4. Results", "TOC"), P("5. Conclusion", "TOC"), P("6. References", "TOC"), PageBreak()]

    # Page 5
    story += [P("1. Introduction", "Chapter"), P("1.1 Background", "Section"), P("E-commerce platforms contain large volumes of customer purchase transactions. A customer may buy thousands of different products over time, making it difficult to manually identify which products should be shown next. Product recommendation systems solve this problem by learning patterns from historical interactions and presenting relevant products to each customer.", "BodyJ"), P("Big Data Analytics provides a systematic way to ingest, clean, aggregate, model, and visualise these transactions. SmartReco applies this lifecycle to the UCI Online Retail dataset. It converts raw invoices into customer-product interactions, learns implicit preferences using Apache Spark MLlib ALS, generates top-10 recommendations, evaluates them against future purchases, and displays the results in a Streamlit dashboard.", "BodyJ"), P("1.2 Problem Statement", "Section"), P("Retail transaction data usually arrives as a large workbook containing invoices, product codes, descriptions, quantities, prices, dates, and customer identifiers. A data analyst needs to remove invalid transactions, handle cancellations and duplicates, find useful customer-product relationships, and produce recommendations that business users can inspect. Spreadsheet-based analysis does not scale well and cannot naturally provide personalised ranked recommendations for thousands of customers.", "BodyJ"), P("SmartReco addresses this problem through a local Spark pipeline and dashboard that transform raw retail data into actionable product recommendations and co-purchase insights.", "BodyJ"), PageBreak()]

    # Page 6
    story += [P("1. Introduction", "Chapter"), P("1.3 Objectives", "Section"), P("1. To clean and validate the Online Retail transaction workbook using a repeatable data pipeline.<br/>2. To aggregate purchase history into customer-product implicit feedback strengths.<br/>3. To train an implicit-feedback ALS recommendation model using Spark MLlib.<br/>4. To produce ranked top-10 recommendations for all available customers.<br/>5. To evaluate recommendations with Precision@K and Recall@K using a temporal holdout.<br/>6. To identify frequently co-purchased products using support, confidence, and lift.<br/>7. To present portfolio summaries, product analytics, and recommendations through Streamlit.", "BodyJ"), P("1.4 Scope and Limitations", "Section"), P("The system works on structured retail transaction data with invoice number, stock code, product description, quantity, invoice date, unit price, customer ID, and country fields. Positive, non-cancelled transactions with valid identifiers and prices are retained. The model uses implicit feedback, so a recorded purchase is treated as positive evidence while an unobserved product is not treated as a confirmed negative. The project is a local prototype; recommendations are not connected to a live commerce checkout or user account system.", "BodyJ"), PageBreak()]

    # Page 7
    story += [P("1. Introduction", "Chapter"), P("1.5 Relevance to Big Data Analytics", "Section"), P("The project reflects the 3 Vs of Big Data at prototype scale. Volume is represented by 541,909 source transaction rows. Variety comes from identifiers, text descriptions, dates, quantities, prices, and customer fields. Velocity is represented by a repeatable batch pipeline that cleans, aggregates, models, and writes outputs for dashboard consumption. The value comes from converting raw purchase history into ranked recommendations and interpretable association rules.", "BodyJ"), P("The analytics lifecycle followed is ingestion, validation, cleaning, feature engineering, model training, evaluation, association analysis, output persistence, and visual presentation. Spark is used for distributed-style transformations and MLlib modelling, while PyArrow Parquet writing supports reliable output generation on Windows.", "BodyJ"), P("1.6 Organisation of the Report", "Section"), P("Section 2 describes the architecture, data flow, schema, and model. Section 3 explains implementation details and technologies. Section 4 presents generated results and dashboard outputs. Section 5 concludes the work and lists future scope. Section 6 provides references.", "BodyJ"), PageBreak()]

    # Page 8
    story += [P("2. System Architecture", "Chapter"), P("2.1 Architectural Overview", "Section"), P("SmartReco follows a layered batch analytics architecture. The data layer reads the Online Retail workbook. The processing layer validates and cleans records with Spark DataFrames. The feature layer aggregates transactions and assigns stable integer IDs. The modelling layer trains implicit ALS and generates recommendations. The presentation layer reads persisted Parquet and JSON outputs in Streamlit.", "BodyJ"), FlowDiagram(["Online Retail\nworkbook", "Clean and\nvalidate", "Interactions\nand IDs", "ALS and\nassociations", "Parquet +\nStreamlit"], [BLUE, GREEN, GOLD, colors.HexColor("#F7E5C5"), colors.HexColor("#E6DDF4")]), P("Figure 2.1: Layered system architecture of SmartReco.", "Caption"), P("The separation between processing and presentation means that the dashboard never retrains the model. It reads stable generated outputs, which makes the user interface responsive and keeps model execution reproducible.", "BodyJ"), P("2.2 Data Layer", "Section"), P("The loader uses an explicit schema and openpyxl to read the Excel workbook without requiring a Spark Excel connector. The original workbook is never overwritten. Data cleaning creates canonical lower-case columns such as invoice_no, stock_code, description, quantity, unit_price, customer_id, invoice_date, and amount.", "BodyJ"), PageBreak()]

    # Page 9
    story += [P("2. System Architecture", "Chapter"), P("2.3 Processing and Modelling Layers", "Section"), P("The cleaning stage removes rows with missing identifiers, invalid dates, non-positive quantities or prices, cancellation invoices, returns, and duplicate records. The feature stage groups valid purchases by customer and stock code. It calculates total quantity, purchase frequency, last purchase timestamp, and a representative product description. The interaction strength is defined as log1p(total positive quantity), which reduces the effect of unusually large purchases.", "BodyJ"), P("Stable integer IDs are assigned to customers and products because Spark ALS expects numeric user and item columns. The temporal evaluation split holds out the final interaction time while training on earlier activity. Recommendations that the customer already purchased are removed through a left-anti join.", "BodyJ"), FlowDiagram(["Raw rows", "Valid positive\npurchases", "Grouped\ninteractions", "Stable user/item\nIDs", "Ranked recs"], [BLUE, GREEN, GREEN, GOLD, colors.HexColor("#E6DDF4")]), P("Figure 2.2: Transaction-to-recommendation data flow.", "Caption"), P("2.4 Presentation Layer", "Section"), P("The Streamlit application provides an overview, product analytics, personalised recommendations, and evaluation and association views. It loads summary.json and data_quality.json for metrics, reads Parquet datasets for detailed views, and allows a customer to be selected before displaying the top-10 ranked products.", "BodyJ"), PageBreak()]

    # Page 10
    story += [P("2. System Architecture", "Chapter"), P("2.5 Dataset and Input Schema", "Section"), table([["Column", "Meaning", "Use"], ["InvoiceNo", "Invoice or transaction number", "Cancellation detection and basket identity"], ["StockCode", "Product identifier", "Item identity"], ["Description", "Product text description", "Dashboard display"], ["Quantity", "Units in transaction line", "Purchase strength and revenue"], ["InvoiceDate", "Transaction timestamp", "Temporal split and analysis"], ["UnitPrice", "Unit price", "Revenue calculation"], ["CustomerID", "Customer identifier", "User identity"], ["Country", "Customer country", "Source field retained for context"]], [3.0*cm, 5.2*cm, 7.1*cm]), Spacer(1, 0.15*inch), P("The inspected workbook contains 541,909 input rows. After validation and filtering, 392,692 positive purchases are retained. The generated interaction table contains 4,338 customers and 3,665 products.", "BodyJ"), P("2.6 Generated Outputs", "Section"), table([["Output", "Purpose"], ["cleaned_purchases", "Validated transaction records"], ["interactions", "Aggregated customer-product strengths and metadata"], ["all_customers", "Top-ranked recommendations for customers"], ["product_associations", "Frequently co-purchased product pairs"], ["summary.json", "Portfolio counts, quantity, and revenue"], ["evaluation.json", "Precision, recall, and model information"]], [5.0*cm, 10.3*cm]), PageBreak()]

    # Page 11
    story += [P("2. System Architecture", "Chapter"), P("2.7 Recommendation Model", "Section"), P("SmartReco uses Spark MLlib ALS with implicitPrefs=True. The model learns latent customer and product representations from the interaction strength rather than from explicit star ratings. The configuration uses rank 10, eight iterations, regularisation parameter 0.1, alpha 1.0, top_k 10, and seed 42. A popularity fallback is available when the data is too sparse to train ALS.", "BodyJ"), P("For a user u and item i, ALS estimates a compatibility score from latent factors. The exact internal optimisation is handled by Spark MLlib. The application uses the resulting scores only for ranking, then removes products already purchased by the customer.", "BodyJ"), P("2.8 Association Analysis", "Section"), P("Product associations are computed from basket-level co-occurrence. Support measures the fraction of baskets containing both products. Confidence measures the conditional probability of product B appearing when product A appears. Lift compares the observed co-occurrence with the probability expected under independence; a lift above 1 indicates a stronger-than-independent association.", "BodyJ"), PageBreak()]

    # Page 12
    story += [P("3. Implementation", "Chapter"), P("3.1 Project Structure", "Section"), table([["Module", "Responsibility"], ["main.py", "Starts Spark and runs the pipeline"], ["src/data_loader.py", "Reads the workbook with an explicit schema"], ["src/data_cleaning.py", "Validates, types, filters, and reports quality"], ["src/feature_engineering.py", "Builds interactions and stable IDs"], ["src/recommendation_model.py", "ALS training and recommendation generation"], ["src/association_rules.py", "Product co-purchase metrics"], ["src/evaluation.py", "Ranking metrics"], ["src/output_writer.py", "Windows-friendly Parquet persistence"], ["app.py", "Streamlit dashboard"]], [5.0*cm, 10.3*cm]), P("3.2 Data Cleaning", "Section"), P("The cleaning module validates required source columns, casts fields to stable types, derives amount as quantity multiplied by unit price, marks cancellation invoices, filters invalid rows, removes duplicate records, and selects the canonical output schema. A data-quality report records input rows, duplicate rows, cancellations or returns, retained positive purchases, and dropped rows.", "BodyJ"), PageBreak()]

    # Page 13
    story += [P("3. Implementation", "Chapter"), P("Listing 3.1: Data cleaning and canonical fields", "Caption"), Preformatted('''typed = (\n    df.withColumn("invoice_no", F.trim(F.col("InvoiceNo").cast("string")))\n      .withColumn("stock_code", F.trim(F.col("StockCode").cast("string")))\n      .withColumn("description", F.trim(F.col("Description").cast("string")))\n      .withColumn("quantity", F.col("Quantity").cast("double"))\n      .withColumn("unit_price", F.col("UnitPrice").cast("double"))\n      .withColumn("customer_id", F.col("CustomerID").cast("long"))\n      .withColumn("invoice_date", F.to_timestamp("InvoiceDate"))\n      .withColumn("amount", F.col("quantity") * F.col("unit_price"))\n)\npurchases = valid.filter(\n    (F.col("quantity") > 0) & (F.col("unit_price") > 0)\n).dropDuplicates()''', styles["CodeBlock"]), Spacer(1, 0.2*inch), P("The implementation keeps source validation close to ingestion so that downstream modelling receives a well-defined schema. This also makes data-quality counts reproducible across runs.", "BodyJ"), PageBreak()]

    # Page 14
    story += [P("3. Implementation", "Chapter"), P("Listing 3.2: Interaction feature engineering", "Caption"), Preformatted('''interactions = (\n    purchases.groupBy("customer_id", "stock_code")\n    .agg(\n        F.sum("quantity").alias("total_quantity"),\n        F.countDistinct("invoice_no").alias("purchase_frequency"),\n        F.max("invoice_date").alias("last_purchase"),\n        F.first("description", ignorenulls=True).alias("description"),\n    )\n    .withColumn("strength", F.log1p("total_quantity"))\n)''', styles["CodeBlock"]), Spacer(1, 0.2*inch), P("Stable IDs are then created with ordered row numbers over distinct customers and products. Keeping the original customer_id and stock_code alongside user and item makes the Parquet outputs useful for both modelling and dashboard display.", "BodyJ"), P("Listing 3.3: ALS recommendation configuration", "Caption"), Preformatted('''ALS(\n    userCol="user", itemCol="item", ratingCol="strength",\n    rank=10, maxIter=8, regParam=0.1, alpha=1.0,\n    implicitPrefs=True, coldStartStrategy="drop", seed=42\n)''', styles["CodeBlock"]), PageBreak()]

    # Page 15
    story += [P("3. Implementation", "Chapter"), P("3.3 Evaluation and Persistence", "Section"), P("The pipeline uses a temporal holdout based on the maximum last-purchase timestamp. Earlier interactions form the training data, while the held-out future interaction is used to measure ranking performance. Precision@K counts recommended items that appear in observed future purchases divided by K. Recall@K counts observed future purchases recovered by the recommendations divided by the future items for that user.", "BodyJ"), P("Outputs are written as Parquet directories using PyArrow rather than requiring Hadoop's Windows-specific winutils.exe. JSON files store summary statistics, quality counts, and evaluation metrics. The Streamlit dashboard reads these persisted results and does not retrain the model.", "BodyJ"), P("3.4 Technologies Used", "Section"), table([["Layer", "Technology", "Role"], ["Processing", "Apache Spark", "Distributed DataFrame transformations"], ["Machine learning", "Spark MLlib ALS", "Implicit product recommendation"], ["Data handling", "pandas, PyArrow, openpyxl", "Inspection, Parquet writing, workbook input"], ["Presentation", "Streamlit", "Interactive dashboard"], ["Language", "Python 3", "Pipeline and application implementation"]], [3.2*cm, 4.5*cm, 7.6*cm]), PageBreak()]

    # Page 16
    story += [P("4. Results", "Chapter"), P("4.1 Data Quality and Portfolio Summary", "Section"), P("The complete workbook contained 541,909 source rows. The cleaning pipeline detected 5,268 duplicate rows and 8,905 cancellation or return rows. It retained 392,692 positive purchase records for modelling and analysis.", "BodyJ"), table([["Indicator", "Value", "Interpretation"], ["Input rows", "541,909", "Rows in Online Retail workbook"], ["Duplicate rows", "5,268", "Reported before deduplication"], ["Cancellations or returns", "8,905", "Excluded from positive training data"], ["Retained purchases", "392,692", "Valid positive purchase rows"], ["Customers", "4,338", "Distinct customer IDs"], ["Products", "3,665", "Distinct stock codes"]], [4.6*cm, 3.0*cm, 7.7*cm]), P("Figure 4.1: Data-quality and scale summary generated by the pipeline.", "Caption"), P("The retained data represents 18,532 unique invoices, 5,152,002 positive units, and revenue of approximately 8,887,208.89 in the source currency. These values demonstrate that the application processes a substantial retail history rather than a toy single-customer example.", "BodyJ"), PageBreak()]

    # Page 17
    story += [P("4. Results", "Chapter"), P("4.2 Product Analytics", "Section"), P("The dashboard presents best-selling products by total quantity and top products by revenue. These views are calculated from cleaned purchases grouped by stock code and description. A customer purchase-volume chart highlights customers with the highest aggregate spend.", "BodyJ"), FlowDiagram(["Cleaned\npurchases", "Group by\nproduct", "Rank quantity\nand revenue", "Dashboard\ncharts"], [GREEN, BLUE, GOLD, colors.HexColor("#E6DDF4")]), P("Figure 4.2: Product analytics flow.", "Caption"), P("The product views serve two purposes. First, they provide a business-level understanding of demand concentration. Second, they provide a baseline for judging personalised recommendations: a personalised model should identify relevant products without simply returning only the globally most popular items.", "BodyJ"), P("4.3 Personalised Recommendations", "Section"), P("For each selected customer, the dashboard displays up to ten ranked products with rank, product code, description, and model score. Products already purchased by the customer are removed before display. The recommendations are read from data/recommendations/all_customers, so the dashboard remains a presentation layer over the generated model outputs.", "BodyJ"), PageBreak()]

    # Page 18
    story += [P("4. Results", "Chapter"), P("4.4 Model Evaluation", "Section"), table([["Metric", "Value", "Meaning"], ["Algorithm", "Implicit ALS", "Spark MLlib recommendation model"], ["Precision@10", "0.00002359", "Relevant observed future items per recommendation slot"], ["Recall@10", "0.07142857", "Share of observed future items recovered"], ["Evaluated users", "4,239", "Users included in temporal evaluation"]], [4.2*cm, 3.0*cm, 8.1*cm]), P("The low Precision@10 and modest Recall@10 should be interpreted carefully. The evaluation counts only observed future purchases as positive evidence. An item that was recommended but not purchased is not necessarily a true negative because the customer may not have needed, seen, or had the opportunity to buy it. Sparse interactions and a strict temporal split also make the task difficult.", "BodyJ"), P("The metrics nevertheless provide a reproducible baseline for future model improvements, such as tuning rank and regularisation, adding recency weighting, filtering very rare products, or comparing ALS with popularity and item-item collaborative filtering.", "BodyJ"), PageBreak()]

    # Page 19
    story += [P("4. Results", "Chapter"), P("4.5 Association Rules", "Section"), P("The association module identifies product pairs that occur in the same customer basket. The dashboard allows a product code to be selected and displays related pairs sorted by lift. Support, confidence, and lift together distinguish frequent products from genuinely informative co-purchase relationships.", "BodyJ"), table([["Measure", "Definition", "Interpretation"], ["Support", "baskets containing A and B / all baskets", "How common the pair is"], ["Confidence", "baskets containing A and B / baskets containing A", "How often B follows A in a basket"], ["Lift", "confidence(A -> B) / support(B)", "Strength above independent occurrence"]], [3.2*cm, 7.0*cm, 5.1*cm]), P("Association results complement ALS recommendations. ALS models a customer-product preference across history, while associations describe products that appear together in baskets. A retail system can use both signals for personalised recommendations, cross-selling, and merchandising decisions.", "BodyJ"), PageBreak()]

    # Page 20
    story += [P("4. Results", "Chapter"), P("4.6 Dashboard Views", "Section"), P("The SmartReco dashboard is organised into four working areas:", "BodyJ"), table([["View", "Displayed information"], ["Overview", "Transactions, customers, products, revenue, and data quality"], ["Product analytics", "Best-selling products, revenue leaders, and customer purchase volume"], ["Personalised recommendations", "Customer selector and ranked top-10 product recommendations"], ["Evaluation and associations", "Model metrics and frequently co-purchased products"]], [5.0*cm, 10.3*cm]), P("The interface uses a wide layout so tables and charts remain readable. It also includes a fallback mode that shows live analytics from the workbook when generated Spark outputs are not yet available. This makes the application useful during initial setup while clearly indicating that the fallback does not train ALS or claim personalised recommendations.", "BodyJ"), P("Figure 4.3: Streamlit dashboard modules and their generated data sources.", "Caption"), PageBreak()]

    # Page 21
    story += [P("4. Results", "Chapter"), P("4.7 Discussion", "Section"), P("The project completes the full BDA workflow from ingestion to presentation. The source workbook is cleaned without modifying the original file, aggregated into meaningful customer-product features, used to train an implicit recommendation model, evaluated with a temporal split, and persisted for dashboard use.", "BodyJ"), P("The most important practical result is the separation of model computation from user presentation. A new pipeline run can refresh Parquet and JSON outputs, while the Streamlit interface continues to use the same schema. This makes the prototype easier to test and extend.", "BodyJ"), P("The evaluation result also provides an honest baseline rather than an inflated claim. Since unobserved products are unknown rather than confirmed negatives, Precision@10 is very small and Recall@10 is 0.0714. The project should therefore be presented as a recommendation-system prototype and analytics demonstration, not as a production-grade commercial recommender.", "BodyJ"), PageBreak()]

    # Page 22
    story += [P("4. Results", "Chapter"), P("4.8 Reliability and Reproducibility", "Section"), P("The pipeline is configured with a fixed random seed of 42 for ALS, explicit source and output paths, deterministic stable-ID ordering, and JSON summaries that can be inspected independently of the dashboard. The test suite verifies that interaction aggregation and stable IDs preserve distinct customers and products and calculate positive strengths.", "BodyJ"), table([["Check", "Result"], ["Source workbook schema", "Validated by the loader"], ["Positive purchase filtering", "392,692 retained rows"], ["Stable customer and product IDs", "Implemented and tested"], ["Parquet outputs", "Written through PyArrow"], ["Recommendation display schema", "rank, stock_code, description, score"], ["Dashboard syntax", "Validated with py_compile"]], [6.2*cm, 9.1*cm]), P("These checks support repeatable execution on the current environment. For deployment, the project would additionally need automated integration tests, monitoring, dependency pinning, and a persistent serving layer.", "BodyJ"), PageBreak()]

    # Page 23
    story += [P("4. Results", "Chapter"), P("4.9 Limitations", "Section"), P("The current system has several limitations. It uses only transaction history and does not include product categories, customer demographics, stock availability, seasonality, or item price changes. ALS quality depends on sufficient interaction history, and cold-start customers or products are difficult to recommend. The popularity fallback is useful for sparse cases but is not personalised.", "BodyJ"), P("The current evaluation is based on a single temporal split and observed future purchases. More robust evaluation would use multiple time windows, per-user minimum activity thresholds, ranking metrics such as MAP@K and NDCG@K, and business measures such as coverage and diversity. These limitations are appropriate for a semester prototype and define clear future work.", "BodyJ"), PageBreak()]

    # Page 24
    story += [P("5. Conclusion", "Chapter"), P("This mini project presented SmartReco, a local Big Data Analytics application for e-commerce product recommendations. The system reads the UCI Online Retail workbook, validates and cleans transactions, aggregates customer-product interactions, trains an implicit Spark ALS model, evaluates future-item recovery, computes product associations, and presents the outputs through Streamlit.", "BodyJ"), P("The pipeline processed 541,909 source rows and retained 392,692 positive purchase records from 4,338 customers and 3,665 products. It generated ranked recommendations and recorded a Recall@10 of 0.0714 for 4,239 evaluated users. The project therefore demonstrates how raw retail data can be transformed into an end-to-end recommendation workflow with reproducible outputs and an accessible dashboard.", "BodyJ"), P("The results should be understood as a prototype baseline. The application shows the complete analytics lifecycle and provides a foundation for more advanced recommendation experiments and eventual production deployment.", "BodyJ"), PageBreak()]

    # Page 25
    story += [P("5. Conclusion", "Chapter"), P("Future Scope", "Section"), P("1. Improve model tuning by comparing ALS ranks, regularisation values, alpha, and top-k settings.<br/>2. Add recency and frequency weighting so recent purchases influence recommendations more strongly.<br/>3. Compare ALS with item-item collaborative filtering and popularity-based ranking.<br/>4. Add product categories, country, seasonality, and price features for hybrid recommendations.<br/>5. Evaluate with repeated temporal splits, MAP@K, NDCG@K, coverage, diversity, and novelty.<br/>6. Add a database and authenticated API for multi-user deployment.<br/>7. Scale the pipeline to larger retail streams using scheduled Spark jobs or structured streaming.<br/>8. Add explainable recommendation reasons such as frequently bought together or similar customer behaviour.", "BodyJ"), P("SmartReco can consequently grow from a local academic prototype into a monitored recommendation service while preserving the current separation between data preparation, modelling, persisted outputs, and presentation.", "BodyJ"), PageBreak()]

    # Page 26
    story += [P("6. References", "Chapter"), P("[1] UCI Machine Learning Repository, Online Retail Data Set, University of California, Irvine.<br/><br/>[2] X. Meng et al., \"MLlib: Machine Learning in Apache Spark,\" Journal of Machine Learning Research, vol. 17, no. 34, 2016.<br/><br/>[3] Y. Koren, R. Bell, and C. Volinsky, \"Matrix Factorization Techniques for Recommender Systems,\" IEEE Computer, vol. 42, no. 8, pp. 30-37, 2009.<br/><br/>[4] R. M. Bell and Y. Koren, \"Lessons from the Netflix Prize Challenge,\" SIGKDD Explorations, vol. 9, no. 2, 2007.<br/><br/>[5] Apache Spark Documentation, Spark MLlib Collaborative Filtering.<br/><br/>[6] pandas Documentation, DataFrame and Parquet interfaces.<br/><br/>[7] Streamlit Documentation, Data Apps in Python.<br/><br/>[8] PyArrow Documentation, Parquet file format and Python API.<br/><br/>[9] W. McKinney, <i>Python for Data Analysis</i>, O'Reilly Media.<br/><br/>[10] SmartReco project source code and generated outputs, BDA Mini Project repository, accessed October 2026.", "BodyJ")]

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    build()
