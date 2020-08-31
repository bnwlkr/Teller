from datetime import datetime
from .model import Transaction, AccountType

def create_db(db_conn):
    db_conn.execute(
        """
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            account_type varchar(255),
            timestamp INTEGER,
            description varchar(255),
            amount REAL
        )
        """
    )

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

def get_existing_trans(db_conn):
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
    return existing_trans
