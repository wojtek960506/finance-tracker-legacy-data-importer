Admin and migration CLI tools for legacy transaction data.

These are trusted local admin tools. All commands require the hidden admin token prompt to match
`LEGACY_IMPORTER_ADMIN_TOKEN` from `src/transactions/importing/.env`.

## Setup

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Then create `.env` here with:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=finance-tracker
LEGACY_IMPORTER_ADMIN_TOKEN=change-me
```

## Commands

Run commands from the repository root:

```bash
python -m src.transactions.scripts.list_users
python -m src.transactions.scripts.list_users --json
python -m src.transactions.scripts.list_users --include-raw
python -m src.transactions.scripts.list_ownerless_resources
python -m src.transactions.scripts.list_ownerless_resources --json
python -m src.transactions.scripts.delete_all_empty_users
python -m src.transactions.scripts.delete_all_unused_resources
python -m src.transactions.scripts.delete_user <owner_id>
python -m src.transactions.scripts.delete_resources <owner_id>
python -m src.transactions.scripts.delete_transactions <owner_id>
python -m src.transactions.scripts.import_transactions_csv <owner_id> <csv_file_path>
python -m src.transactions.scripts.import_transactions_csv <owner_id> <csv_file_path> --print
```

## CSV Format

Required columns:

- `source_index` (`sourceIndex`)
- `date`
- `description`
- `amount`
- `currency`
- `category`
- `payment_method` (`paymentMethod`)
- `account`
- `transaction_type` (`transactionType`)

Optional columns:

- `exchange_rate` (`exchangeRate`)
- `currencies`
- `source_ref_index` (`sourceRefIndex`)

Rules:

- Empty values are treated as `null`.
- `ownerId` is not part of the CSV; it is taken from the CLI argument.
- `category`, `payment_method`, and `account` values are created as user-specific resources if needed.
- If `category` is `exchange`, then `currencies`, `exchange_rate`, and `source_ref_index` must be provided together.
- If `currencies` or `exchange_rate` is provided for a non-exchange transaction, both must be provided together.
