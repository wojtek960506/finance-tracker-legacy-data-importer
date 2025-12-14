from pathlib import Path
import pandas as pd

def calculate_single_file_exchange_refs(filename: str, should_print: bool = False):

  DATA_DIR = Path(__file__).resolve().parents[0] / "data" / filename
  EXPENSES_FILE = DATA_DIR / f"finance_expenses_{filename}.csv"
  INCOMES_FILE = DATA_DIR / f"finance_incomes_{filename}.csv"

  df_incomes = pd.read_csv(INCOMES_FILE)
  df_expenses = pd.read_csv(EXPENSES_FILE)

  # Two pointer logic
  index_incomes, index_expenses, num_of_refs = 0, 0, 0

  income_row = df_incomes.iloc[index_incomes]
  expense_row = df_expenses.iloc[index_expenses]

  while index_incomes < len(df_incomes) and index_expenses < len(df_expenses):

    expense_row = df_expenses.iloc[index_expenses]
    income_row = df_incomes.iloc[index_incomes]

    idx_e = expense_row["idx"]
    date_e = expense_row["date"]
    exchange_rate_e = expense_row["exchange_rate"]
    currencies_e = expense_row["currencies"]
    currency_e = expense_row["currency"]
    amount_e = expense_row["amount"]
    category_e = expense_row["category"]

    idx_i = income_row["idx"]
    date_i = income_row["date"]
    exchange_rate_i = income_row["exchange_rate"]
    currencies_i = income_row["currencies"]
    currency_i = income_row["currency"]
    amount_i = income_row["amount"]
    category_i = income_row["category"]

    if (
      date_i == date_e and
      currencies_i == currencies_e and
      exchange_rate_i == exchange_rate_e
    ):
      if (
        (amount_e > amount_i and currencies_e != f"{currency_i}/{currency_e}") or
        (amount_i > amount_e and currencies_e != f"{currency_e}/{currency_i}")
      ):
        raise Exception(f"wrong 'currencies' value in file '{filename}'")
      
      df_incomes.at[index_incomes, "calc_ref_idx"] = idx_e
      df_expenses.at[index_expenses, "calc_ref_idx"] = idx_i 

      index_expenses += 1
      index_incomes += 1
      num_of_refs += 1
      continue

    if (category_e != "exchange"):
      index_expenses += 1
    if (category_i != "exchange"):
      index_incomes += 1


  df_expenses.to_csv(EXPENSES_FILE, index=False, encoding="utf-8")
  df_incomes.to_csv(INCOMES_FILE, index=False, encoding="utf-8")

  if (should_print):
    print(f"number of references added in file '{filename}':", num_of_refs)


def calculate_exchange_refs(should_print=False):
  calculate_single_file_exchange_refs("2015_2024_foreign", should_print)
  calculate_single_file_exchange_refs("2025_foreign", should_print)
  print('calculating exchange refs done')


if __name__ == "__main__":
  calculate_exchange_refs()
