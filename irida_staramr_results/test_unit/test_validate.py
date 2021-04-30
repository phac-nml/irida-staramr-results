import unittest

from irida_staramr_results import validate


class TestValidate(unittest.TestCase):

    def setUp(self):
        print("\nStarting " + self.__module__ + ": " + self._testMethodName)

    def tearDown(self):
        pass

    def test_validate_date(self):
        """
        Test _validate_date function to return as expected
        :return:
        """

        fake_from = "2021-04-08"  # in local timezone
        fake_to = "2021-04-09"  # in local timezone

        res = validate.date_range(fake_from, fake_to)

        self.assertIn("from_date", res)
        self.assertIn("to_date", res)
        self.assertLess(res["from_date"], res["to_date"])

        self.assertEqual(res["from_date"], 1617840000000.0)

        # the actual date plus one day
        self.assertEqual(res["to_date"], 1617926400000.0 + 86400000)

        fake_from = None
        fake_to = None

        res = validate.date_range(fake_from, fake_to)
        self.assertEqual(0, res["from_date"])


if __name__ == '__main__':
    unittest.main()
