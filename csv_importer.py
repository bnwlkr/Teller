import os
import csv
import argparse
import sqlite3
from pathlib import Path
from enum import Enum
from datetime import datetime
import transactions



def get_transactions(data_directory):
    result = []
    for csv_path in Path(data_directory).rglob('*.csv'):
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            print(csv_reader)
            for row in csv_reader:
                account_type = transactions.AccountType(row['Account Type'])
                date = datetime.strptime(row['Transaction Date'], '%d/%m/%Y')
                description = row['Description 1']  + row ['Description 2']
                amount = float(row['CAD$'])


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('database')
    args = arg_parser.parse_args()

    assert os.path.exists(args.database)

    db = sqlite3.connect(args.database)

    

    
    




if __name__ == '__main__':
    main()

