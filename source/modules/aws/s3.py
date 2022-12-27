'''
'''
from typing import Tuple
import boto3, sys
from botocore.exceptions import ClientError

class SherlogS3:
    '''
    Sherlog class to inspect S3 buckets
    '''
    def __init__(self, log, session, regions):
        # Get available regions list
        self.log = log
        self.session = session
        self.regions = regions
        self.account_id = session.client('sts').get_caller_identity().get('Account')
        self.available_regions = boto3.Session().get_available_regions('s3')
        self.formated_results = []
        self.resource_tags=[]
        self.has_results=False

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            return self.formated_results, self.resource_tags
        else:
            return None

    def analyze(self) -> None:
        '''
        Start sherlog for S3
        '''
        buckets = []
        if self.get_buckets():
            buckets = self.get_buckets()
        for bucket in buckets['Buckets']:
            result = {}
            try:
                result = self.get_bucket_logging_of_s3(bucket["Name"])["LoggingEnabled"]
                logging = True if result["LoggingEnabled"] else False
            except KeyError:
                logging = False
            except Exception as error:
                self.log.error(error)
                
            if not logging:
                self.has_results=True
                name = bucket["Name"]
                arn = f"arn:aws:s3:::{name}"
                tags = {}
                try:
                    tags = self.session.client('s3').get_bucket_tagging(Bucket=name)
                except KeyError:
                    print(result)
                    print('name not found')
                except ClientError as error:
                    if 'NoSuchTagSet' not in str(error):
                        self.log.error(error)
                except Exception as error:
                    self.log.error(error)
                self.format_data(name=name, tags=tags, arn=arn)

    def get_buckets(self) -> dict:
        '''
        Get Buckets from AWS
        '''
        try:
            buckets = self.session.client('s3').list_buckets()
            return buckets
        except ClientError as client_error:
            self.log.debug('Error listing buckets: %s', client_error)
            return None

    def get_bucket_logging_of_s3(self, bucket_name) -> dict:
        '''
        Function to get the logging status of the given bucket
        '''
        try:
            result = self.session.client('s3').get_bucket_logging(Bucket=bucket_name)
            if result:
                return result
        except ClientError as excp:
            raise Exception("boto3 client error in get_bucket_logging_of_s3: " + excp) from excp
        except Exception as excp:
            self.log.error("Unexpected error in get_bucket_logging_of_s3 function: " + str(excp))
        return None

    def format_data(self, name, tags, arn):
        """
        Format data in json
        """
        self.formated_results.append({
            "name":name,
            "rational":"Public Policy",
            "service":"s3",
            "arn":arn,
            "policy":"sherlog-1-1"
        })
        self.resource_tags.append(
            {
                "arn":f"{self.account_id}/tags/{arn}",
                "tags":tags
            }
        )
