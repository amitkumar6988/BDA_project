from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "SmartReco_System_Architecture.png"
WIDTH, HEIGHT = 1800, 1200

BG = "#F6F8FC"
NAVY = "#173A63"
TEXT = "#142235"
MUTED = "#526579"
BLUE = "#DCEBFA"
GREEN = "#DFF2E4"
GOLD = "#F9E9B8"
PURPLE = "#E9DDF7"
ORANGE = "#F8E1C5"
WHITE = "#FFFFFF"

font_dir = Path("C:/Windows/Fonts")
regular_path = font_dir / "arial.ttf"
bold_path = font_dir / "arialbd.ttf"
regular = str(regular_path) if regular_path.exists() else None
bold = str(bold_path) if bold_path.exists() else regular


def font(size, is_bold=False):
    return ImageFont.truetype(bold if is_bold else regular, size) if regular else ImageFont.load_default()


def centered(draw, box, lines, size=25, color=TEXT, bold_text=False, gap=5):
    x1, y1, x2, y2 = box
    line_font = font(size, bold_text)
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=line_font)
        heights.append(bbox[3] - bbox[1])
    total = sum(heights) + gap * (len(lines) - 1)
    y = (y1 + y2 - total) / 2
    for line, h in zip(lines, heights):
        bbox = draw.textbbox((0, 0), line, font=line_font)
        x = (x1 + x2 - (bbox[2] - bbox[0])) / 2
        draw.text((x, y), line, font=line_font, fill=color)
        y += h + gap


def box(draw, xy, fill, title, body, title_size=25):
    draw.rounded_rectangle(xy, radius=18, fill=fill, outline=NAVY, width=4)
    x1, y1, x2, y2 = xy
    centered(draw, (x1 + 18, y1 + 15, x2 - 18, y1 + 62), [title], title_size, NAVY, True)
    centered(draw, (x1 + 18, y1 + 70, x2 - 18, y2 - 15), body, 20, TEXT, False, 8)


def arrow(draw, start, end, color=NAVY, width=6):
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        if x2 >= x1:
            points = [(x2, y2), (x2 - 18, y2 - 11), (x2 - 18, y2 + 11)]
        else:
            points = [(x2, y2), (x2 + 18, y2 - 11), (x2 + 18, y2 + 11)]
    else:
        if y2 >= y1:
            points = [(x2, y2), (x2 - 11, y2 - 18), (x2 + 11, y2 - 18)]
        else:
            points = [(x2, y2), (x2 - 11, y2 + 18), (x2 + 11, y2 + 18)]
    draw.polygon(points, fill=color)


image = Image.new("RGB", (WIDTH, HEIGHT), BG)
draw = ImageDraw.Draw(image)

# Header
draw.rectangle((0, 0, WIDTH, 120), fill=NAVY)
draw.text((70, 28), "SmartReco", font=font(42, True), fill=WHITE)
draw.text((70, 78), "E-Commerce Product Recommendation System", font=font(22), fill="#DCEBFA")
draw.text((WIDTH - 530, 45), "SYSTEM ARCHITECTURE", font=font(25, True), fill=WHITE)

# Main pipeline boxes
box(draw, (70, 230, 355, 485), BLUE, "Data Source", ["Online Retail.xlsx", "541,909 source rows", "Invoice, product, customer", "quantity, date, price"], 26)
box(draw, (470, 230, 755, 485), GREEN, "Data Cleaning", ["src/data_cleaning.py", "Validate schema", "Remove returns, cancellations", "duplicates and invalid rows"], 26)
box(draw, (870, 230, 1155, 485), GOLD, "Feature Engineering", ["src/feature_engineering.py", "Customer-product groups", "log1p purchase strength", "Stable user/item IDs"], 26)
box(draw, (1270, 180, 1710, 390), ORANGE, "Recommendation Model", ["Spark MLlib implicit ALS", "rank=10, maxIter=8", "Top-10 ranked products", "Popularity fallback"], 26)
box(draw, (1270, 450, 1710, 660), PURPLE, "Association Analysis", ["Basket co-purchases", "Support", "Confidence", "Lift"], 26)

arrow(draw, (355, 358), (470, 358))
arrow(draw, (755, 358), (870, 358))
arrow(draw, (1155, 300), (1270, 285))
arrow(draw, (1155, 415), (1270, 555))

# Persisted outputs band
draw.rounded_rectangle((280, 720, 1520, 900), radius=22, fill=WHITE, outline=NAVY, width=4)
draw.text((325, 748), "Persisted Analytics Outputs", font=font(30, True), fill=NAVY)
output_boxes = [
    ((330, 805, 585, 870), GREEN, ["cleaned_purchases", "Parquet"]),
    ((625, 805, 880, 870), BLUE, ["interactions", "Parquet"]),
    ((920, 805, 1175, 870), PURPLE, ["all_customers", "Recommendations"]),
    ((1215, 805, 1470, 870), GOLD, ["summary / quality / evaluation", "JSON + associations"]),
]
for coords, fill, lines in output_boxes:
    draw.rounded_rectangle(coords, radius=12, fill=fill, outline=NAVY, width=2)
    centered(draw, coords, lines, 17, TEXT, True, 3)

arrow(draw, (1490, 285), (1490, 720))
arrow(draw, (1490, 555), (1490, 720))
arrow(draw, (1010, 485), (1010, 720))

# Presentation layer
draw.rounded_rectangle((210, 980, 1590, 1125), radius=22, fill=NAVY, outline=NAVY, width=4)
draw.text((260, 1002), "Presentation Layer", font=font(29, True), fill=WHITE)
for i, (x, label) in enumerate([(600, "Streamlit Dashboard"), (900, "Product Analytics"), (1195, "Personalised Recommendations")]):
    draw.rounded_rectangle((x, 990, x + 250, 1095), radius=14, fill=WHITE, outline="#91BCE4", width=3)
    centered(draw, (x + 8, 1000, x + 242, 1085), label.split(" ") if label != "Streamlit Dashboard" else ["Streamlit", "Dashboard"], 17, NAVY, True, 3)
arrow(draw, (900, 900), (900, 980))

# Footer note
draw.text((70, 1150), "Pipeline: Ingest -> Clean -> Aggregate -> Model -> Evaluate -> Persist -> Present", font=font(20, True), fill=MUTED)

image.save(OUTPUT, dpi=(180, 180))
print(f"Created {OUTPUT}")
