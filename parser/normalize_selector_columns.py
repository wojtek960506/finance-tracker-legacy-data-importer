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

category_map = {
  "Jedzenie": "food",
  "Inwestycje": "investments",
  "Wymiana": "exchange",
  "Moje konto": "myAccount",
  "Transport": "transport",
  "Zwrot": "refund",
  "Ubrania": "clothing",
  "Wpłatomat": "cashDepositMachine",
  "Noclegi": "accommodation",
  "Darowizna": "donation",
  "Meble": "furniture",
  "Rozrywka": "entertainment",
  "Zdrowie": "health",
  "Praca": "work",
  "Sport": "sport",
  "Inne": "other",
  "Edukacja": "education",
  "Elektronika": "electronics",
  "Bankomat": "atm",
  "Allegro": "allegro",
  "Media": "utilities"
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