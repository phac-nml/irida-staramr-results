import unittest

from irida_staramr_results.amr_downloader import _get_output_file_name


class AmrDownloader(unittest.TestCase):

    def setup(self):
        print("\nStarting " + self.__module__ + ": " + self._testMethodName)

    def tearDown(self):
        pass


    def test_get_output_file(self):
        """
        Test output file name generation is correct.
        :return:
        """

        fake_timestamp_in_millisec = 1611090794000
        fake_timestamp_in_second = 1611090794

        res_milli = _get_output_file_name(fake_timestamp_in_millisec)
        res_sec = _get_output_file_name(fake_timestamp_in_second)

        self.assertIn(".xlsx", res_milli)
        self.assertEqual(res_milli, "2021-01-19T21-13-14.xlsx")

        self.assertTrue(".xlsx" in res_sec)
        self.assertNotEqual(res_sec, "2021-01-19T21-13-14.xlsx")
