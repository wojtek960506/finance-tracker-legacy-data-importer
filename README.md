# Finance Tracker Legacy Data Tools

Utilities for turning legacy spreadsheet exports into import-ready transaction CSV files and for
running local admin/import workflows against the Finance Tracker database.

## Repository Layout

```text
src/
  shared/
    api/
    config/
    db/
    decorators/
    utils/
  transactions/
    importing/
    parse/
    schema/
    scripts/
data/
  transactions/
    import_samples/
    parse/
```

- `src/shared/` contains reusable infrastructure that future domains can share.
- `src/transactions/parse/` contains the legacy transaction parsing pipeline.
- `src/transactions/importing/` contains transaction import/admin services and setup docs.
- `src/transactions/scripts/` contains transaction CLI entrypoints.
- `data/transactions/parse/` holds parser inputs and generated outputs.
- `data/transactions/import_samples/` holds small sanitized sample CSV files.

## Transactions Parser

Raw spreadsheet exports are expected in:

```text
data/transactions/parse/<name>/finance_raw_<name>.csv
```

The parser currently processes:

```text
2015 ... 2025
2015_2024_foreign
2025_foreign
```

Run the full parser pipeline from the repository root:

```bash
./src/transactions/parse/parse_legacy_data.sh
./src/transactions/parse/parse_legacy_data.sh --should-copy
./src/transactions/parse/parse_legacy_data.sh --should-print
./src/transactions/parse/parse_legacy_data.sh --should-copy --should-print
```

If you use `--should-copy`, create `src/transactions/parse/.env`:

```env
LEGACY_FINANCE_EXPORT_PREFIX="Your spreadsheet export prefix"
LEGACY_FINANCE_EXPORT_DIR="~/Downloads"
```

`LEGACY_FINANCE_EXPORT_DIR` is optional and defaults to `~/Downloads`.

The shell script creates `src/transactions/parse/.venv` if needed and installs dependencies from
[`src/transactions/parse/requirements.txt`](/home/wojtek960506/Programming/own_projects/finance-tracker/finance-tracker-legacy-data-importer/src/transactions/parse/requirements.txt).

The final combined file with transfer references is:

```text
data/transactions/parse/all/finance_all_transfer_refs.csv
```

During parsing, only system resource names are normalized to API keys. User-specific resource
names are preserved.

## Transactions Importing

From [`src/transactions/importing`](/home/wojtek960506/Programming/own_projects/finance-tracker/finance-tracker-legacy-data-importer/src/transactions/importing), create and activate a virtual environment, then install dependencies:

```bash
cd src/transactions/importing
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `src/transactions/importing/.env`:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=finance-tracker
LEGACY_IMPORTER_ADMIN_TOKEN=change-me
```

Run transaction admin/import scripts from the repository root:

```bash
python -m src.transactions.scripts.list_users
python -m src.transactions.scripts.list_ownerless_resources
python -m src.transactions.scripts.delete_resources <owner_id>
python -m src.transactions.scripts.delete_user <owner_id>
python -m src.transactions.scripts.delete_all_unused_resources
python -m src.transactions.scripts.delete_all_empty_users
python -m src.transactions.scripts.delete_transactions <owner_id>
python -m src.transactions.scripts.import_transactions_csv <owner_id> <csv_file_path>
```

Example import:

```bash
python -m src.transactions.scripts.import_transactions_csv \
  665000000000000000000000 \
  data/transactions/parse/all/finance_all_transfer_refs.csv
```

Use `--print` with the import command to show resource lookup/creation logs.

## Transaction CSV Format

Required columns:

- `source_index`
- `date`
- `description`
- `amount`
- `currency`
- `category`
- `payment_method`
- `account`
- `transaction_type`

Optional columns:

- `exchange_rate`
- `currencies`
- `source_ref_index`

Rules:

- Empty CSV values are treated as `null`.
- `transaction_type` must be `expense` or `income`.
- `amount` must be positive.
- If `category` is `exchange`, then `currencies`, `exchange_rate`, and `source_ref_index` must be provided together.
- If a non-exchange transaction has `currencies` or `exchange_rate`, both must be provided together.
- `source_ref_index` points to another row's `source_index`; after import it is converted to a real transaction reference.

## Notes

- `data/transactions/parse/`, virtual environments, `.env` files, `__pycache__/`, and local Codex metadata are ignored by Git.
- The parser is local-only and does not require admin authentication because it does not mutate database state.
- Import commands create missing category, account, and payment method resources as user-specific resources unless they already exist as user or system resources in MongoDB.
