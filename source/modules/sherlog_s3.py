'''
'''
from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogS3:
    '''
    Sherlog class to inspect S3 buckets
    '''
    def __init__(self, log, account_id):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('s3')
        self.account_id=account_id
        self.formatted_results = []
        self.resource_tags=[]
        self.associations=[]
        self.has_results=False

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            return self.formated_results, self.resource_tags, self.associations
        else:
            return None

    def start(self, session) -> None:
        '''
        Start sherlog for S3
        '''
        buckets = []
        if self.get_buckets(session):
            buckets = self.get_buckets(session)
        for bucket in buckets['Buckets']:
            result = self.get_bucket_logging_of_s3(session, bucket["Name"])["LoggingEnabled"]
            logging = self.analyze(result)
            if not logging:
                self.has_results=True
                name = bucket["Name"]
                arn = f"arn:aws:s3:::{name}"
                tags = session.client('S3').get_bucket_tagging(Bucket=result['name'])
                self.format_data(name=name)

    def get_buckets(self, session) -> dict:
        '''
        Get Buckets from AWS
        '''
        try:
            buckets = session.client('s3').list_buckets()
            return buckets
        except ClientError as client_error:
            self.log.debug('Error listing buckets: %s', client_error)
            return None

    def get_bucket_logging_of_s3(self, session, bucket_name) -> dict:
        '''
        Function to get the logging status of the given bucket
        '''
        try:
            result = session.client('s3').get_bucket_logging(Bucket=bucket_name)
            if result:
                return result
        except ClientError as excp:
            raise Exception("boto3 client error in get_bucket_logging_of_s3: " + excp) from excp
        except Exception as excp:
            self.log.error("Unexpected error in get_bucket_logging_of_s3 function: " + str(excp))
        return None

    def analyze(self, data) -> bool:
        '''
        Check if bucket is indeed logging
        '''
        if data["LoggingEnabled"]:
            return True
        return False
    
    def format_data(self, name, region, tags, arn):
        """
        Format data in json
        """
        self.formated_results.append({
            "name":name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"s3",
            "arn":arn,
            "policy":"sherlog-1-1"
        })
        self.resource_tags.append(
            {
                "arn":f"{self.account_id}/tags/{arn}",
                "tags":tags
            })
        self.associations.append(
            {
                "parentId":arn,
                "childId":f"{self.account_id}/tags/{arn}"
            }
        )
