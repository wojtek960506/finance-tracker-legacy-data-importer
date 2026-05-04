from pathlib import Path


PARSE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PARSE_DIR.parents[2]
DATA_DIR = REPO_ROOT / "data" / "transactions" / "parse"
