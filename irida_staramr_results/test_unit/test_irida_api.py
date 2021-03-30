import unittest
from unittest.mock import patch

from irida_staramr_results.api.irida_api import IridaAPI
from irida_staramr_results.api import exceptions


class IridaApiTest(unittest.TestCase):

    def setup(self):
        print("\nStarting " + self.__module__ + ": " + self._testMethodName)

    def tearDown(self):
        pass

    @patch("irida_staramr_results.api.irida_api.IridaAPI._get_analysis_result")
    @patch("irida_staramr_results.api.irida_api.IridaAPI._is_result_type_amr")
    def test_is_submission_type_amr(self, mock_get_analysis_result, mock_is_result_type_amr):
        """
        Test _is_submission_type_amr function calls and return values
        :param mock_get_analysis_result:
        :param mock_is_result_type_amr:
        :return:
        """


        fake_data_completed = {"analysisState": "COMPLETED", "identifier": 1}
        fake_data_error = {"analysisState": "ERROR", "identifier": 1}

        # Test with COMPLETED data.
        IridaAPI._is_submission_type_amr(IridaAPI, fake_data_completed)
        self.assertTrue(mock_get_analysis_result.called)
        self.assertTrue(mock_is_result_type_amr.called)

        mock_get_analysis_result.reset_mock()
        mock_is_result_type_amr.reset_mock()

        # Test with ERROR data.
        res = IridaAPI._is_submission_type_amr(IridaAPI, fake_data_error)
        self.assertFalse(mock_get_analysis_result.called)
        self.assertFalse(res)

    def test_is_results_type_amr(self):
        """
        Test _is_results_type_amr return values
        :return:
        """
        fake_amr_type = {"analysisType": {"type": "AMR_DETECTION"}}
        fake_none_amr_type = {"analysisType": {"type": "NOT_AMR"}}

        res_true = IridaAPI._is_result_type_amr(IridaAPI, fake_amr_type)
        res_false = IridaAPI._is_result_type_amr(IridaAPI, fake_none_amr_type)

        self.assertTrue(res_true)
        self.assertFalse(res_false)

    @patch("irida_staramr_results.api.irida_api.IridaAPI._get_analysis_submissions")
    @patch("irida_staramr_results.api.irida_api.IridaAPI._is_submission_type_amr")
    def test_get_amr_analysis_submissions_return_value(self, mock_is_submission_type_amr, mock_get_analysis_submissions):
        """
        Test get_amr_analysis_submissions method to return what is expected
        :param mock_is_submission_type_amr:
        :param mock_get_analysis_submissions:
        :return:
        """
        def _is_submission_type_stub(args):
            return args

        fake_data_all_true = [True, True, True]
        fake_data_all_false = [False, False, False]
        fake_data_some_true = [False, False, True, False]

        # Test [True, True, True] to return 3 values
        mock_get_analysis_submissions.return_value = fake_data_all_true
        mock_is_submission_type_amr.side_effect = _is_submission_type_stub
        res = IridaAPI.get_amr_analysis_submissions(IridaAPI, 1)
        self.assertEqual(len(res), 3)

        # Test [False, False, False] to return 0 values
        mock_get_analysis_submissions.return_value = fake_data_all_false
        mock_is_submission_type_amr.side_effect = _is_submission_type_stub
        res = IridaAPI.get_amr_analysis_submissions(IridaAPI, 1)
        self.assertEqual(len(res), 0)

        # Test [False, False, True, False] to return 1 value
        mock_get_analysis_submissions.return_value = fake_data_some_true
        mock_is_submission_type_amr.side_effect = _is_submission_type_stub
        res = IridaAPI.get_amr_analysis_submissions(IridaAPI, 1)
        self.assertEqual(len(res), 1)

    @patch("irida_staramr_results.api.irida_api.IridaAPI._get_analysis_submissions")
    def test_get_amr_analysis_submissions_error(self, mock_get_analysis_submissions):
        """
        Test get_amr_analysis_submissions to raise an error as when expected.
        :param mock_get_analysis_submissions:
        :return:
        """

        mock_get_analysis_submissions.side_effect = KeyError

        with self.assertRaises(exceptions.IridaResourceError):
            IridaAPI.get_amr_analysis_submissions(IridaAPI, 1)


if __name__ == '__main__':
    unittest.main()
