from copy_finance_data import copy_finance_data
from parse_finance_data import parse_finance_data
from calculate_exchage_refs import calculate_exchange_refs
from check_parsed_files import check_parsed_files
from combine_finance_data import combine_finance_data


def main():
  
  copy_finance_data()
  parse_finance_data()
  calculate_exchange_refs()
  check_parsed_files()
  combine_finance_data()

if __name__ == "__main__":
  main()
