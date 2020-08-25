import re
import argparse
import pdfplumber

from pathlib import Path
from datetime import datetime

from model import Transaction, AccountType

VISA_TRANSACTION_REGEX = (r"^(?P<dates>(?:\w{3} \d{2} ){2})"
                          r"(?P<description>.+)\s"
                          r"(?P<amount>-?\$[\d,]+\.\d{2})$")

def get_start_year(pdf_file_name):
    return int(re.search(r"(?<=-)\d{4}", pdf_file_name).group(0))


def get_transactions(data_directory):
    result = set()
    for pdf_path in Path(data_directory).rglob('*.pdf'):
        print(pdf_path.name)
        with pdfplumber.open(pdf_path) as pdf:
            year = get_start_year(pdf_path.name)
            last_month = None
            all_text = ""
            for page in pdf.pages:
                all_text += page.extract_text(x_tolerance=1)
            print(all_text)
            for match in re.finditer(VISA_TRANSACTION_REGEX, all_text, re.MULTILINE):
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
                result.add(Transaction(AccountType(pdf_path.parts[-2]),
                                       date,
                                       match_dict['description'],
                                       amount))
    return result


# cropped = page.crop((0.05 * float(page.width), 0, page.width, page.height)) 
