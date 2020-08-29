import os
import argparse
import sqlite3
from datetime import datetime

from teller.model import Transaction, AccountType
import teller.pdf_processor


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
    arg_parser.add_argument('-d', dest='directory', required=False)
    args = arg_parser.parse_args()

    assert os.path.exists(args.database)

    directory = 'data/statements'

    if args.directory:
        assert os.path.exists(args.directory)
        directory = args.directory
    

    db_conn = sqlite3.connect(args.database)

    existing_rows = db_conn.execute(
        """
        SELECT account_type,
               timestamp,
               description,
               amount
        FROM transactions
        """
    ).fetchall()

    existing_trans = {Transaction(AccountType(e[0]), 
                                  datetime.fromtimestamp(e[1]),
                                  e[2],
                                  e[3])
                      for e in existing_rows}

    all_trans = teller.pdf_processor.get_transactions(directory)

    to_add = all_trans - existing_trans
    
    add_to_db(db_conn, to_add)

    db_conn.commit()
    db_conn.close()
    



if __name__ == '__main__':
    main()

