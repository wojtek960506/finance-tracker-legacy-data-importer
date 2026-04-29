# Finance Tracker Legacy Data Importer

Utilities for converting legacy finance spreadsheets into transaction CSV files and importing
those CSV files into the Finance Tracker database.

The repository has two parts:

- `parser/` prepares CSV exports from old spreadsheet data.
- `importer/` validates prepared CSV files and writes transactions directly to MongoDB.

## Parser

The parser reads raw CSV files exported from the legacy spreadsheet, cleans them, normalizes
columns, calculates transaction references, and combines everything into import-ready files.

Raw spreadsheet exports are expected in:

```text
parser/data/<name>/finance_raw_<name>.csv
```

The parser currently processes these names:

```text
2015 ... 2025
2015_2024_foreign
2025_foreign
```

Generated files are written under `parser/data/`, which is ignored by Git.
Parser inputs and outputs can contain sensitive financial data, so keep real files out of
commits and treat generated CSVs as private local artifacts.

### Run the Full Parser Pipeline

From the repository root:

```bash
./parser/parse_legacy_data.sh
```

Useful flags:

```bash
./parser/parse_legacy_data.sh --should-copy
./parser/parse_legacy_data.sh --should-print
./parser/parse_legacy_data.sh --should-copy --should-print
```

`--should-copy` copies files from:

```text
<LEGACY_FINANCE_EXPORT_DIR>/<LEGACY_FINANCE_EXPORT_PREFIX> - <name>.csv
```

into the expected `parser/data/<name>/finance_raw_<name>.csv` paths before parsing.

For this option, create `parser/.env`:

```env
LEGACY_FINANCE_EXPORT_PREFIX="Your spreadsheet export prefix"
LEGACY_FINANCE_EXPORT_DIR="~/Downloads"
```

`LEGACY_FINANCE_EXPORT_DIR` is optional and defaults to `~/Downloads`.

The shell script creates `parser/.venv` if needed and installs dependencies from
`parser/requirements.txt`.

### Parser Steps

The full pipeline is defined in `parser/main_get_all.py`:

1. Optionally copy raw spreadsheet exports from the configured export directory.
2. Parse raw CSV files into per-year expenses and incomes files.
3. Calculate exchange transaction references.
4. Collect selector values for review.
5. Combine all years into aggregate CSV files.
6. Add references for `myAccount` transfer transactions.

The final combined file with transfer references is:

```text
parser/data/all/finance_all_transfer_refs.csv
```

### Selector Normalization

During parsing, only system resource names are normalized to API keys. User-specific resource
names are preserved.

System categories:

- `Wymiana -> exchange`
- `Moje konto -> myAccount`

System payment methods:

- `Bankomat -> atm`
- `Karta -> card`
- `Gotówka -> cash`
- `Przelew -> bankTransfer`

System accounts:

- `Gotówka -> cash`

All other category, payment method, and account values pass through unchanged and are treated as
user-specific resources by the importer.

## Importer

The importer reads an import-ready CSV file, validates rows with the local Pydantic transaction
schema, creates missing user-specific resources, inserts transactions, and then resolves
`source_ref_index` references to real MongoDB transaction IDs.

### Setup

From `importer/`, create and activate a virtual environment, then install dependencies:

```bash
cd importer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `importer/.env`:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=finance-tracker
LEGACY_IMPORTER_ADMIN_TOKEN=change-me
```

Adjust the values for your local database and replace `LEGACY_IMPORTER_ADMIN_TOKEN` with a local
secret value. Importer scripts use this token as an admin guard before mutating transactions.

### Import Transactions

Run from the `importer/` directory:

```bash
python -m scripts.import_transactions_csv <owner_id> <csv_file_path>
```

Example:

```bash
python -m scripts.import_transactions_csv 665000000000000000000000 ../parser/data/all/finance_all_transfer_refs.csv
```

The import script refuses to import if:

- the admin token prompt does not match `LEGACY_IMPORTER_ADMIN_TOKEN`;
- the user does not exist;
- the user already has transactions;
- any CSV row fails validation.

### Delete Transactions

Run from the `importer/` directory:

```bash
python -m scripts.delete_transactions <owner_id>
```

This deletes all transactions for the given user.

The delete script also requires the admin token prompt to match
`LEGACY_IMPORTER_ADMIN_TOKEN`.

## CSV Format

The importer expects a header row with these columns. Snake case names are supported, and the
Pydantic schema also accepts camelCase aliases.

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

## Temporary CSV Samples

`importer/tmp_csv/` contains small sanitized CSV files that can be used for quick importer checks.
They include examples of normal expenses, `myAccount` transfer references, and `exchange`
references.

## Notes

- `parser/data/`, virtual environments, `.env`, `__pycache__/`, and local Codex metadata are ignored by Git.
- The parser is a local file transformation tool and does not require admin authentication because it does not mutate database state.
- The importer creates missing category, account, and payment method resources as user-specific resources unless they already exist as user or system resources in MongoDB.
- Import and delete scripts are trusted local admin tools. They require `LEGACY_IMPORTER_ADMIN_TOKEN`, but database credentials should still be scoped carefully.
