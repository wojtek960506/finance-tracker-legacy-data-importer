import subprocess
from pathlib import Path


def execute_copying(path_1, path_2):
  print('-' * len(str(path_2)))
  print(path_1)
  print(path_2)

  if path_1.exists():
    print("copying")
    subprocess.run(["cp", str(path_1), str(path_2)], check=True)


def copy_original_finance_spreadsheet(year):
  path_1 = Path(f"~/Downloads/Finanse WZ - {year}.csv").expanduser()
  path_2 = Path(__file__).resolve().parents[0] / f"data/{year}/finance_raw_{year}.csv"
  execute_copying(path_1, path_2)

def copy_original_foreign_finanse_spreadsheet():
  path_1 = Path(f"~/Downloads/Finanse WZ - obce waluty 2015-2024.csv").expanduser()
  path_2 = (
    Path(__file__)
    .resolve()
    .parents[0]
    / f"data/foreign_transactions/foreign_finance_raw_2015_2024.csv"
  )
  execute_copying(path_1, path_2)


for y in range(2015, 2025):
  copy_original_finance_spreadsheet(y)

copy_original_foreign_finanse_spreadsheet()

