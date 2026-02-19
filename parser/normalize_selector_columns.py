import pandas as pd


account_map = {
  "Pekao": "pekao",
  "VeloBank": "veloBank",
  "Nest Bank": "nestBank",
  "Alior Bank": "aliorBank",
  "Revolut": "revolut",
  "mBank": "mBank",
  "CardByCliq": "cardByCliq",
  "Alior": "aliorBank",
  "Gotówka": "cash",
  "Credit Agricole": "creditAgricole"
}

# `myAccount` and `exchange` are system categories so they need to be mapped exactly to its keys
# in the API. The rest are user categories and they are available only for given user
# I will keep their names in Polish and for now they will not be translated to any other
# language
category_map = {
  "Jedzenie": "Jedzenie",       # Food
  "Inwestycje": "Inwestycje",   # Investments
  "Wymiana": "exchange",        # system category
  "Moje konto": "myAccount",    # system category
  "Transport": "Transport",     # Transport
  "Zwrot": "Zwrot",             # Refund
  "Ubrania": "Ubrania",         # Clothing
  "Wpłatomat": "Wpłatomat",     # Cash Deposit Machine
  "Noclegi": "Noclegi",         # Accommodation
  "Darowizna": "Darowizna",     # Donation
  "Meble": "Meble",             # Furniture
  "Rozrywka": "Rozrywka",       # Entertainment
  "Zdrowie": "Health",          # Health
  "Praca": "Praca",             # Work
  "Sport": "Sport",             # Sport
  "Inne": "Inne",               # Other
  "Edukacja": "Edukacja",       # Education
  "Elektronika": "Elektronika", # Electronics
  "Bankomat": "Bankomat",       # ATM
  "Allegro": "Allegro",         # Allegro
  "Media": "Media"              # Utilities
}

currency_map = {
  "PLN": "pln",
  "EUR": "eur",
  "CZK": "czk",
  "GBP": "gbp",
  "USD": "usd",
  "HUF": "huf",
  "RON": "ron"
}

payment_method_map = {
  "Bankomat": "atm",
  "Przelew": "bankTransfer",
  "Gotówka": "cash",
  "BLIK": "blik",
  "Opłata": "fee",
  "Uznanie": "incomingTransfer",
  "Wpłatomat": "cashDepositMachine",
  "Karta": "card"
}

def normalize_selector_columns(df: pd.DataFrame):
  df["account"] = df["account"].map(account_map)
  df["category"] = df["category"].map(category_map)
  # keep the 'currency' column as it is now because those are standard codes
  # df["currency"] = df["currency"].map(currency_map)
  df["payment_method"] = df["payment_method"].map(payment_method_map)
  