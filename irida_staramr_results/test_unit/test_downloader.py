import unittest
import time

from irida_staramr_results.downloader import _get_output_file_name, _filter_by_date


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

        fake_prefix_name = "out"
        fake_timestamp_in_millisec = 1611090794000

        res_milli = _get_output_file_name(fake_prefix_name, fake_timestamp_in_millisec)

        self.assertNotIn(".xlsx", res_milli)
        self.assertEqual(res_milli, "out-2021-01-19T21-13-14")

    def test_filter_by_date(self):
        """
        Tests function that filters analysis by date range
        :return:
        """
        fake_list = [
            {"createdDate": 1611122400000},  # Jan 20 2021
            {"createdDate": 1613282400000},  # Feb 14 2021
            {"createdDate": 1614405600000},  # Feb 27 2021
            {"createdDate": 1614924000000},  # Mar 05 2021
            {"createdDate": 1617858000000}  # Apr 08 2021
        ]

        # timestamps default values if user did not input any date (from and to)
        fake_from_date_no_input = 0  # epoch
        fake_to_date_no_input = time.time() * 1000  # now

        fake_from_date = 1614319200000  # Feb 26 2021
        fake_to_date = 1617771600000  # Apr 07 2021

        res_no_input = _filter_by_date(fake_list, fake_from_date_no_input, fake_to_date_no_input)
        res_input = _filter_by_date(fake_list, fake_from_date, fake_to_date)

        self.assertEqual(len(res_no_input), 5)
        self.assertEqual(len(res_input), 2)
