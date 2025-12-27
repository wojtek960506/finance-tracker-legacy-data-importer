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
  accounts = [
    "pekao",
    "veloBank",
    "nestBank",
    "aliorBank",
    "revolut",
    "mBank",
    "cardByCliq",
    "cash",
    "creditAgricole",
  ]

  if len(group) == 0:
    return group

  group_expense = group[group["transaction_type"] == "expense"]
  group_income = group[group["transaction_type"] == "income"]

  if len(group_expense) != len(group_income):
    raise ValueError(
      'there should be the same number of expenses and incomes within group (the same amount)'
    )

  from_to_pairs = []

  for row in group_expense.itertuples(index=False):
    desc = row.description
    desc = desc.replace(" ", "")
    desc = desc.lower()
  
    from_account = ""
    from_index = len(desc)
    for account in accounts:
      account = account.lower()
      index = desc.find(account)
      if index != -1 and index < from_index:
        from_index = index
        from_account = account

    to_account = ""
    for account in accounts:
      account = account.lower()
      index = desc.find(account, from_index + len(from_account))
      if index != -1:
        to_account = account
        break

    if (from_account == "" or to_account == ""):
      print('ERRORO ERRORO ERRORO ERRORO')
      print('desc', desc)

    from_to_pairs.append((from_account, to_account))
  
  remaining_incomes = group_income.copy()
  sorted_group_incomes = []

  for _, to_acc in from_to_pairs:
    mask = (
      remaining_incomes["account"]
      .str.lower()
      .str.replace(" ", "")
      == to_acc
    )

    if not mask.any():
        raise ValueError(f"No income found for account '{to_acc}'")
    
    # take the first matching income
    row = remaining_incomes[mask].iloc[0]
    sorted_group_incomes.append(row)

    # REMOVE it so it cannot be reused
    remaining_incomes = remaining_incomes.drop(row.name)
  

  sorted_df = pd.DataFrame(sorted_group_incomes)
  result = pd.concat([group_expense, sorted_df], ignore_index=True)

  return result

def update_data_frames_with_references(df_expenses, df_incomes):
  if len(df_expenses) != len(df_incomes):
    raise ValueError(
      'references for money transfers cannot be added' +
      'number of expenses should be the same as number of incomes'
    )
  
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
    raise ValueError(
      f"invalid amounts: {invalid_amounts}" +
      'references of money transfers cannot be added'
    )

  out = []

  for _, group in tmp_df.groupby("amount", sort=False):
    group = group.sort_values(by=["date"])
    if len(group) == 2:
      out.append(group)
      continue

    group_to_sort_manually = group[group["description"].str.startswith("Przelew z")]
    group_properly_sorted = group[~group["description"].str.startswith("Przelew z")]

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