'''
'''
from typing import Tuple
import boto3, sys
from botocore.exceptions import ClientError

class SherlogS3:
    '''
    Sherlog class to inspect S3 buckets
    '''
    def __init__(self, log, session, regions, retention_check):
        # Get available regions list
        self.log = log
        self.session = session
        self.regions = regions
        self.retention_check = retention_check
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
        logging = None
        if self.get_buckets():
            buckets = self.get_buckets()
        for bucket in buckets['Buckets']:
            result = {}
            try:
                result = self.get_bucket_logging_of_s3(bucket["Name"])["LoggingEnabled"]
                print(result)
                logging = True
            except KeyError:
                logging = False
            except Exception as error:
                self.log.error(error)
                
            if not logging:
                print(logging)
                self.has_results=True
                name = bucket["Name"]
                arn = f"arn:aws:s3:::{name}"
                tags = {}
                try:
                    tags = self.session.client('s3').get_bucket_tagging(Bucket=name)
                except KeyError:
                    self.log.error('Name bucket not found when getting the tags')
                except ClientError as error:
                    if 'NoSuchTagSet' not in str(error):
                        self.log.error(error)
                except Exception as error:
                    self.log.error(error)
                self.format_data(name=name, tags=tags, arn=arn, policy='sherlog-1-1')
            elif self.retention_check:
                print('Retention check')
                self.evaluate_retention_period(result)

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

    def evaluate_retention_period(self, bucket):
        '''
        Function that analyzes the retention period of the target bucket
        '''
        recommendations = []
        arn = ""
        tags = {}
        no_life_cycle_error = 'An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist'
        result = None
        name = bucket['TargetBucket']
        try:
            result = self.session.client('s3').get_bucket_lifecycle_configuration(
                Bucket=name
            )
        except ClientError as error:
            if str(error) == no_life_cycle_error:
                recommendations.append('No lifeCycle! Consider enabling a lifecycle to reduce costs on this target bucket. Check the reccomendation on:')

        if result:
            print(result)
            transition_to_ia = False
            transition_to_glacier = False
            one_year_expiration = False
            no_expiration = False
            all_rules_disabled = True
            tags = self.session.client('s3').get_bucket_tagging(Bucket=name)
            arn = f"arn:aws:s3:::{name}"
            for rule in result['Rules']:
                if rule['Status'] == 'Enabled':
                    all_rules_disabled = False
                    for transition in rule['Transitions']:
                        if transition['Days'] == 30 and transition['StorageClass'] == 'STANDARD_IA':
                            transition_to_ia = True
                        elif transition['Days'] == 60 and transition['StorageClass'] == 'GLACIER':
                            transition_to_glacier = True
                    expiration = {}
                    try:
                        expiration = rule['Expiration']
                    except KeyError:
                        no_expiration = True
                    if expiration['Days'] >= 365:
                        one_year_expiration = True
            if not all_rules_disabled:
                if not transition_to_ia:
                    recommendations.append("Objects from the original bucket should transit to 'STANDARD IA' after 30 days")
                if not transition_to_glacier:
                    recommendations.append("Objects from 'STANDARD IA' bucket should transit to 'GLACIER' after 60 days")
                if no_expiration:
                    recommendations.append("No expire configuration was found. Consider activating an expiration for at least 365 days. This way, logs are kept for auditing and costs are reduced")
                if not one_year_expiration:
                    recommendations.append("Consider to increase the expiration for at least 365 days")
            else:
                recommendations.append('Enable lifecycle rules for better management of objects and to reduce costs')
        self.format_data(name=bucket['TargetBucket'], tags=tags, arn=arn, policy="sherlog-1-2", recomendations=recommendations)
     
    def format_data(self, name, tags, arn, policy, recomendations=""):
        """
        Format data in json
        """
        self.formated_results.append({
            "name":name,
            "rational":"Public Policy",
            "service":"s3",
            "arn":arn,
            "policy":policy,
            "recommendations":recomendations
        })
        self.resource_tags.append(
            {
                "arn":f"{self.account_id}/tags/{arn}",
                "tags":tags
            }
        )
