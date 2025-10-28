import pandas as pd
from pathlib import Path

YEAR = 2015

# Paths
DATA_DIR = Path(__file__).resolve().parents[0] / "data"
RAW_FILE = DATA_DIR / f"finance_raw_{YEAR}.csv"
EXPENSES_FILE = DATA_DIR / f"finance_expenses_{YEAR}.csv"
INCOMES_FILE = DATA_DIR / f"finance_incomes_{YEAR}.csv"

# load CSV (first 2 rows don't have meaningful data)
df = pd.read_csv(RAW_FILE, skiprows=2) 


# drop all columns whose name starts with (Unnamed) those are empty columns
# both of the lines below have the same effect (keep them just for learning purposes)

# df = df.loc[:, ~df.columns.str.startswith("Unnamed")]
df.drop(columns=[col for col in df.columns if col.startswith("Unnamed")], inplace=True)

# drop all columns which are some additional data calculated based on incomes and expenses
df.drop(columns=[
  col for col in df.columns 
  if col.startswith("Ilość") or col.startswith("ile") or col[-1] in ["2", "3", "4"]
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

def get_full_date(df: pd.DataFrame):
  df["full_date"] = pd.to_datetime(
    df.assign(year=YEAR).loc[:, ["year", "m.", "d."]]
      .rename(columns={"m.": "month", "d.": "day"})
  )
  df.drop(columns=["m.", "d."], inplace=True)
  columns = list(df.columns)
  columns.remove("full_date")
  columns.insert(1, "full_date")
  df = df[columns]
  return df

df_expenses = get_full_date(df_expenses)
df_incomes = get_full_date(df_incomes)

print("expenses", df_expenses.columns)
print("incomes", df_incomes.columns)
print(f"Loaded {len(df_expenses)} of expenses rows")
print(f"Loaded {len(df_incomes)} of incomes rows")

# save prepared data frames to separate CSV files
df_expenses.to_csv(EXPENSES_FILE, index=False, encoding="utf-8")
df_incomes.to_csv(INCOMES_FILE, index=False, encoding="utf-8")