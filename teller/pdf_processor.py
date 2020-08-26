import re
import argparse
import pdfplumber

from pathlib import Path
from datetime import datetime

from teller.model import Transaction, AccountType

VISA_TRANSACTION_REGEX = (r"^(?P<dates>(?:\w{3} \d{2} ){2})"
                          r"(?P<description>.+)\s"
                          r"(?P<amount>-?\$[\d,]+\.\d{2})$")

def get_start_year(pdf_file_name):
    return int(re.search(r"(?<=-)\d{4}", pdf_file_name).group(0))


def get_transactions(data_directory):
    result = set()
    for pdf_path in Path(data_directory).rglob('*.pdf'):
        print(pdf_path.name)
        year = get_start_year(pdf_path.name)
        with pdfplumber.open(pdf_path) as pdf:
            if pdf_path.parts[-2] == 'visa':
                result |= _parse_visa(pdf, year)
            elif pdf_path.parts[-2] == 'chequing':
                result |= _parse_cheq_save(pdf, year)
    return result 


def _parse_visa(pdf, year):
    result = set()
    text = ""
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


def _parse_cheq_save(pdf, year):
    result = set()
    last_date = None
    text = ""
    for page in pdf.pages:
        cropped = page.crop((0.05 * float(page.width),
                             0, page.width, page.height))
        text += cropped.extract_text(x_tolerance=1)
    lines = text.splitlines()
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.endswith("Details of your account activity"):
            start = i
        elif line.startswith("Closing Balance"):
            end = i
            break
    lines = lines[start:end]
    print(lines)
        
    return result
