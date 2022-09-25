import boto3

class AwsSession:
    '''
    Class responsible to assure a trustable AWS session
    '''
    def __init__(self, log, role_arn=None, external_id=None, session_name='sherlog_session'):
        self.session = None
        self.role_arn = role_arn
        self.external_id = external_id
        self.session_name = session_name
        self.log = log

    def get_session(self):
        '''
        Get IAM Role to perform the actions
        '''
        self.log.info(f'[aws_session] Start')

        if self.role_arn and len(self.external_id) > 1:
            client = boto3.client('sts')
            response = client.assume_role(RoleArn=self.role_arn, ExternalId=self.external_id, RoleSessionName=self.session_name)
            session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken'])
            self.log.info(f'[awsSession] Successfully assumed the role {self.role_arn}')
            return session
        elif self.role_arn:
            client = boto3.client('sts')
            response = client.assume_role(RoleArn=self.role_arn, RoleSessionName=self.session_name)
            self.log.info("Assumed role: %s", response)
            session = boto3.Session(
                aws_access_key_id=response['Credentials']['AccessKeyId'],
                aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                aws_session_token=response['Credentials']['SessionToken'])
            self.log.info(f'[awsSession] Successfully assumed the role {self.role_arn}')
            return session
        else:
            self.log.info(f'[aws_session] No new role was detected. Continue with Service IAM role')
            return boto3.Session()