import unittest

from irida_staramr_results import cli


class TestCli(unittest.TestCase):

    def test_validate_date(self):

        fake_from = "2021-04-08"  # in local timezone
        fake_to = "2021-04-09"  # in local timezone

        res = cli._validate_date(fake_from, fake_to)

        self.assertIn("fromDate", res)
        self.assertIn("toDate", res)
        self.assertLess(res["fromDate"], res["toDate"])

        self.assertEqual(res["fromDate"], 1617840000000.0)
        self.assertEqual(res["toDate"], 1617926400000.0)

        fake_from = None
        fake_to = None

        res = cli._validate_date(fake_from, fake_to)
        self.assertEqual(0, res["fromDate"])

    def test_local_to_timestamp(self):
        """
        Test local to timestamp conversion.
        :return:
        """
        fake_good_date = "2021-04-08"  # CDT
        res = cli.local_to_timestamp(fake_good_date)
        self.assertEqual(res, 1617840000000.0)

        fake_bad_date = "2021/04/08"
        with self.assertRaises(ValueError) as c:
            cli.local_to_timestamp(fake_bad_date)
            self.assertTrue("does not match format '%Y-%m-%d'" in c.exception)












if __name__ == '__main__':
    unittest.main()
