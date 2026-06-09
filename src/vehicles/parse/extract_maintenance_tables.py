import argparse
import csv
from pathlib import Path


MAINTENANCE_HEADERS = [
  "source_row",
  "date",
  "cost_pln",
  "odometer_km",
  "description",
  "service_provider",
]

SECTION_FILE_NAMES = {
  "own_maintenance": "own_maintenance.csv",
  "previous_owner_services": "previous_owner_services.csv",
  "driving_licence_costs": "driving_licence_costs.csv",
}


def read_rows(csv_path: Path) -> list[list[str]]:
  with csv_path.open(encoding="utf-8", newline="") as csv_file:
    return list(csv.reader(csv_file))


def clean_text(value: str | None) -> str:
  return (value or "").replace("\xa0", " ").strip()


def get_cell(row: list[str], index: int) -> str:
  if index < len(row):
    return row[index]
  return ""


def is_data_row(row: list[str]) -> bool:
  year = clean_text(get_cell(row, 0))
  month = clean_text(get_cell(row, 1))
  day = clean_text(get_cell(row, 2))
  return year.isdigit() and month.isdigit() and day.isdigit()


def build_date(row: list[str]) -> str:
  year = int(clean_text(get_cell(row, 0)))
  month = int(clean_text(get_cell(row, 1)))
  day = int(clean_text(get_cell(row, 2)))
  return f"{year:04d}-{month:02d}-{day:02d}"


def parse_cost(value: str | None) -> float:
  cleaned = clean_text(value)
  if not cleaned or cleaned in {"-", "?"}:
    return 0.0
  return float(cleaned.replace(" ", "").replace(",", "."))


def parse_odometer(value: str | None) -> int | None:
  cleaned = clean_text(value)
  if not cleaned or cleaned in {"-", "?"}:
    return None
  return int(cleaned.replace(" ", ""))


def classify_section(label: str) -> str | None:
  lowered = clean_text(label).lower()
  if not lowered:
    return None
  if "moja eksploatacja" in lowered:
    return "own_maintenance"
  if "naprawy wykonywane przez" in lowered:
    return "previous_owner_services"
  if "prawo jazdy" in lowered:
    return "driving_licence_costs"
  return None


def extract_maintenance_sections(rows: list[list[str]]) -> dict[str, list[dict]]:
  sections: dict[str, list[dict]] = {key: [] for key in SECTION_FILE_NAMES}
  current_section: str | None = None

  for row_index, row in enumerate(rows, start=1):
    section_name = classify_section(get_cell(row, 0))
    if section_name:
      current_section = section_name
      continue

    if not is_data_row(row) or current_section is None:
      continue

    sections[current_section].append({
      "source_row": row_index,
      "date": build_date(row),
      "cost_pln": parse_cost(get_cell(row, 3)),
      "odometer_km": parse_odometer(get_cell(row, 4)),
      "description": clean_text(get_cell(row, 5)) or None,
      "service_provider": clean_text(get_cell(row, 6)) or None,
    })

  return sections


def write_csv(path: Path, headers: list[str], rows: list[dict]) -> None:
  with path.open("w", encoding="utf-8", newline="") as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)


def run(csv_path: Path, output_dir: Path) -> None:
  output_dir.mkdir(parents=True, exist_ok=True)
  rows = read_rows(csv_path)
  sections = extract_maintenance_sections(rows)

  for section_name, file_name in SECTION_FILE_NAMES.items():
    section_rows = sections[section_name]
    if not section_rows:
      continue
    write_csv(output_dir / file_name, MAINTENANCE_HEADERS, section_rows)


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Extract section-based maintenance tables from vehicle spreadsheet CSV exports.",
  )
  parser.add_argument("csv_path", help="Path to the mixed maintenance CSV export")
  parser.add_argument(
    "--output-dir",
    help="Directory where the extracted CSV files will be written",
  )
  args = parser.parse_args()

  csv_path = Path(args.csv_path)
  output_dir = Path(args.output_dir) if args.output_dir else csv_path.parent / "maintenance_tables"
  run(csv_path, output_dir)


if __name__ == "__main__":
  main()
