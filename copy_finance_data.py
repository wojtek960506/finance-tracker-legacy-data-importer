import subprocess
from pathlib import Path
from typing import List, Union


def execute_copying(path_1, path_2):
  print('-' * len(str(path_2)))
  print(path_1)
  print(path_2)

  if path_1.exists():
    print("copying")
    subprocess.run(["cp", str(path_1), str(path_2)], check=True)


def copy_original_finance_spreadsheet(name):
  path_1 = Path(f"~/Downloads/Finanse WZ - {name}.csv").expanduser()
  path_2 = Path(__file__).resolve().parents[0] / f"data/{name}/finance_raw_{name}.csv"
  execute_copying(path_1, path_2)


def copy_finance_data():
  names: List[Union[int, str]] = list(range(2015,2025))
  names.append("2015_2024_foreign")

  for name in names:
    copy_original_finance_spreadsheet(name)


if __name__ == "__main__":
  copy_finance_data()