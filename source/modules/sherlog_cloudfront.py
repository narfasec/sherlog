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
    def __init__(self, log, session):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('cloudfront')
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
        self.associations=[]
        self.resource_tags=[]
        self.has_results=False

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            return self.formated_results, self.resource_tags, self.associations
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
                if dist['Logging']['Enabled'] is False:
                    self.format_data(cf_name=item, tags=tags, arn=arn)
                    self.has_results = True
            except KeyError:
                self.log.error('Error while getting info from distribution: %s', item)
                self.log.error(KeyError)

    def format_data(self, cf_name, tags, arn):
        """
        Format data to insert on DB
        """
        self.formated_results.append({
            "name":cf_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "service":"cloudfront",
            "arn":arn,
            "policy":"sherlog-4-1"
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
