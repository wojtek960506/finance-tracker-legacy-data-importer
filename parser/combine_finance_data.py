import pandas as pd
import numpy as np
from pathlib import Path


def combine_finance_data(should_print=False):
  names: list[int | str] = list(range(2015,2026))
  names.append("2015_2024_foreign")
  names.append("2025_foreign")

  frames_all = []
  frames_expenses = []
  frames_incomes = []


  cn_idx = "idx"
  cn_calc_ref_idx = "calc_ref_idx"
  cn_source_index = "source_index"
  cn_source_ref_index = "source_ref_index"

  # used for setting proper 'real_idx' - it will be used to set connections with real IDs from
  # database when many transactions are created based on the CSV file created with this function
  total_rows = 0

  for name in names:
    DATA_DIR = Path(__file__).resolve().parents[0] / "data" 
    EXPENSES_FILE = DATA_DIR / f"{name}" / f"finance_expenses_{name}.csv"
    INCOMES_FILE = DATA_DIR / f"{name}" / f"finance_incomes_{name}.csv"
    df_expenses = pd.read_csv(EXPENSES_FILE)
    df_incomes = pd.read_csv(INCOMES_FILE)

    # ----------------------------------------------------------------------------------------
    # here is the logic with creating new column `source_index` and `source_ref_index`
    # basically I am using a little "brute force logic" as I am just increasing the `idx`
    # by the number of rows in the previous documents in the loop. As this is just operation
    # for cleaning old data and new data will be added via UI with proper values then it works well
    len_expenses = len(df_expenses)
    len_incomes = len(df_incomes)  

    # index of each expense is increase by the number of total rows
    # ('idx' of first expenses stays the same)

    total_rows_expenses = total_rows

    df_expenses[cn_source_index] = df_expenses[cn_idx] + total_rows_expenses

    total_rows_incomes = total_rows + len_expenses

    df_incomes[cn_source_index] = df_incomes[cn_idx] + total_rows_incomes

    # Values for "source_index" are fine now I have to set values for "source_ref_index".
    # So in expenses I extend reference to income by the same number by which I was extending
    # idx for income and vice versa

    df_expenses[cn_source_ref_index] = np.where(
      (df_expenses[cn_calc_ref_idx].notna()) & (df_expenses[cn_calc_ref_idx] > 0),
      df_expenses[cn_calc_ref_idx] + total_rows_incomes,
      df_expenses[cn_calc_ref_idx]
    )

    df_incomes[cn_source_ref_index] = np.where(
      (df_incomes[cn_calc_ref_idx].notna()) & (df_incomes[cn_calc_ref_idx] > 0),
      df_incomes[cn_calc_ref_idx] + total_rows_expenses,
      df_incomes[cn_calc_ref_idx]
    )

    total_rows = total_rows + len_expenses + len_incomes
    # ----------------------------------------------------------------------------------------

    # remove `idx` and `calc_ref_idx` columns as they are not meaningful
    df_expenses.drop(columns=[cn_idx, cn_calc_ref_idx], inplace=True)
    df_incomes.drop(columns=[cn_idx, cn_calc_ref_idx], inplace=True)

    # move column "source_index" to the first position
    expenses_cols = [cn_source_index] + [c for c in df_expenses.columns if c != cn_source_index]
    incomes_cols = [cn_source_index] + [c for c in df_incomes.columns if c != cn_source_index]
    df_expenses = df_expenses[expenses_cols]
    df_incomes = df_incomes[incomes_cols]

    frames_all.extend([df_expenses, df_incomes])
    frames_expenses.append(df_expenses)
    frames_incomes.append(df_incomes)

  sort_by = cn_source_index

  df_all = pd.concat(frames_all, ignore_index=True).sort_values(by=sort_by)
  df_expenses_all = pd.concat(frames_expenses, ignore_index=True).sort_values(by=sort_by)
  df_incomes_all = pd.concat(frames_incomes, ignore_index=True).sort_values(by=sort_by)

  if should_print:
    print("All expenses and incomes", len(df_all))
    print("All expenses", len(df_expenses_all))
    print("All incomes", len(df_incomes_all))

  ALL_EXPENSES_FILE = DATA_DIR / "all" / "finance_expenses_all.csv"
  ALL_INCOMES_FILE = DATA_DIR / "all" / "finance_incomes_all.csv"
  ALL_TRANSACTIONS_FILE = DATA_DIR / "all" / "finance_all.csv"

  df_expenses_all.to_csv(ALL_EXPENSES_FILE, index=False, encoding="utf-8")
  df_incomes_all.to_csv(ALL_INCOMES_FILE, index=False, encoding="utf-8")
  df_all.to_csv(ALL_TRANSACTIONS_FILE, index=False, encoding="utf-8")

  print("combining data done")


if __name__ == "__main__":
  combine_finance_data()
