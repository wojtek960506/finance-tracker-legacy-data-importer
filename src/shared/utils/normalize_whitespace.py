import re

def normalize_whitespace(s: str) -> str:
  return re.sub(r"\s+", " ", s).strip()
