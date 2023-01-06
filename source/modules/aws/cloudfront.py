'''
Octoguard
Sherlog CloudFron
'''
from typing import Tuple
import boto3

class SherlogCF:
    '''
    Sherlog component for CloudFront distributions
    '''
    def __init__(self, log, session, check_retention):
        # Get available regions list
        self.log = log
        self.check_retention = check_retention
        self.available_regions = boto3.Session().get_available_regions('cloudfront')
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
        self.resource_tags=[]
        self.results_policy_1 = []
        self.results_policy_2 = []
        self.target_buckets = []
        self.has_results=False

    def get_target_buckets(self) -> list:
        '''
        Getter for target buckets
        '''
        return self.target_buckets
    
    def get_module_name(self) -> str:
        '''
        Getter for service/module name
        '''
        return 'cloudfront'
    
    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            policies = ['sherlog-4-1', 'sherlog-4-2']
            policies_list = {
                'sherlog-4-1': self.results_policy_1,
                'sherlog-4-2': self.results_policy_2
            }
            for policy in policies:
                self.formated_results.append({policy:policies_list[policy]})
            self.log.debug('Results: %s', str(self.formated_results))
            return self.formated_results, self.resource_tags
        else:
            return None

    def analyze(self):
        '''
        Function that will read the logging status of the buckets
        '''
        cloudfront = self.session.client('cloudfront')
        paginator = cloudfront.get_paginator('list_distributions')
        page_iterator = paginator.paginate()
        distributions = []
        try:
            for page in page_iterator:
                distributions += [d["Id"] for d in page['DistributionList']['Items']]
        except KeyError:
            self.log.debug('No CloudFront Distributions found')

        for item in distributions:
            try:
                cf_config = cloudfront.get_distribution_config(Id=item)
                arn = f"arn:aws:cloudfront::{self.account_id}:distribution/{item}"
                tags = cloudfront.list_tags_for_resource(Resource=arn)
                dist = cf_config['DistributionConfig']
                self.log.debug(dist)
                policy = ''
                comments = []
                if dist['Logging']['Enabled'] is False:
                    comments = ['Cloudfront distribution without access logs. Consider enabling it for auditing purposes.https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/AccessLogs.html']
                    policy = 'sherlog-4-1'
                    self.has_results = True
                elif self.check_retention:
                    self.has_results=True
                    target_bucket = dist['Logging']['Bucket'][:-17]
                    self.target_buckets.append(target_bucket)
                    policy = 'sherlog-4-2'
                    comments=[f'The access logs for this distribution are sent to s3 bucket, <{target_bucket}>. Check the results of sherlog-1-2 for this bucket']
                self.format_data(cf_name=item, tags=tags, arn=arn, policy=policy, comments=comments)
            except KeyError:
                self.log.error('Error while getting info from distribution: %s', item)
                self.log.error(KeyError)

    def format_data(self, cf_name, tags, arn, policy, comments):
        """
        Format data to insert on DB
        """
        self.log.debug('Formatting finding for %s with %s', cf_name, policy)
        policies_list = {
            'sherlog-4-1': self.results_policy_1,
            'sherlog-4-2': self.results_policy_2
        }
        policies_list[policy].append({
            "name":cf_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "service":"cloudfront",
            "arn":arn,
            "policy":policy,
            "comments":comments,
            "tags": tags
        })
