import unittest
from datetime import datetime
from teller.model import Transaction, AccountType
from teller import pdf_processor


class TestTeller(unittest.TestCase):
    def test_parse_visa(self):
        actual = pdf_processor.get_transactions('test_data/visa')
        self.assertIn(
            Transaction(AccountType.VISA, datetime(2017, 12, 27, 12),
                        "THRIFTY FOODS 9457QPS VICTORIA BC", 7.60),
            actual
        )

    def test_parse_chequing(self):
        actual = pdf_processor.get_transactions('test_data/chequing')
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2018, 12, 17, 12),
                        "UBC BOOKSTORE", 3.10),
            actual
        )


if __name__ == '__main__':
    unittest.main()
