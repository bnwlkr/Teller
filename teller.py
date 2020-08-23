import os
import argparse
import sqlite3
from enum import Enum

import pdf_processor

class AccountType(Enum):
    VISA = 'visa'
    CHEQUING = 'chequing'
    SAVINGS = 'savings'
    
class Transaction():
    def __init__(self, account_type, date, description, amount):
        self.account_type = account_type
        self.date = date
        self.description = description
        self.amount = amount  # CAD


def add_to_db(db_conn, transactions):
    for t in transactions:
        db_conn.execute(
            """
            INSERT INTO transactions
            (account_type, timestamp, description, amount)
            VALUES 
            (?, ?, ?, ?)
            """,
            [t.account_type.value,
             int(t.date.timestamp()),
             t.description,
             t.amount]
        )


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('database')
    args = arg_parser.parse_args()

    assert os.path.exists(args.database)

    db_conn = sqlite3.connect(args.database)

    transactions = pdf_processor.get_transactions('data/statements')

    add_to_db(db_conn, transactions)

    db_conn.commit()
    db_conn.close()
    



if __name__ == '__main__':
    main()

