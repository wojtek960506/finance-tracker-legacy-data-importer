import pandas as pd
from pathlib import Path


def combine_finance_data():
  names: list[int | str] = list(range(2015,2025))
  names.append("2015_2024_foreign")

  frames_all = []
  frames_expenses = []
  frames_incomes = []

  for name in names:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" 
    EXPENSES_FILE = DATA_DIR / f"{name}" / f"finance_expenses_{name}.csv"
    INCOMES_FILE = DATA_DIR / f"{name}" / f"finance_incomes_{name}.csv"
    df_expenses = pd.read_csv(EXPENSES_FILE)
    df_incomes = pd.read_csv(INCOMES_FILE)

    frames_all.extend([df_expenses, df_incomes])
    frames_expenses.append(df_expenses)
    frames_incomes.append(df_incomes)

  df_all = pd.concat(frames_all, ignore_index=True).sort_values(by="date")
  df_expenses_all = pd.concat(frames_expenses, ignore_index=True).sort_values(by="date")
  df_incomes_all = pd.concat(frames_incomes, ignore_index=True).sort_values(by="date")

  print("All expenses and incomes", len(df_all))
  print("All expenses", len(df_expenses_all))
  print("All incomes", len(df_incomes_all))

  ALL_EXPENSES_FILE = DATA_DIR / "all" / "finance_expenses_all.csv"
  ALL_INCOMES_FILE = DATA_DIR / "all" / "finance_incomes_all.csv"
  ALL_TRANSACTIONS_FILE = DATA_DIR / "all" / "finance_all.csv"

  df_expenses_all.to_csv(ALL_EXPENSES_FILE, index=False, encoding="utf-8")
  df_incomes_all.to_csv(ALL_INCOMES_FILE, index=False, encoding="utf-8")
  df_all.to_csv(ALL_TRANSACTIONS_FILE, index=False, encoding="utf-8")


if __name__ == "__main__":
  combine_finance_data()
