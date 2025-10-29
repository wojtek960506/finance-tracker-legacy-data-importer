import pandas as pd
from pathlib import Path
from typing import List, Union


def check_parsed_file(file_path: Path, columns: List[str]):
  df = pd.read_csv(file_path)
  df_columns = list(df.columns)

  # TODO - check what are the sets of values for:
  #   * currency
  #   * category
  #   * payment_method
  #   * account
  #   * currencies
  #   * transaction_type  


  # check if columns in all files with finance data are the same
  if len(columns) == 0:
    columns = df_columns
  elif columns != df_columns:
    raise Exception(
      "columns names and order should be the same in all parsed files",
      f"Problem with file: {file_path}"
    )
  
  return columns

def check_parsed_files():
  names: List[Union[int, str]] = list(range(2015,2025))
  names.append("2015_2024_foreign")
  
  columns = []
  for name in names:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" / f"{name}"
    EXPENSES_FILE = DATA_DIR / f"finance_expenses_{name}.csv"
    INCOMES_FILE = DATA_DIR / f"finance_incomes_{name}.csv"

    columns = check_parsed_file(EXPENSES_FILE, columns)
    columns = check_parsed_file(INCOMES_FILE, columns)

  
  print('All good')


if __name__ == "__main__":
  check_parsed_files()