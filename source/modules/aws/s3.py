'''
'''
from typing import Tuple
import boto3, sys
from botocore.exceptions import ClientError

class SherlogS3:
    '''
    Sherlog class to inspect S3 buckets
    '''
    def __init__(self, log, session, regions, retention_check, target_buckets):
        # Get available regions list
        self.log = log
        self.session = session
        self.regions = regions
        self.retention_check = retention_check
        self.target_buckets = target_buckets
        self.account_id = session.client('sts').get_caller_identity().get('Account')
        self.available_regions = boto3.Session().get_available_regions('s3')
        self.formated_results = []
        self.results_policy_1 = []
        self.results_policy_2 = []
        self.resource_tags=[]
        self.has_results=False

    def get_module_name(self) -> str:
        '''
        Getter for service/module name
        '''
        return 's3'

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            policies = ['sherlog-1-1', 'sherlog-1-2']
            policies_list = {
                'sherlog-1-1': self.results_policy_1,
                'sherlog-1-2': self.results_policy_2
            }
            for policy in policies:
                self.formated_results.append({policy:policies_list[policy]})
            self.log.debug('Results: %s', str(self.formated_results))
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
            try:
                result = self.get_bucket_logging_of_s3(bucket["Name"])["LoggingEnabled"]
                logging = True
            except KeyError:
                logging = False
            except Exception as error:
                self.log.error(error)
            self.log.debug("Analysing S3: %s",bucket['Name'])
            if not logging:
                if not self.is_target_bucket(bucket["Name"]):
                    self.log.debug('%s is not loging and it is not a target bucket. Adding to fidings results', bucket["Name"])
                    self.has_results=True
                    name = bucket["Name"]
                    arn = f"arn:aws:s3:::{name}"
                    comments = ["Access logs are not enabled! Consider enable logs on S3 bucket if it contains critical data"]
                    tags = self.get_tags(name)
                    self.format_data(name=name, tags=tags, arn=arn, policy='sherlog-1-1', comments=comments)
                elif self.retention_check:
                    self.evaluate_retention_period(name=bucket["Name"])

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

    def is_target_bucket(self, bucket) -> bool:
        '''
        Function to check if bucket is receiving logs by analysing it's policy
        '''
        self.log.debug('Target buckets received: %s', str(self.target_buckets))
        if bucket in self.target_buckets:
            return True
        return False

    def evaluate_retention_period(self, name):
        '''
        Function that analyzes the retention period of the target bucket
        '''
        recommendations = []
        tags = {}
        no_life_cycle_error = 'An error occurred (NoSuchLifecycleConfiguration) when calling the GetBucketLifecycleConfiguration operation: The lifecycle configuration does not exist'
        result = None
        arn = f"arn:aws:s3:::{name}"
        try:
            result = self.session.client('s3').get_bucket_lifecycle_configuration(
                Bucket=name
            )
        except ClientError as error:
            # self.log.error(error)
            if str(error) == no_life_cycle_error:
                recommendations.append('No lifeCycle! Consider enabling a lifecycle to reduce costs on this target bucket. Check the reccomendation on:https://medium.com/avmconsulting-blog/aws-s3-lifecycle-management-1ed2f67c3b73')

        if result:
            transition_to_ia = False
            transition_to_glacier = False
            one_year_expiration = False
            no_expiration = False
            all_rules_disabled = True
            tags = self.get_tags(name)
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
                    if not no_expiration:
                        if expiration['Days'] >= 365:
                            one_year_expiration = True
            if not all_rules_disabled:
                if not transition_to_ia:
                    recommendations.append("Objects from the original bucket should transit to 'STANDARD IA' after 30 days")
                if not transition_to_glacier:
                    recommendations.append("Objects from 'STANDARD IA' bucket should transit to 'GLACIER' after 60 days")
                if no_expiration:
                    recommendations.append("No expire configuration was found. Consider activating an expiration for at least 365 days. This way, logs are kept for auditing and costs are reduced")
                elif not one_year_expiration:
                    recommendations.append("Consider to increase the expiration for at least 365 days")
            else:
                recommendations.append('Enable lifecycle rules for better management of objects and to reduce costs')
        if recommendations:
            self.has_results = True
            self.format_data(name=name, tags=tags, arn=arn, policy="sherlog-1-2", comments=recommendations)
    
    def get_tags(self, bucket) -> dict:
        '''
        Function to get tags from bucket
        '''
        try:
            return self.session.client('s3').get_bucket_tagging(Bucket=bucket)
        except KeyError:
            self.log.error('Name bucket not found when getting the tags')
            return {}
        except ClientError as error:
            if 'NoSuchTagSet' not in str(error):
                return {}
        except Exception as error:
            self.log.error(error)
            return {}

    def format_data(self, name, tags, arn, policy, comments):
        """
        Format data in json
        """
        self.log.debug('Formatting finding for %s with %s', name, policy)
        policies_list = {
            'sherlog-1-1': self.results_policy_1,
            'sherlog-1-2': self.results_policy_2
        }
        policies_list[policy].append({
            "name":name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "service":"s3",
            "arn":arn,
            "policy":policy,
            "comments":comments,
            "tags":tags
        })
