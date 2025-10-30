from pathlib import Path
import pandas as pd


def calculate_exchange_refs(should_print=False):
  DATA_DIR = Path(__file__).resolve().parents[0] / "data" / "2015_2024_foreign"
  EXPENSES_FILE = DATA_DIR / "finance_expenses_2015_2024_foreign.csv"
  INCOMES_FILE = DATA_DIR / "finance_incomes_2015_2024_foreign.csv"

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

    idx_i = income_row["idx"]
    date_i = income_row["date"]
    exchange_rate_i = income_row["exchange_rate"]
    currencies_i = income_row["currencies"]
    currency_i = income_row["currency"]
    amount_i = income_row["amount"]

    if (
      date_i == date_e and
      currencies_i == currencies_e and
      exchange_rate_i == exchange_rate_e
    ):
      if (
        (amount_e > amount_i and currencies_e != f"{currency_i}/{currency_e}") or
        (amount_i > amount_e and currencies_e != f"{currency_e}/{currency_i}")
      ):
        print(idx_e)
        print(idx_i)
        raise Exception("wrong 'currencies' value")
      
      df_incomes.at[index_incomes, "calc_ref_idx"] = idx_e
      df_expenses.at[index_expenses, "calc_ref_idx"] = idx_i 

      index_expenses += 1
      index_incomes += 1
      num_of_refs += 1
      continue

    # if current row in any dataframe cannot be refernce just go to the next one
    if pd.isna(exchange_rate_e) and pd.isna(currencies_e):
      index_expenses += 1
    if pd.isna(exchange_rate_i) and pd.isna(currencies_i):
      index_incomes += 1


  df_expenses.to_csv(EXPENSES_FILE, index=False, encoding="utf-8")
  df_incomes.to_csv(INCOMES_FILE, index=False, encoding="utf-8")

  if (should_print):
    print("number of references added:", num_of_refs)


if __name__ == "__main__":
  calculate_exchange_refs()
