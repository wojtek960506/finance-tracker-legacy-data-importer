import pandas as pd
from pathlib import Path


def check_columns(df: pd.DataFrame, columns: list[str], file_path):
  df_columns = list(df.columns)

  # check if columns in all files are the same
  if len(columns) == 0:
    columns = df_columns
  elif columns != df_columns:
    raise Exception(
      "columns names and order should be the same in all parsed files",
      f"Problem with file: {file_path}"
    )
  
  return columns

def get_values_for_selectors(df: pd.DataFrame, columns_values: dict[str, set[str]]):
  for column_name, value in columns_values.items():
    value.update(df[column_name].dropna().unique())

  return columns_values

def check_parsed_files(should_print=False):
  
  columns: list[str] = []
  columns_values: dict[str, set[str]] = {
    "currency": set(),
    "category": set(),
    "payment_method": set(),
    "account": set(),
    "currencies": set(),
    "transaction_type": set(),
  }

  names: list[int | str] = list(range(2015,2025))
  names.append("2015_2024_foreign")

  for name in names:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" / f"{name}"
    EXPENSES_FILE = DATA_DIR / f"finance_expenses_{name}.csv"
    INCOMES_FILE = DATA_DIR / f"finance_incomes_{name}.csv"
    df_expenses = pd.read_csv(EXPENSES_FILE)
    df_incomes = pd.read_csv(INCOMES_FILE)

    columns = check_columns(df_expenses, columns, EXPENSES_FILE)
    columns = check_columns(df_incomes, columns, INCOMES_FILE)

    if (should_print):
      columns_values = get_values_for_selectors(df_expenses, columns_values)
      columns_values = get_values_for_selectors(df_incomes, columns_values)

  if (should_print):
    print('All good with column names')
    for column_name, values in columns_values.items():
      print(f"{column_name} - {values}")

  print("checking done")


if __name__ == "__main__":
  check_parsed_files()