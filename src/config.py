from pathlib import Path
from dataclasses import dataclass

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "dataset" / "Online Retail.xlsx"
DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
RECOMMENDATIONS_DIR = DATA_DIR / "recommendations"
OUTPUT_DIR = ROOT / "output"
PLOTS_DIR = OUTPUT_DIR / "plots"


@dataclass(frozen=True)
class ModelConfig:
    rank: int = 10
    max_iter: int = 8
    reg_param: float = 0.1
    alpha: float = 1.0
    top_k: int = 10
    seed: int = 42


def ensure_directories() -> None:
    for path in (DATA_DIR, PROCESSED_DIR, RECOMMENDATIONS_DIR, OUTPUT_DIR, PLOTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
