'''
Unit tests for Redshift
'''
import json
import logging
from Sherlog.source.modules.aws.redshift import SherlogRedshift

def load_data():
    '''
    Load Mock data here
    '''
    with open('source/tests/redshift/mocks/get_logging_status.json') as json_file:
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
        redshift = SherlogRedshift(log, "12345678")
        mocker.patch("source.modules.sherlog_redshift.SherlogRedshift.__init__", return_value=None)
        value = redshift.analyze(data)
        assert value is False, "Cluster should not have logging enabled"
