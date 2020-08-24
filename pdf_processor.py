import re
import argparse
import pdfplumber

from pathlib import Path
from datetime import datetime

from teller import Transaction, AccountType

VISA_ACCOUNT_NUM = '451015XXXXXX8313'

VISA_TRANSACTION_REGEX = (r"^(?P<dates>(?:\w{3} \d{2} ){2})"
                          r"(?P<description>.+)\s"
                          r"(?P<amount>-?\$[\d,]+\.\d{2})$")

def get_account_type(pdf_file_name):
    if pdf_file_name.startswith(VISA_ACCOUNT_NUM):
        return AccountType.VISA

def get_start_year(pdf_file_name):
    return int(re.search(r"(?<=-)\d{4}", pdf_file_name).group(0))


def get_transactions(data_directory):
    result = []
    for pdf_path in Path(data_directory).rglob('*.pdf'):
        print(pdf_path.name)
        with pdfplumber.open(pdf_path) as pdf:
            year = get_start_year(pdf_path.name)
            last_month = None
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text(x_tolerance=1)
            for match in re.finditer(VISA_TRANSACTION_REGEX, all_text, re.MULTILINE):
                match_dict = match.groupdict()
                account_type = get_account_type(pdf_path.name)
                date = ' '.join(match_dict['dates'].split(' ')[0:2])
                month = datetime.strptime(date.split(' ')[0], '%b').month
                if last_month is not None:
                    if month < last_month:
                        year += 1
                last_month = month
                date = datetime.strptime(date + ' ' + str(year), '%b %d %Y')
                date = date.replace(hour=12)
                amount = float(match_dict['amount'].replace('$', '').replace(',', ''))
                result.append(Transaction(account_type,
                                          date,
                                          match_dict['description'],
                                          amount))
    return result
