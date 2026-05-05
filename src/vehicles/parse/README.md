CLI for extracting structured fuel tables from vehicle spreadsheet CSV exports.

Run the parser from the repository root:

```bash
python -m src.vehicles.parse.extract_fuel_tables data/vehicles/parse/car_2005/original_fuel_data.csv
python -m src.vehicles.parse.extract_fuel_tables data/vehicles/parse/motorcycle_2001/original_fuel_data.csv
```

Parser inputs and outputs live under `data/vehicles/parse/`.

Each run writes the extracted tables into the matching vehicle's `fuel_tables/` directory:

- `fuel_entries.csv`
- `fuel_stats.csv`
- `fuel_yearly_distance_summary.csv`
- `cost_total.csv`
