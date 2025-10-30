from copy_finance_data import copy_finance_data
from parse_finance_data import parse_finance_data
from calculate_exchage_refs import calculate_exchange_refs
from check_parsed_files import check_parsed_files
from combine_finance_data import combine_finance_data
import click


@click.command()
@click.option("--should-copy", is_flag=True, help="Whether to update copies of the raw CSV files")
@click.option("--should-print", is_flag=True, help="Whehter to print additional info")
def main(should_copy, should_print):
  
  print('Start preparing files')

  if should_copy:
    copy_finance_data(should_print)
  parse_finance_data(should_print)
  calculate_exchange_refs(should_print)
  check_parsed_files(should_print)
  combine_finance_data(should_print)

  print('Files ready')

if __name__ == "__main__":
  main()
