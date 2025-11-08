import pandas as pd
from pathlib import Path
from normalize_selector_columns import normalize_selector_columns


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

def parse_number(x: int | float | str, to_int: bool):
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
    # because there are some NaN values in this column the whole column is cast to 'float'
    df['ref_lp'] = df['ref_lp'].apply(lambda x: parse_number(x, True))
  except:
    pass

def rename_columns(df: pd.DataFrame):
  df.rename(
    columns= {
      "lp.": "idx",
      "full_date": "date",
      "nazwa": "description",
      "wartość": "amount",
      "waluta": "currency",
      "kategoria": "category",
      "rodzaj_operacji": "payment_method",
      "konto": "account",
      "kurs_wymiany": "exchange_rate",
      "waluty": "currencies", # currencies for exchange_rate
    },
    inplace=True
  )

def add_missing_columns(df: pd.DataFrame, transaction_type: str):
  if not "exchange_rate" in df.columns:
    df["exchange_rate"] = pd.NA
  if not "currencies" in df.columns:
    df["currencies"] = pd.NA
  
  df["calc_ref_idx"] = pd.NA
  df["transaction_type"] = transaction_type


def drop_unnecessary_columns(df: pd.DataFrame):
  # drop all columns whose name starts with (Unnamed) - those are empty columns
  df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")], inplace=True)

  # drop all columns which are some additional data calculated based on incomes and expenses
  df.drop(
    columns=[
      col for col in df.columns 
      if (col.startswith("Ilość") or col.startswith("ile") or
          col[-1] in ["2", "3", "4", "5", "6", "7"])
    ],
    inplace=True
  )


def print_info(year: str, df_expenses: pd.DataFrame, df_incomes: pd.DataFrame):
  print('*'*100)
  print("Year:", year)
  print(f"Loaded {len(df_expenses)} of expenses rows")
  print(f"Loaded {len(df_incomes)} of incomes rows")


def parse_finance_spreadsheet(
  raw_file: Path,
  expenses_file: Path,
  incomes_file: Path,
  year: int = None,
  should_print: bool = False
):
  # load CSV (first 2 rows don't have meaningful data)
  df = pd.read_csv(raw_file, skiprows=2)

  drop_unnecessary_columns(df)

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

  # clean numbers as they can have some spaces from formatting and commas instead of dots
  clean_numbers(df_expenses)
  clean_numbers(df_incomes)

  # rename columns to be in english and match Transaction schema from Node.js server
  # here columns are in snake_case and in Node.js server are in camelCase
  rename_columns(df_expenses)
  rename_columns(df_incomes)

  # add columns for all files to match the schema
  add_missing_columns(df_expenses, "expense")
  add_missing_columns(df_incomes, "income")

  if year is not None:
    df_expenses.insert(loc=4, column="currency", value="PLN")
    df_incomes.insert(loc=4, column="currency", value="PLN")

  # normalize values in columns which are "selector-based"
  normalize_selector_columns(df_expenses)
  normalize_selector_columns(df_incomes)

  # save prepared data frames to separate CSV files
  df_expenses.to_csv(expenses_file, index=False, encoding="utf-8")
  df_incomes.to_csv(incomes_file, index=False, encoding="utf-8")

  if should_print:
    print_info(year, df_expenses, df_incomes)


def parse_finance_data(should_print= False):
  names: list[int | str] = list(range(2015,2025))
  names.append("2015_2024_foreign")
  
  for name in names:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" / f"{name}"
    RAW_FILE = DATA_DIR / f"finance_raw_{name}.csv"
    EXPENSES_FILE = DATA_DIR / f"finance_expenses_{name}.csv"
    INCOMES_FILE = DATA_DIR / f"finance_incomes_{name}.csv"

    year = name if isinstance(name, int) else None
    parse_finance_spreadsheet(RAW_FILE, EXPENSES_FILE, INCOMES_FILE, year, should_print)

  print("parsing done")

  
if __name__ == "__main__":
  parse_finance_data()