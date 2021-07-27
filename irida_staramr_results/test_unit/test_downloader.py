import unittest

from irida_staramr_results.downloader import _get_output_file_name


class TestDownloader(unittest.TestCase):

    def setUp(self):
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


if __name__ == '__main__':
    unittest.main()
