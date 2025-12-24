import pandas as pd
import numpy as np
from pathlib import Path


def add_transfer_references(should_print=False):
  DATA_DIR = Path(__file__).resolve().parents[0] / "data" 
  ALL_TRANSACTIONS_FILE = DATA_DIR / "all" / "finance_all.csv"

  df_all = pd.read_csv(ALL_TRANSACTIONS_FILE)

  df_all_my_account = df_all[df_all["category"] == "myAccount"]

  df_all_my_account = df_all_my_account.sort_values(
    by=[
      "amount",
      "date"
    ]
  )

  tmp_df = df_all_my_account.drop(columns=["exchange_rate", "currencies", "source_ref_index", "category"])

  if should_print:
    print('NUMBER OF ROWS WITH `MY ACCOUNT` CATEGORY')
    print(len(df_all_my_account))
    print(df_all_my_account)
    print(df_all_my_account.columns)
    print(tmp_df)

  current_expense_count = 0
  current_income_count = 0
  current_amount = 0
  invalid_amounts = []
  invalid_amounts_2 = []

  for row in tmp_df.itertuples(index=False):
    amount = row.amount
    transaction_type = row.transaction_type

    if amount != current_amount:
      if current_expense_count != current_income_count:
        invalid_amounts.append(current_amount)
        invalid_amounts_2.append({
          current_amount: {
            "current_expense_count": current_expense_count,
            "current_income_count": current_income_count,
          }
        })
      current_amount = amount

      if transaction_type == 'income':
        current_expense_count = 0
        current_income_count = 1
      else:
        current_expense_count = 1
        current_income_count = 0

    else:
      if transaction_type == 'income':
        current_income_count += 1
      else:
        current_expense_count += 1

  print('invalid amounts', invalid_amounts)
  print('INVALID AMOUNTS DICTS')
  for a in invalid_amounts_2:
    print(a)


  TMP_FILE = DATA_DIR / "all" / "tmp_myAccount.csv"
  tmp_df.to_csv(TMP_FILE, index=False, encoding="utf-8")

  TMP_FILE_INVALID = DATA_DIR / "all" / "tmp_myAccount_invalid_amount.csv"
  tmp_df_invalid_amount = tmp_df[tmp_df["amount"].isin(invalid_amounts)].sort_values(by='date')


  tmp_df_invalid_amount.to_csv(TMP_FILE_INVALID, index=False, encoding="utf-8")

  print('`myAccount` operations saved to a temporary file')
  


if __name__ == "__main__":
  add_transfer_references()