import pandas as pd
from pathlib import Path
import sys
from typing import Union


def get_full_date(df: pd.DataFrame, year: int = None):
  
  if year is None:
    df["full_date"] = pd.to_datetime(
      df.loc[:, ["r.", "m.", "d."]]
        .rename(columns={"r.": "year", "m.": "month", "d.": "day"})
    )
  else:
    df["full_date"] = pd.to_datetime(
      df.assign(year=year ).loc[:, ["year", "m.", "d."]]
        .rename(columns={"m.": "month", "d.": "day"})
    )

  df.drop(columns=["r.", "m.", "d."], inplace=True, errors="ignore")
  columns = list(df.columns)
  columns.remove("full_date")
  columns.insert(1, "full_date")
  df = df[columns]
  return df

def parse_number(x: Union[int, float, str], to_int: bool):
  if pd.isna(x):
    return x

  if isinstance(x, str):
    x = x.replace('\xa0', '') # remove non-breaking space
    x = x.replace(' ', '')    # remove regular spaces
    x = x.replace(',', '.')   # replace comma with dot

  return int(x) if to_int else float(x) 

def clean_numbers(df: pd.DataFrame):
  df['lp.'] = df['lp.'].apply(lambda x: parse_number(x, True))
  df['wartość'] = df['wartość'].apply(lambda x: parse_number(x, False))
  try:
    df['kurs_wymiany'] = df['kurs_wymiany'].apply(lambda x: parse_number(x, False))
    print('g')
    # because there are some NaN values in this column the whole column is cast to 'float'
    df['ref_lp'] = df['ref_lp'].apply(lambda x: parse_number(x, True))
  except:
    pass


def parse_finance_spreadsheet(
  raw_file: Path,
  expenses_file: Path,
  incomes_file: Path,
  year: int = None
):
  # load CSV (first 2 rows don't have meaningful data)
  df = pd.read_csv(raw_file, skiprows=2)

  # drop all columns whose name starts with (Unnamed) - those are empty columns
  # both of the lines below have the same effect (keep them just for learning purposes)

  # df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
  df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")], inplace=True)

  # drop all columns which are some additional data calculated based on incomes and expenses
  df.drop(columns=[
    col for col in df.columns 
    if col.startswith("Ilość") or col.startswith("ile") or col[-1] in ["2", "3", "4", "5", "6", "7"]
  ], inplace=True)

  # split data to expenses and incomes
  df_expenses = df[[col for col in df.columns if not col.endswith(".1")]]
  df_incomes = df[[col for col in df.columns if col.endswith(".1")]]

  # clean names of columns in both new dataframes
  df_incomes.columns = df_incomes.columns.str.replace(r"\.1$", "", regex=True)
  df_expenses.columns = df_expenses.columns.str.strip().str.lower().str.replace(" ", "_")
  df_incomes.columns = df_incomes.columns.str.strip().str.lower().str.replace(" ", "_")

  # drop totally empty rows
  df_expenses = df_expenses.dropna(how="all")
  df_incomes = df_incomes.dropna(how="all")

  # clean columns for date
  df_expenses = get_full_date(df_expenses, year)
  df_incomes = get_full_date(df_incomes, year)

  print('*'*100)
  print("Year:", year)
  print(f"Loaded {len(df_expenses)} of expenses rows")
  print(f"Loaded {len(df_incomes)} of incomes rows")

  # clean numbers as they can have some spaces from formatting and commas instead of dots
  clean_numbers(df_expenses)
  clean_numbers(df_incomes)

  # save prepared data frames to separate CSV files
  df_expenses.to_csv(expenses_file, index=False, encoding="utf-8")
  df_incomes.to_csv(incomes_file, index=False, encoding="utf-8")

def main():
  if len(sys.argv) > 1:
    years = [sys.argv[1]]
    print(f"Year passed: {sys.argv[1]}")
  else:
    years = list(range(2015,2025))
    
  # parse transactions in PLN
  for year in years:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" / f"{year}"
    RAW_FILE = DATA_DIR / f"finance_raw_{year}.csv"
    EXPENSES_FILE = DATA_DIR / f"finance_expenses_{year}.csv"
    INCOMES_FILE = DATA_DIR / f"finance_incomes_{year}.csv"
    
    parse_finance_spreadsheet(RAW_FILE, EXPENSES_FILE, INCOMES_FILE, year)

  # parse foreign transactions
  DATA_DIR = Path(__file__).resolve().parents[0] / "data" / "foreign_transactions"
  RAW_FILE = DATA_DIR / "foreign_finance_raw_2015_2024.csv"
  EXPENSES_FILE = DATA_DIR / "foreign_finance_expenses_2015_2024.csv"
  INCOMES_FILE = DATA_DIR / "foreign_finance_incomes_2015_2024.csv"
  parse_finance_spreadsheet(RAW_FILE, EXPENSES_FILE, INCOMES_FILE)
  
if __name__ == "__main__":
  main()