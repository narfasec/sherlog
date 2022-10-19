import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogS3:
    '''
    Sherlog class to inspect S3 buckets
    '''
    def __init__(self, log, session):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('s3')
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.client=session.client('s3')

    def analyze(self):
        '''
        Function that will read the logging status of the buckets
        '''
        s3_logs_disabled = []
        buckets = self.client.list_buckets()
        for bucket in buckets['Buckets']:
            try:
                result = self.get_bucket_logging_of_s3(bucket["Name"])["LoggingEnabled"]
                print(result)
            except KeyError:
                s3_logs_disabled.append(bucket["Name"])
        if s3_logs_disabled:
            return self.format_data(results=s3_logs_disabled)
        else:
            self.log.info('S3 buckets with logs disabled not found')
            return None

    def get_bucket_logging_of_s3(self, bucket_name):
        '''
        Function to get the logging status of the given bucket
        '''
        try:
            result = self.client.get_bucket_logging(Bucket=bucket_name)
        except ClientError as excp:
            raise Exception("boto3 client error in get_bucket_logging_of_s3: " + excp) from excp
        except Exception as excp:
            self.log.error("Unexpected error in get_bucket_logging_of_s3 function: " + str(excp))
        return result
    
    def format_data(self, results):
        """
        Format data to insert on DB
        """
        formated_results = []
        resource_tags = []
        associations = []
        for result in results:
            formated_results.append({
                "name":result,
                "rational":"Public Policy",
                "accountId":self.account_id,
                "service":"s3",
                "resourceType":"bucket",
                "arn":f"arn:aws:s3:::{result}",
                "policy":"sherlog-1-1"
            })
        for result in formated_results:
            try:
                response = self.client.get_bucket_tagging(Bucket=result['name'])
                resource_tags.append(
                {
                    "arn":f"{self.account_id}/tags/{result['arn']}",
                    "tags":response['TagSet']
                })
                associations.append(
                    {
                        "parentId":result['arn'],
                        "childId":f"{self.account_id}/tags/{result['arn']}"
                    }
                )
            except ClientError:
                self.log.info(f"{result['name']} does not have tags, adding tags")
        return formated_results, resource_tags, associations

