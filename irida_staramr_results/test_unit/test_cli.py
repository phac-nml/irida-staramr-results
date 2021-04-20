import unittest

from irida_staramr_results import cli


class TestCli(unittest.TestCase):

    def test_validate_date(self):

        fake_from = "2021-04-08"  # UTC
        fake_to = "2021-04-09"  # UTC

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

    def test_utc_to_timestamp(self):
        """
        Test utc to timestamp conversion.
        :return:
        """
        fake_good_date = "2021-04-08"
        res = cli.utc_to_timestamp(fake_good_date)
        self.assertEqual(res, 1617840000000.0)

        fake_bad_date = "2021/04/08"
        with self.assertRaises(ValueError) as c:
            cli.utc_to_timestamp(fake_bad_date)
            self.assertTrue("does not match format '%Y-%m-%d'" in c.exception)

    def test_output_name_validation(self):

        fake_filename_1 = "out"  # --> out.xlsx
        fake_filename_2 = "out.xlsx"  # --> out.xlsx
        fake_filename_2 = ""  # --> out.xlsx
        fake_filename_3 = "xouts.xlsx"  # --> xouts.xlsx
        fake_filename_4 = "out.xlsx.out"  # --> out.xlsx.out.xslx
        fake_filename_5 = "out.xlxs"  # --> out.xslx.xlsx











if __name__ == '__main__':
    unittest.main()
