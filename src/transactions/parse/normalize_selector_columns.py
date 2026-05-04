import pandas as pd


account_map = {
  "Gotówka": "cash"
}

# System resource names need to be mapped exactly to their API keys.
# The rest are user-specific resources and should keep their original names.
category_map = {
  "Wymiana": "exchange",
  "Moje konto": "myAccount"
}

payment_method_map = {
  "Bankomat": "atm",
  "Przelew": "bankTransfer",
  "Gotówka": "cash",
  "Karta": "card"
}

def normalize_selector_columns(df: pd.DataFrame):
  df["account"] = df["account"].replace(account_map)
  df["category"] = df["category"].replace(category_map)
  # keep the 'currency' column as it is now because those are standard codes
  df["payment_method"] = df["payment_method"].replace(payment_method_map)
