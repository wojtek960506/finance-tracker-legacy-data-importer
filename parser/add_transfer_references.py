import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[0] / "data" 

def calculate_invalid_my_account_transactions(tmp_df):
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

  TMP_FILE = DATA_DIR / "all" / "tmp_myAccount.csv"
  tmp_df.to_csv(TMP_FILE, index=False, encoding="utf-8")

  TMP_FILE_INVALID = DATA_DIR / "all" / "tmp_myAccount_invalid_amount.csv"
  tmp_df_invalid_amount = tmp_df[tmp_df["amount"].isin(invalid_amounts)]
  tmp_df_invalid_amount.to_csv(TMP_FILE_INVALID, index=False, encoding="utf-8")
  return invalid_amounts

def sort_group_manually(group):
  # TODO add logic for sorting transaction when many are in one day
  # not to have broken refs
  accounts = [
    "pekao",
    "veloBank",
    "nestBank",
    "aliorBank",
    "revolut",
    "mBank",
    "cardByCliq",
    "aliorBank",
    "cash",
    "creditAgricole",
  ]

  return group

def update_data_frames_with_references(df_expenses, df_incomes):
  if len(df_expenses) != len(df_incomes):
    print('references for money transfers cannot be added')
    print('number of expenses should be the same as number of incomes')
    return None
  
  for i in range(len(df_expenses)):
    df_expenses.loc[i, "source_ref_index"] = df_incomes.loc[i, "source_index"]
    df_incomes.loc[i, "source_ref_index"] = df_expenses.loc[i, "source_index"]

  return pd.concat([df_expenses, df_incomes])


def add_transfer_references(should_print=False):
  
  ALL_TRANSACTIONS_FILE = DATA_DIR / "all" / "finance_all.csv"

  df_all = pd.read_csv(ALL_TRANSACTIONS_FILE)
  df_all_my_account = df_all[df_all["category"] == "myAccount"]
  df_all_my_account = df_all_my_account.sort_values(by=["amount", "date"])
  tmp_df = df_all_my_account.drop(columns=["exchange_rate", "currencies", "source_ref_index", "category"])

  if should_print:
    print('NUMBER OF ROWS WITH `MY ACCOUNT` CATEGORY')
    print(len(df_all_my_account))
    print(df_all_my_account)
    print(df_all_my_account.columns)
    print(tmp_df)

  invalid_amounts = calculate_invalid_my_account_transactions(tmp_df)
  if len(invalid_amounts) > 0:
    print('invalid amounts: ', invalid_amounts)
    print('references of money transfers cannot be added')
    return

  out = []

  for _, group in tmp_df.groupby("amount", sort=False):
    group = group.sort_values(by=["date"])
    if len(group) == 2:
      out.append(group)
      continue

    group_to_sort_manually = group[group["description"].str.startswith("Przelew")]
    group_properly_sorted = group[~group["description"].str.startswith("Przelew")]

    out.append(group_properly_sorted)
    out.append(sort_group_manually(group_to_sort_manually))

  # split DataFrame with `myAccount` rows to get expenses and incomes separately
  df_correct_order = pd.concat(out, ignore_index=False)
  df_expenses = df_correct_order[df_correct_order["transaction_type"] == "expense"]
  df_incomes = df_correct_order[df_correct_order["transaction_type"] == "income"]
  df_expenses = df_expenses.reset_index(drop=True)
  df_incomes = df_incomes.reset_index(drop=True)

  df_my_account_with_refs = update_data_frames_with_references(df_expenses, df_incomes)
  
  if df_my_account_with_refs is None:
    return
  
  # create a mapping: source_index → source_ref_index
  mapping = df_my_account_with_refs.set_index("source_index")["source_ref_index"]

  # update main df only where mapping exists
  df_all["source_ref_index"] = df_all["source_index"].map(mapping).combine_first(
    df_all["source_ref_index"]
  )

  # save final DataFrame to a file
  TMP_FILE = DATA_DIR / "all" / "finance_all_transfer_refs.csv"
  df_all.to_csv(TMP_FILE, index=False, encoding="utf-8")

  print('references has been successfully added for `myAccount` transactions.')

if __name__ == "__main__":
  add_transfer_references()