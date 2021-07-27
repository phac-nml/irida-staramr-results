import unittest

from irida_staramr_results import util


class TestUtil(unittest.TestCase):

    def setUp(self):
        print("\nStarting " + self.__module__ + ": " + self._testMethodName)

    def tearDown(self):
        pass

    def test_local_to_timestamp(self):
        """
        Test local to timestamp conversion.
        :return:
        """

        fake_good_date = "2021-04-08"  # CDT
        res = util.local_to_timestamp(fake_good_date)
        self.assertEqual(res, 1617840000000.0)

        fake_bad_date = "2021/04/08"
        with self.assertRaises(ValueError) as c:
            util.local_to_timestamp(fake_bad_date)
            self.assertTrue("does not match format '%Y-%m-%d'" in c.exception)


if __name__ == '__main__':
    unittest.main()
