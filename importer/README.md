Admin and migration CLI tools for legacy Finance Tracker data.

These are trusted local admin and migration tools. All scripts require the hidden admin token prompt
to match `LEGACY_IMPORTER_ADMIN_TOKEN` from `.env`.

Scripts:
- `scripts.delete_all_empty_users`: deletes all users who have neither transactions nor user-owned resources.
- `scripts.delete_all_unused_resources`: deletes all user-owned named resources for users with no transactions.
- `scripts.delete_user`: deletes a user only when they have no transactions and no user-owned resources.
- `scripts.delete_resources`: deletes user-owned named resources not used by any transaction.
- `scripts.list_ownerless_resources`: lists suspicious user-owned resources with missing `ownerId`.
- `scripts.list_users`: lists users in a table with transaction and named resource counts.
- `scripts.delete_transactions`: deletes all transactions for a user.
- `scripts.import_transactions_csv`: imports transactions from a CSV file for a user.

Run scripts as modules from this directory:

```bash
python -m scripts.list_users
```

```bash
python -m scripts.list_users --json
python -m scripts.list_users --include-raw
```

```bash
python -m scripts.list_ownerless_resources
```

```bash
python -m scripts.list_ownerless_resources --json
```

This script lists suspicious resource documents where `type` is `user` but `ownerId` is missing
or null. System resources are not included.

```bash
python -m scripts.delete_all_empty_users
```

This script requires the admin token prompt and then the exact confirmation text
`DELETE ALL EMPTY USERS <count>`, where you must calculate `<count>` yourself from the shown
number of users to delete.

```bash
python -m scripts.delete_all_unused_resources
```

This script requires the admin token prompt and then the exact confirmation text
`DELETE ALL UNUSED RESOURCES <sum>`, where you must calculate `<sum>` yourself from the shown
accounts, categories, and payment methods counts.

```bash
python -m scripts.delete_user <owner_id>
```

This script requires the admin token prompt and the exact confirmation text `DELETE USER`.
It returns early with current `transactions`, `accounts`, `categories`, and `paymentMethods`
counts if the user still owns any of them.

```bash
python -m scripts.delete_resources <owner_id>
```

This script requires both the admin token prompt and the exact confirmation text
`DELETE RESOURCES`. Only unused user-owned resources are deleted.

```bash
python -m scripts.delete_transactions <owner_id>
```

This script requires both the admin token prompt and the exact confirmation text
`DELETE TRANSACTIONS <count>`, where you must calculate `<count>` yourself from the shown
transaction count for the target user.

```bash
python -m scripts.import_transactions_csv <owner_id> <csv_file_path>
```

```bash
python -m scripts.import_transactions_csv <owner_id> <csv_file_path> --print
```

Use `--print` to show resource lookup and creation logs during import. Final success and error
results are printed regardless of this flag.

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
