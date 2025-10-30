import subprocess
from pathlib import Path


def execute_copying(path_1: str, path_2: str, should_print: bool):
  if should_print:
    print('-' * len(str(path_2)))
    print(path_1)
    print(path_2)

  if path_1.exists():
    if should_print:
      print("copying")
    subprocess.run(["cp", str(path_1), str(path_2)], check=True)


def copy_original_finance_spreadsheet(name: str, should_print: bool):
  path_1 = Path(f"~/Downloads/Finanse WZ - {name}.csv").expanduser()
  path_2 = Path(__file__).resolve().parents[0] / f"data/{name}/finance_raw_{name}.csv"
  execute_copying(path_1, path_2, should_print)


def copy_finance_data(should_print: bool = False):
  names: list[int | str] = list(range(2015,2025))
  names.append("2015_2024_foreign")

  for name in names:
    copy_original_finance_spreadsheet(name, should_print)

  print("copying done")

if __name__ == "__main__":
  copy_finance_data()