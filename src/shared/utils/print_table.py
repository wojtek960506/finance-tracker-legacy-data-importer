def stringify_cell(value) -> str:
  if value is None:
    return ""
  return str(value)


def get_table_columns(rows: list[dict]) -> list[str]:
  columns: list[str] = []

  for row in rows:
    for column in row.keys():
      if column not in columns:
        columns.append(column)

  return columns


def print_table(rows: list[dict], columns: list[str] | None = None) -> None:
  if len(rows) == 0:
    print("No rows found.")
    return

  resolved_columns = columns or get_table_columns(rows)
  widths = {
    column: max(
      len(column),
      *[len(stringify_cell(row.get(column))) for row in rows],
    )
    for column in resolved_columns
  }

  header = "| " + " | ".join(
    column.ljust(widths[column]) for column in resolved_columns
  ) + " |"
  separator = "+-" + "-+-".join(
    "-" * widths[column] for column in resolved_columns
  ) + "-+"

  print(header)
  print(separator)

  for row in rows:
    print(
      "| " + " | ".join(
        stringify_cell(row.get(column)).ljust(widths[column])
        for column in resolved_columns
      ) + " |"
    )
