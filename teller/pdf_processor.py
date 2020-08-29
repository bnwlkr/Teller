import re
import argparse
import pdfplumber
import tabula
import pandas as pd

from pathlib import Path
from datetime import datetime, timedelta

from teller.model import Transaction, AccountType

VISA_TRANSACTION_REGEX = (r"^(?P<dates>(?:\w{3} \d{2} ){2})"
                          r"(?P<description>.+)\s"
                          r"(?P<amount>-?\$[\d,]+\.\d{2})$")

TEMPLATES_DIRECTORY = 'tabula_templates'

def get_start_year(pdf_file_name):
    return int(re.search(r"(?<=-)\d{4}", pdf_file_name).group(0))


def get_transactions(data_directory):
    result = set()
    for pdf_path in Path(data_directory).rglob('*.pdf'):
        print(pdf_path.name)
        year = get_start_year(pdf_path.name)
        if pdf_path.parts[-2] == 'visa':
            result |= _parse_visa(pdf_path, year)
        elif pdf_path.parts[-2] == 'chequing':
            transactions = _parse_cheq_save(pdf_path, year, AccountType.CHEQUING)
            _validate(pdf_path, AccountType.CHEQUING, transactions)
            result |= transactions
        elif pdf_path.parts[-2] == 'savings':
            transactions = _parse_cheq_save(pdf_path, year, AccountType.SAVINGS)
            _validate(pdf_path, AccountType.SAVINGS, transactions)
            result |= transactions 
    return result 


def _validate(pdf_path, account_type, transactions):
    opening = _get_opening_bal(pdf_path, account_type)
    closing = _get_closing_bal(pdf_path, account_type)
    net = round(sum([r.amount for r in transactions]), 2)
    if round(closing - opening, 2) != net:
        print(f"opening: {opening}, closing: {closing}, net: {net}")
        for t in transactions:
            print(t)
        raise AssertionError()


def _parse_visa(pdf_path, year):
    result = set()
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text(x_tolerance=1)
        last_month = None
        for match in re.finditer(VISA_TRANSACTION_REGEX, text, re.MULTILINE):
            match_dict = match.groupdict()
            date = ' '.join(match_dict['dates'].split(' ')[0:2])
            month = datetime.strptime(date.split(' ')[0], '%b').month
            if last_month is not None:
                if month < last_month:
                    year += 1
            last_month = month
            date = datetime.strptime(date + ' ' + str(year), '%b %d %Y')
            date = date.replace(hour=12)
            amount = float(match_dict['amount'].replace('$', '').replace(',', ''))
            result.add(Transaction(AccountType.VISA,
                                   date,
                                   match_dict['description'],
                                   amount))
    return result


def _parse_cheq_save(pdf_path, year, account_type):
    result = set()
    with pdfplumber.open(pdf_path) as pdf:
        template_path = f"{TEMPLATES_DIRECTORY}/{len(pdf.pages)}.json"
    dataframes = tabula.read_pdf_with_template(pdf_path, template_path)
    records = []
    for df in dataframes:
        records.extend(df.where(pd.notnull(df), None).to_dict('records'))
    last_date = None
    records = records[1:len(records)-1]  # skip Opening/Closing
    for record in records:
        if 'Date Description' in record:
            parts = record['Date Description'].split(' ')
            try:
                if len(parts) > 2 and 0 <= int(parts[0]) <= 31:
                    record['Date'] = ' '.join(parts[:2])
                    record['Description'] = ' '.join(parts[2:])
                else:
                    record['Date'] = None
                    record['Description'] = record['Date Description']
            except ValueError:
                record['Date'] = None
                record['Description'] = record['Date Description']

        if 'Date' not in record:
            continue
        date_str = record['Date']
        if date_str is None:
            date = last_date
        else:
            month = datetime.strptime(date_str.split(' ')[1], '%b').month
            if last_date is not None and month < last_date.month:
                year += 1
            date = datetime.strptime(f"{date_str} {year}", '%d %b %Y')
            last_date = date

        if record['Withdrawals ($)'] is not None:
            amount = -float(str(record['Withdrawals ($)']).replace(',', ''))
        elif record['Deposits ($)'] is not None:
            amount = float(str(record['Deposits ($)']).replace(',', ''))
        else: 
            continue
        description = record['Description']

        transaction = Transaction(account_type,
                                  date,
                                  description,
                                  amount)

        if transaction in result:
            transaction.date += timedelta(seconds=1)

        result.add(transaction)
    return result


def _get_opening_bal(pdf_path, account_type):
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text(x_tolerance=1)
    match = re.search(r'Your opening balance.+\$(?P<balance>[\d,]+\.\d{2})', text)
    balance = match.groupdict()['balance'].replace(',', '')
    return float(balance)


def _get_closing_bal(pdf_path, account_type):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text(x_tolerance=1)
    match = re.search(r'Your closing balance.+\$(?P<balance>[\d,]+\.\d{2})', text)
    balance = match.groupdict()['balance'].replace(',', '')
    return float(balance)
