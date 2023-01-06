from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogELB:
    '''
    Sherlog class to inspect Elastic Load Balancer access logs
    '''
    def __init__(self, log, session, regions, check_retention):
        # Get available regions list
        self.log = log
        self.check_retention = check_retention
        self.available_regions = boto3.Session().get_available_regions('elbv2')
        self.regions = regions
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
        return 'elbv2'
    
    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            policies = ['sherlog-5-1', 'sherlog-5-2']
            policies_list = {
                'sherlog-5-1': self.results_policy_1,
                'sherlog-5-2': self.results_policy_2
            }
            for policy in policies:
                self.formated_results.append({policy:policies_list[policy]})
            self.log.debug('Results: %s', str(self.formated_results))
            return self.formated_results, self.resource_tags
        else:
            return None

    def get_relevant_regions(self) -> list:
        '''
        Filter selected regions if user used --region option
        '''
        resource_regions = []
        if self.regions == "all-regions":
            return self.available_regions
        else:
            for region in self.regions:
                if region in self.available_regions:
                    resource_regions.append(region)
        return resource_regions
    
    def get_elb_tags(self, client, arn) -> list:
        '''
        Get tags of given loadbalancer simply returning a dict of filters
        '''
        elbs_tags = client.describe_tags(
            ResourceArns=[arn]
        )
        for elb in elbs_tags['TagDescriptions']:
            return elb['Tags']
        
    def analyze(self) -> None:
        '''
        Function that will read the logging status of rds instances
        '''
        selected_regions = self.get_relevant_regions()
        elbs = []
        for region in selected_regions:
            elbv2 = self.session.client('elbv2', region_name=region)
            try:
                elbs = elbv2.describe_load_balancers()
                if not elbs:
                    continue
            except ClientError:
                self.log.debug('Error describing load balancers on region: %s', region)
                continue
            except Exception as error:
                self.log.error(error)
            
            paginator = elbv2.get_paginator('describe_load_balancers')
            page_iterator = paginator.paginate(
                
            )

            for page in page_iterator:
                for elb in page['LoadBalancers']:
                    arn = elb['LoadBalancerArn']
                    elb_name=elb['LoadBalancerName']
                    self.log.debug("Analysing alb: %s", elb_name)
                    tags = self.get_elb_tags(elbv2, arn)
                    attributes = elbv2.describe_load_balancer_attributes(LoadBalancerArn=arn)
                    self.log.debug('Attributes %s', str(attributes['Attributes']))
                    for attribute in attributes['Attributes']:
                        if attribute['Key'] == 'access_logs.s3.enabled' and attribute['Value'] == 'false':
                            self.has_results=True
                            self.format_data(
                                elb_name=elb_name,
                                region=region,
                                tags=tags,
                                arn=arn,
                                policy='sherlog-5-1',
                                comments=['Load Balancer without access logs. Consider enabling it for auditing purposes. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html']
                            )
                        elif self.check_retention and attribute['Key'] == 'access_logs.s3.bucket' and attribute['Value']:
                            self.has_results=True
                            comments = []
                            if attribute['Value']:
                                target_bucket = attribute['Value']
                                self.target_buckets.append(target_bucket)
                                comments=[f'The access logs of this elb are sent to s3 bucket: {target_bucket}. Check the results of sherlog-1-2 for this bucket']
                            else:
                                comments = ['No target bucket has been selected. Choose a target bucket to store ALB access logs. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html']
                            self.format_data(
                                elb_name=elb['LoadBalancerName'],
                                region=region,
                                tags=tags,
                                arn=arn,
                                policy='sherlog-5-2',
                                comments=comments
                            )
    
    def format_data(self, elb_name, region, tags, arn, comments,policy) -> None:
        """
        Format data to for verbose output
        """
        self.log.debug('Formatting finding for %s with %s', elb_name, policy)
        policies_list = {
            'sherlog-5-1': self.results_policy_1,
            'sherlog-5-2': self.results_policy_2
        }
        policies_list[policy].append({
            "name":elb_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"elbv2",
            "arn":arn,
            "policy":policy,
            "comments": comments,
            "tags": tags
        })
