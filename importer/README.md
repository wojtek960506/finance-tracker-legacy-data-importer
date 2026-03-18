CLI tools to import and delete legacy transactions.

Scripts:
- `scripts.delete_transactions`: deletes all transactions for a user.
- `scripts.import_transactions_csv`: imports transactions from a CSV file for a user.

Run scripts as modules from this directory:

```bash
python -m scripts.delete_transactions <owner_id>
```

```bash
python -m scripts.import_transactions_csv <owner_id> <csv_file_path>
```

CSV format:
- Header names are required and should match the columns below (snake_case like the example file,
  or their camelCase aliases).
- Empty values are treated as nulls.
- `ownerId` is not part of the CSV; it is taken from the CLI argument.
- Values from `paymentMethod`, `account`, and `category` columns are added as user-specific
  entities during import in case they aren't already present in the database.

Required columns:
- `source_index` (alias: `sourceIndex`) - integer
- `date` - ISO date or datetime (e.g. `2015-09-24`)
- `description` - string
- `amount` - positive number
- `currency` - string (e.g. `PLN`)
- `category` - string
- `payment_method` - (alias: `paymentMethod`) string
- `account` - string
- `transaction_type` - (alias: `transactionType`) string (`expense` or `income` only)

Optional columns:
- `exchange_rate` - (alias: `exchangeRate`) number
- `currencies` - string
- `source_ref_index` - (alias: `sourceRefIndex`) integer

Validation rules:
- If `category` is `exchange`, then `currencies`, `exchange_rate`, and `source_ref_index`
  must be provided together.
- If `currencies` or `exchange_rate` is provided for a non-exchange transaction,
  both must be provided together.
