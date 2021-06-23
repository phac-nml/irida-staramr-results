import io
import unittest
import pandas as pd

from irida_staramr_results.downloader import _get_output_file_name, _convert_to_df



class TestDownloader(unittest.TestCase):

    def setUp(self):
        print("\nStarting " + self.__module__ + ": " + self._testMethodName)

    def tearDown(self):
        pass

    def test_get_output_file_name(self):
        """
        Test output file name generation is correct.
        :return:
        """

        fake_prefix_name = "out"
        fake_timestamp_in_millisec = 1611090794000

        res_milli = _get_output_file_name(fake_prefix_name, fake_timestamp_in_millisec)

        self.assertNotIn(".xlsx", res_milli)
        self.assertEqual(res_milli, "out-2021-01-19T21-13-14")

    def test_convert_to_df(self):
        """
        Test converting file content to dataframe function
        :return:
        """

        fake_content_in_dict = {"a": "1", "b": "2", "c": "3"}
        # fake_content_in_tsv = "h1\th2\th3\t\na\tb\tc"

        res_dict = _convert_to_df(fake_content_in_dict)
        # res_tsv = _convert_to_df(fake_content_in_tsv)

        expected_res_dict = pd.DataFrame({"a": ["1"], "b": ["2"], "c": ["3"]})
        # expected_res_tsv = pd.read_csv(io.StringIO(fake_content_in_tsv), delimiter="\t")

        self.assertTrue(expected_res_dict.equals(res_dict))
        # print(expected_res_dict)



if __name__ == '__main__':
    unittest.main()
