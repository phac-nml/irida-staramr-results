import unittest

from irida_staramr_results import cli


class TestCli(unittest.TestCase):

    def test_validate_date(self):
        """
        Test _validate_date function to return as expected
        :return:
        """

        fake_from = "2021-04-08"  # in local timezone
        fake_to = "2021-04-09"  # in local timezone

        res = cli._validate_date(fake_from, fake_to)

        self.assertIn("from_date", res)
        self.assertIn("to_date", res)
        self.assertLess(res["from_date"], res["to_date"])

        self.assertEqual(res["from_date"], 1617840000000.0)

        # the actual date plus one day
        self.assertEqual(res["to_date"], 1617926400000.0 + 86400000)

        fake_from = None
        fake_to = None

        res = cli._validate_date(fake_from, fake_to)
        self.assertEqual(0, res["from_date"])

    def test_local_to_timestamp(self):
        """
        Test local to timestamp conversion.
        :return:
        """
        fake_good_date = "2021-04-08"  # CDT
        res = cli._local_to_timestamp(fake_good_date)
        self.assertEqual(res, 1617840000000.0)

        fake_bad_date = "2021/04/08"
        with self.assertRaises(ValueError) as c:
            cli._local_to_timestamp(fake_bad_date)
            self.assertTrue("does not match format '%Y-%m-%d'" in c.exception)


if __name__ == '__main__':
    unittest.main()
