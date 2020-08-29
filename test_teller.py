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
                        "UBC BOOKSTORE", -3.10),
            actual
        )
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2018, 11, 26, 12),
                        "YELLOW CAB #205", -17.30),
            actual
        )
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2019, 3, 19, 12),
                        "DOORDASH*TIMKEE", -19.24),
            actual
        )
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2019, 1, 25, 12),
                        "e-Transfer received TOMAS KANTOR", 1238),
            actual
        )
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2019, 1, 4, 12),
                        "INS MARKET # 91", -3.19),
            actual
        )
        self.assertIn(
            Transaction(AccountType.CHEQUING, datetime(2018, 12, 28, 12),
                        "Interac purchase - 7556 ACT DISTWESTVAN", -6.50),
            actual
        )

    def test_parse_savings(self):
        actual = pdf_processor.get_transactions('test_data/savings')
        self.assertIn(
            Transaction(AccountType.SAVINGS, datetime(2016, 9, 20, 12),
                        "Interac purchase - 5347 SHOPPERS DRUG M", -38.51),
            actual
        )
        self.assertIn(
            Transaction(AccountType.SAVINGS, datetime(2018, 7, 19, 12),
                        "ATM deposit - VE258559", 200),
            actual
        )
        self.assertIn(
            Transaction(AccountType.SAVINGS, datetime(2018, 1, 11, 12),
                        "UBC", -1000),
            actual
        )

    def test_get_opening_bal(self):
        test_path = 'test_data/chequing/08480XXX6520-2018Dec24-2019Jan25.pdf'
        self.assertEqual(2062, pdf_processor._get_opening_bal(test_path))
        test_path = 'test_data/savings/08400XXX4349-2019Jul25-2019Aug23.pdf'
        self.assertEqual(0, pdf_processor._get_opening_bal(test_path))

    def test_get_closing_bal(self):
        test_path = 'test_data/chequing/08480XXX6520-2018Dec24-2019Jan25.pdf'
        self.assertEqual(6576.66, pdf_processor._get_closing_bal(test_path))
        test_path = 'test_data/savings/08400XXX4349-2019Jul25-2019Aug23.pdf'
        self.assertEqual(0, pdf_processor._get_closing_bal(test_path))


if __name__ == '__main__':
    unittest.main()
