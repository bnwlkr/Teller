import os
import argparse
import sqlite3

from teller import pdf_processor
from teller import db_manager


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('database')
    arg_parser.add_argument('-d', dest='directory', required=False)
    args = arg_parser.parse_args()

    directory = 'data'

    if args.directory:
        assert os.path.exists(args.directory)
        directory = args.directory

    db_conn = sqlite3.connect(args.database)

    try:
        db_manager.create_db(db_conn)
    except sqlite3.OperationalError:  # db exists
        pass


    print(f"Searching for statements in '{directory}'...")
    found_trans = pdf_processor.get_transactions(directory) 
    print(f"Found {len(found_trans)} transactions in pdf statements") 

    existing_trans = db_manager.get_existing_trans(db_conn)
    to_add = found_trans - existing_trans

    print(f"Adding {len(to_add)} new transactions to db...")
    db_manager.add_to_db(db_conn, to_add)

    db_conn.commit()
    db_conn.close()
    


if __name__ == '__main__':
    main()

