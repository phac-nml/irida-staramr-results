import unittest
from unittest.mock import patch


from irida_staramr_results.api.irida_api import IridaAPI
from irida_staramr_results.api import exceptions


class IridaApiTest(unittest.TestCase):

    def setup(self):
        print("Set up Test")
        self.fake_project_id = 1
        self.fake_analysis_submission_list = [
            {
                "name": "Sample1",
                "workflowId": "0001",
                "inputParameters": {
                    "input1": "0",
                },
                "createdDate": "0",
                "modifiedDate": "0",
                "updateSamples": "0",
                "analysisDescription": "",
                "emailPipelineResultCompleted": "false",
                "emailPipelineResultError": "false",
                "remoteInputDataId": "0001",
                "remoteWorkflowId": "0001",
                "analysisState": "COMPLETED",
                "analysisCleanedState": "NOT_CLEANED",
                "priority": "MEDIUM",
                "automated": "false",
                "label": "Sample1",
                "links": [
                    {
                        "rel": "input/unpaired",
                        "href": "http://localhost:8080/api/analysisSubmissions/1/sequenceFiles/unpaired"
                    },
                    {
                        "rel": "input/paired",
                        "href": "http://localhost:8080/api/analysisSubmissions/1/sequenceFiles/pairs"
                    },
                    {
                        "rel": "analysis",
                        "href": "http://localhost:8080/api/analysisSubmissions/1/analysis"
                    },
                    {
                        "rel": "self",
                        "href": "http://localhost:8080/api/analysisSubmissions/2"
                    }
                ],
                "identifier": "1"
            },
            {
                "name": "Sample2",
                "workflowId": "0002",
                "inputParameters": {
                    "input1": "0",
                },
                "createdDate": "0",
                "modifiedDate": "0",
                "updateSamples": "0",
                "analysisDescription": "",
                "emailPipelineResultCompleted": "false",
                "emailPipelineResultError": "false",
                "remoteInputDataId": "0002",
                "remoteWorkflowId": "0002",
                "analysisState": "ERROR",
                "analysisCleanedState": "NOT_CLEANED",
                "priority": "MEDIUM",
                "automated": "false",
                "label": "Sample2",
                "links": [
                    {
                        "rel": "input/unpaired",
                        "href": "http://localhost:8080/api/analysisSubmissions/2/sequenceFiles/unpaired"
                    },
                    {
                        "rel": "input/paired",
                        "href": "http://localhost:8080/api/analysisSubmissions/2/sequenceFiles/pairs"
                    },
                    {
                        "rel": "self",
                        "href": "http://localhost:8080/api/analysisSubmissions/2"
                    }
                ],
                "identifier": "2"
            }
        ]

    def tearDown(self):
        pass

    @patch('irida_staramr_results.api.irida_api.IridaAPI._get_analysis_submissions')
    def test_get_amr_analysis_submissions_error(self, mock_analysis_submissions_func):
        """
        Test get_amr_analysis_submissions to raise an error as when expected.
        :param mock_analysis_submissions:
        :param mock_type:
        :return:
        """

        self.setup()

        # Test project id not found (IridaResourceError)
        mock_analysis_submissions_func.side_effect = exceptions.IridaResourceError("project not found")
        with self.assertRaises(exceptions.IridaResourceError):
            IridaAPI.get_amr_analysis_submissions(IridaAPI, project_id=self.fake_project_id)

        # Test when receiving an None type.
        mock_analysis_submissions_func.side_effect = None
        with self.assertRaises(exceptions.IridaResourceError):
            IridaAPI.get_amr_analysis_submissions(IridaAPI, project_id=self.fake_project_id)

    @patch('irida_staramr_results.api.irida_api.IridaAPI._is_submission_type_amr')
    @patch('irida_staramr_results.api.irida_api.IridaAPI._get_analysis_submissions')
    def test_get_amr_analysis_submission_calls(self, mock_submission_type, mock_analysis_submissions_func):
        """
        Test the the function is_submission_type_amr is called
        :param mock_submission_type:
        :param mock_analysis_submissions_func:
        :return:
        """

        self.setup()

        # Empty analysis submissions list
        mock_analysis_submissions_func.return_value = []
        IridaAPI.get_amr_analysis_submissions(IridaAPI, self.fake_project_id)
        mock_submission_type.assert_called()

        # Non-empty analysis submissions list
        mock_analysis_submissions_func.return_value = self.fake_analysis_submission_list

    @patch('irida_staramr_results.api.irida_api.IridaAPI._get_analysis_submissions')
    @patch('irida_staramr_results.api.irida_api.IridaAPI._is_submission_type_amr')
    def test_get_amr_analysis_submission_return_value(self, mock_submission_type, mock_analysis_submissions_func):
        """
        Test return values of get_amr_analysis_submission.
        :param mock_submission_type:
        :param mock_analysis_submissions_func:
        :return:
        """

        self.setup()

        fake_none_completed_submission_list = [
            {
                "name": "Sample1",
                "analysisState": "ERROR",
                "label": "Sample1",
                "links": [],
                "identifier": "1"
            },
            {
                "name": "Sample2",
                "analysisState": "ERROR",
                "label": "Sample2",
                "links": [],
                "identifier": "2"
            }
        ]
        fake_all_completed_submission_list = [
            {
                "name": "Sample1",
                "analysisState": "COMPLETED",
                "label": "Sample1",
                "links": [
                    {
                        "rel": "analysis",
                        "href": "http://localhost:8080/api/analysisSubmissions/1/analysis"
                    },
                ],
                "identifier": "1"
            },
            {
                "name": "Sample2",
                "analysisState": "COMPLETED",
                "label": "Sample2",
                "links": [
                    {
                        "rel": "analysis",
                        "href": "http://localhost:8080/api/analysisSubmissions/2/analysis"
                    },
                ],
                "identifier": "2"
            },
            {
                "name": "Sample3",
                "analysisState": "COMPLETED",
                "label": "Sample3",
                "links": [
                    {
                        "rel": "analysis",
                        "href": "http://localhost:8080/api/analysisSubmissions/3/analysis"
                    },
                ],
                "identifier": "3"
            }
        ]
        fake_one_complete_submission_list = [
            {
                "name": "Sample1",
                "analysisState": "ERROR",
                "label": "Sample1",
                "links": [],
                "identifier": "1"
            },
            {
                "name": "Sample2",
                "analysisState": "COMPLETED",
                "label": "Sample2",
                "links": [
                    {
                        "rel": "analysis",
                        "href": "http://localhost:8080/api/analysisSubmissions/2/analysis"
                    },
                ],
                "identifier": "2"
            },
            {
                "name": "Sample3",
                "analysisState": "ERROR",
                "label": "Sample3",
                "links": [],
                "identifier": "3"
            }
        ]
        fake_empty_submission_list = {}

        # No completed amr submissions must return empty list
        mock_analysis_submissions_func.return_value = fake_none_completed_submission_list
        return_submission_list = IridaAPI.get_amr_analysis_submissions(IridaAPI, self.fake_project_id)
        mock_submission_type.assert_called()
        self.assertTrue(len(return_submission_list) is 0)

        # All completed amr submissions must return all
        mock_analysis_submissions_func.return_value = fake_all_completed_submission_list
        return_submission_list = IridaAPI.get_amr_analysis_submissions(IridaAPI, self.fake_project_id)
        mock_submission_type.assert_called()
        self.assertTrue(len(return_submission_list) is len(fake_all_completed_submission_list))

        # One completed amr submissions must not return all and only one
        mock_analysis_submissions_func.return_value = fake_one_complete_submission_list
        return_submission_list = IridaAPI.get_amr_analysis_submissions(IridaAPI, self.fake_project_id)
        mock_submission_type.assert_called()
        self.assertTrue(len(return_submission_list) is 1)

        # Empty dictionary must return an empty list
        mock_analysis_submissions_func.return_value = fake_empty_submission_list
        return_submission_list = IridaAPI.get_amr_analysis_submissions(IridaAPI, self.fake_project_id)
        mock_submission_type.assert_called()
        self.assertTrue(len(return_submission_list) is 0)


if __name__ == '__main__':
    unittest.main()
