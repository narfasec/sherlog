from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogELB:
    '''
    Sherlog class to inspect Elastic Load Balancer access logs
    '''
    def __init__(self, log, session, regions):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('elbv2')
        self.regions = regions
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
    
    def get_elb_tags(self, client, name) -> list:
        '''
        Get tags of given loadbalancer simply returning a dict of filters
        '''
        elbs_tags = client.describe_tags(
            LoadBalancerNames=[name]
        )
        for elb in elbs_tags:
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
                    attributes = elbv2.describe_load_balancer_attributes(LoadBalancerArn=arn)
                    for attribute in attributes['Attributes']:
                        if attribute['Key'] == 'access_logs.s3.enabled' and attribute['Value'] == 'false':
                            tags = self.get_elb_tags(elb['LoadBalancerName'], elbv2)
                            self.format_data(
                                elb_name=elbv2['LoadBalancerName'],
                                region=region,
                                tags=tags,
                                arn=arn
                            )
    
    def format_data(self, elb_name, region, tags, arn) -> None:
        """
        Format data to for verbose output
        """
        self.formated_results.append({
            "name":elb_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"elbv2",
            "arn":arn,
            "policy":"sherlog-5-1"
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
