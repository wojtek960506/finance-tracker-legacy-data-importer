import argparse
import csv
from pathlib import Path


MAIN_TABLE_HEADERS = [
  "source_row",
  "date",
  "fuel_liters",
  "fuel_liters_to_full",
  "unit_price_pln",
  "is_full_tank",
  "cost_pln",
  "cost_to_full_pln",
  "odometer_km",
  "distance_since_previous_km",
  "distance_since_previous_full_km",
  "consumption_l_per_100km",
  "cost_per_km_pln",
  "km_per_liter",
  "station_brand",
  "station_address",
  "description",
]

STATS_TABLE_HEADERS = [
  "source_row",
  "scope",
  "year",
  "start_odometer_km",
  "end_odometer_km",
  "total_distance_km",
  "total_fuel_liters",
  "avg_consumption_l_per_100km",
  "total_fuel_cost_pln",
  "avg_fuel_price_pln",
  "avg_cost_per_km_pln",
  "avg_km_per_liter",
  "refuel_count",
  "avg_refuel_liters",
]

YEARLY_DISTANCE_HEADERS = [
  "source_row",
  "year",
  "start_odometer_km",
  "end_odometer_km",
  "total_distance_km",
  "description",
]

CROSS_SHEET_HEADERS = [
  "source_row",
  "metric_name",
  "metric_value_pln",
]


def read_rows(csv_path: Path) -> list[list[str]]:
  with csv_path.open(encoding="utf-8", newline="") as csv_file:
    return list(csv.reader(csv_file))


def clean_text(value: str | None) -> str:
  return (value or "").replace("\xa0", " ").strip()


def is_data_row(row: list[str]) -> bool:
  return len(row) >= 3 and clean_text(row[0]).isdigit() and len(clean_text(row[0])) == 4


def parse_float(value: str | None) -> float | None:
  cleaned = clean_text(value)
  if not cleaned:
    return None
  return float(cleaned.replace(" ", "").replace(",", "."))


def parse_int(value: str | None) -> int | None:
  cleaned = clean_text(value)
  if not cleaned:
    return None
  return int(cleaned.replace(" ", ""))


def parse_bool(value: str | None) -> bool | None:
  cleaned = clean_text(value).upper()
  if not cleaned:
    return None
  if cleaned == "TAK":
    return True
  if cleaned == "NIE":
    return False
  raise ValueError(f"Unsupported boolean value: {value!r}")


def build_date(row: list[str]) -> str:
  year = int(clean_text(row[0]))
  month = int(clean_text(row[1]))
  day = int(clean_text(row[2]))
  return f"{year:04d}-{month:02d}-{day:02d}"


def join_description_parts(parts: list[str]) -> str | None:
  normalized = [clean_text(part) for part in parts if clean_text(part)]
  if not normalized:
    return None
  return "\n".join(normalized)


def get_cell(row: list[str], index: int) -> str:
  if index < len(row):
    return row[index]
  return ""


def extract_main_table(rows: list[list[str]]) -> list[dict]:
  extracted_rows: list[dict] = []

  for row_index, row in enumerate(rows, start=1):
    if not is_data_row(row):
      continue

    description_parts = [get_cell(row, 17)]

    continuation_index = row_index
    while continuation_index < len(rows):
      next_row = rows[continuation_index]
      if is_data_row(next_row):
        break

      next_description = join_description_parts(
        [get_cell(next_row, 17), get_cell(next_row, 18), get_cell(next_row, 19)]
      )
      if next_description:
        description_parts.append(next_description)
      continuation_index += 1

    extracted_rows.append({
      "source_row": row_index,
      "date": build_date(row),
      "fuel_liters": parse_float(get_cell(row, 3)),
      "fuel_liters_to_full": parse_float(get_cell(row, 4)),
      "unit_price_pln": parse_float(get_cell(row, 5)),
      "is_full_tank": parse_bool(get_cell(row, 6)),
      "cost_pln": parse_float(get_cell(row, 7)),
      "cost_to_full_pln": parse_float(get_cell(row, 8)),
      "odometer_km": parse_int(get_cell(row, 9)),
      "distance_since_previous_km": parse_int(get_cell(row, 10)),
      "distance_since_previous_full_km": parse_int(get_cell(row, 11)),
      "consumption_l_per_100km": parse_float(get_cell(row, 12)),
      "cost_per_km_pln": parse_float(get_cell(row, 13)),
      "km_per_liter": parse_float(get_cell(row, 14)),
      "station_brand": clean_text(get_cell(row, 15)) or None,
      "station_address": clean_text(get_cell(row, 16)) or None,
      "description": join_description_parts(description_parts),
    })

  return extracted_rows


def build_stats_row(scope: str, year: int | None, source_row: int, row: list[str]) -> dict:
  return {
    "source_row": source_row,
    "scope": scope,
    "year": year,
    "start_odometer_km": parse_int(get_cell(row, 20)),
    "end_odometer_km": parse_int(get_cell(row, 21)),
    "total_distance_km": parse_int(get_cell(row, 22)),
    "total_fuel_liters": parse_float(get_cell(row, 23)),
    "avg_consumption_l_per_100km": parse_float(get_cell(row, 24)),
    "total_fuel_cost_pln": parse_float(get_cell(row, 25)),
    "avg_fuel_price_pln": parse_float(get_cell(row, 26)),
    "avg_cost_per_km_pln": parse_float(get_cell(row, 27)),
    "avg_km_per_liter": parse_float(get_cell(row, 28)),
    "refuel_count": parse_int(get_cell(row, 29)),
    "avg_refuel_liters": parse_float(get_cell(row, 30)),
  }


def extract_stats_table(rows: list[list[str]]) -> list[dict]:
  extracted_rows: list[dict] = []
  overall_label_row = 4
  overall_values_row = 5

  if clean_text(get_cell(rows[overall_label_row - 1], 20)).upper() == "CAŁKOWITE":
    extracted_rows.append(
      build_stats_row("overall", None, overall_values_row, rows[overall_values_row - 1])
    )

  for label_row in range(6, 17, 2):
    value_row = label_row + 1
    year_text = clean_text(get_cell(rows[label_row - 1], 20))
    if not year_text:
      continue

    extracted_rows.append(
      build_stats_row("year", int(year_text), value_row, rows[value_row - 1])
    )

  return extracted_rows


def extract_yearly_distance_summary(rows: list[list[str]]) -> list[dict]:
  extracted_rows: list[dict] = []

  for row_index in range(24, 29):
    row = rows[row_index - 1]
    extracted_rows.append({
      "source_row": row_index,
      "year": parse_int(get_cell(row, 20)),
      "start_odometer_km": parse_int(get_cell(row, 21)),
      "end_odometer_km": parse_int(get_cell(row, 22)),
      "total_distance_km": parse_int(get_cell(row, 23)),
      "description": clean_text(get_cell(row, 24)) or None,
    })

  return extracted_rows


def extract_cross_sheet_totals(rows: list[list[str]]) -> list[dict]:
  extracted_rows: list[dict] = []

  for row_index in range(6, 11):
    row = rows[row_index - 1]
    metric_name = clean_text(get_cell(row, 34))
    if not metric_name:
      continue

    extracted_rows.append({
      "source_row": row_index,
      "metric_name": metric_name,
      "metric_value_pln": parse_float(get_cell(row, 35)),
    })

  return extracted_rows


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
  with path.open("w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Extract the four embedded tables from a fuel spreadsheet CSV export.",
  )
  parser.add_argument("csv_path", help="Path to the mixed fuel CSV export")
  parser.add_argument(
    "--output-dir",
    default="data/vehicles/parse/car_2005/fuel_tables",
    help="Directory where the extracted CSV files will be written",
  )
  args = parser.parse_args()

  csv_path = Path(args.csv_path)
  output_dir = Path(args.output_dir)
  output_dir.mkdir(parents=True, exist_ok=True)

  rows = read_rows(csv_path)

  write_csv(output_dir / "fuel_entries.csv", MAIN_TABLE_HEADERS, extract_main_table(rows))
  write_csv(output_dir / "fuel_stats.csv", STATS_TABLE_HEADERS, extract_stats_table(rows))
  write_csv(
    output_dir / "fuel_yearly_distance_summary.csv",
    YEARLY_DISTANCE_HEADERS,
    extract_yearly_distance_summary(rows),
  )
  write_csv(
    output_dir / "car_cost_totals.csv",
    CROSS_SHEET_HEADERS,
    extract_cross_sheet_totals(rows),
  )


if __name__ == "__main__":
  main()
