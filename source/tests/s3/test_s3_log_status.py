'''
Unit tests for Redshift
'''
import json
import logging
from Sherlog.source.modules.aws.s3 import SherlogS3

def load_data():
    '''
    Load Mock data here
    '''
    with open('source/tests/s3/mocks/s3_logging.json') as json_file:
        data = json.load(json_file)
    return data

def test_mocking_function(mocker):
    '''
    Test analyze function
    '''
    logging.basicConfig(format="%(levelname)s: %(message)s")
    log = logging.getLogger()
    log_level = "INFO"
    log.setLevel(log_level)
    data = load_data()
    if data:
        s_s3 = SherlogS3(log, "12345678")
        mocker.patch("source.modules.sherlog_s3.SherlogS3.__init__", return_value=None)
        value = s_s3.analyze(data)
        assert value is True
