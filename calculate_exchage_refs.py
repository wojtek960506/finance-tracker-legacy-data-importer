from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[0] / "data" / "foreign_transactions"
EXPENSES_FILE = DATA_DIR / "foreign_finance_expenses_2015_2024.csv"
INCOMES_FILE = DATA_DIR / "foreign_finance_incomes_2015_2024.csv"

df_incomes = pd.read_csv(INCOMES_FILE)
df_expenses = pd.read_csv(EXPENSES_FILE)

df_incomes['calc_ref_idx'] = -1
df_expenses['calc_ref_idx'] = -1

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

  idx_i = income_row["idx"]
  date_i = income_row["date"]
  exchange_rate_i = income_row["exchange_rate"]
  currencies_i = income_row["currencies"]

  # TODO maybe add a check if currencies are properly specified

  if (
    date_i == date_e and
    currencies_i == currencies_e and
    exchange_rate_i == exchange_rate_e
  ):
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

print("number of references added:", num_of_refs)
