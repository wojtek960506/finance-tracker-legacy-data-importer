import subprocess
import os
from pathlib import Path
from dotenv import load_dotenv

PARSER_DIR = Path(__file__).resolve().parents[0]
DATA_DIR = PARSER_DIR.parents[2] / "data" / "transactions" / "parse"
load_dotenv(PARSER_DIR / ".env")


def get_legacy_export_prefix() -> str:
  prefix = os.getenv("LEGACY_FINANCE_EXPORT_PREFIX")
  if prefix is None or prefix.strip() == "":
    raise ValueError(
      "LEGACY_FINANCE_EXPORT_PREFIX has to be set in "
      "src/transactions/parse/.env when using --should-copy"
    )
  return prefix


def get_legacy_export_dir() -> Path:
  export_dir = os.getenv("LEGACY_FINANCE_EXPORT_DIR", "~/Downloads")
  return Path(export_dir).expanduser()


def execute_copying(path_1: str, path_2: str, should_print: bool):
  if should_print:
    print('-' * len(str(path_2)))
    print(path_1)
    print(path_2)

  if path_1.exists():
    # when the target path (path_2) does not exist then it is created
    path_2.parent.mkdir(parents=True, exist_ok=True)

    if should_print:
      print("copying")
    subprocess.run(["cp", str(path_1), str(path_2)], check=True)


def copy_original_finance_spreadsheet(name: str, should_print: bool):
  export_prefix = get_legacy_export_prefix()
  export_dir = get_legacy_export_dir()
  path_1 = export_dir / f"{export_prefix} - {name}.csv"
  path_2 = DATA_DIR / f"{name}" / f"finance_raw_{name}.csv"
  execute_copying(path_1, path_2, should_print)


def copy_finance_data(should_print: bool = False):
  names: list[int | str] = list(range(2015,2026))
  names.append("2015_2024_foreign")
  names.append("2025_foreign")

  for name in names:
    copy_original_finance_spreadsheet(name, should_print)

  print("copying done")

if __name__ == "__main__":
  copy_finance_data()
