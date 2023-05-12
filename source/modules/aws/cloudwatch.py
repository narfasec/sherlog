from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogCWLogs:
    '''
    Sherlog class to inspect Elastic Load Balancer access logs
    '''
    def __init__(self, log, session, regions, check_retention):
        # Get available regions list
        self.log = log
        self.check_retention = check_retention
        self.available_regions = boto3.Session().get_available_regions('logs')
        self.regions = regions
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
        self.resource_tags=[]
        self.results_policy = []
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
        return 'logs'
    
    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            policies = ['sherlog-6']
            policies_list = {
                'sherlog-6': self.results_policy
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
        log_groups = []
        for region in selected_regions:
            cw_logs = self.session.client('logs', region_name=region)
            try:
                logs = cw_logs.describe_log_groups()
                if not logs:
                    continue
            except ClientError:
                self.log.debug('Error describing cw logs on region: %s', region)
                continue
            except Exception as error:
                self.log.error(error)
            
            paginator = cw_logs.get_paginator('describe_log_groups')
            page_iterator = paginator.paginate()

            for page in page_iterator:
                for log_group in page['logGroups']:
                    arn = log_group['arn']
                    log_group_name=log_group['logGroupName']
                    self.log.debug("Analysing alb: %s", log_group_name)
                    tags = cw_logs.list_tags_log_group(logGroupName=log_group_name)
                    log_group_description = cw_logs.describe_log_groups(logGroupNamePrefix=log_group_name)
                    for group in log_group_description['logGroups']:
                        try:
                            if group['retentionInDays'] and group['retentionInDays'] > 30:
                                retention_period = group['retentionInDays']
                                self.has_results=True
                                self.format_data(
                                    log_group_name=log_group_name,
                                    region=region,
                                    tags=tags,
                                    arn=arn,
                                    policy='sherlog-6',
                                    comments=[f'Log group with a retention period greater than 30 days ({retention_period} days ). Consider storing older logs (specially if they are not frequently accessed) in cheaper options like S3-IA or S3 glacier.']
                                )
                        except KeyError:
                            self.has_results=True
                            self.format_data(
                                log_group_name=log_group_name,
                                region=region,
                                tags=tags,
                                arn=arn,
                                policy='sherlog-6',
                                comments=['Log group retention policy set with "Never Expire". Consider adding a retention policy to save costs. We reccomend 30 days and older logs should be stored in cold storage']
                            )
                            self.log.debug('Log group set with "NeverExpire" retention policy')
                        except Exception as error:
                            self.log.error(error)
                # self.log.debug('Attributes %s', str(attributes['Attributes']))
                #     for attribute in attributes['Attributes']:
                #         if attribute['Key'] == 'access_logs.s3.enabled' and attribute['Value'] == 'false':
                #             self.has_results=True
                #             self.format_data(
                #                 elb_name=elb_name,
                #                 region=region,
                #                 tags=tags,
                #                 arn=arn,
                #                 policy='sherlog-5-1',
                #                 comments=['Load Balancer without access logs. Consider enabling it for auditing purposes. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html']
                #             )
                #         elif self.check_retention and attribute['Key'] == 'access_logs.s3.bucket' and attribute['Value']:
                #             self.has_results=True
                #             comments = []
                #             if attribute['Value']:
                #                 target_bucket = attribute['Value']
                #                 self.target_buckets.append(target_bucket)
                #                 comments=[f'The access logs of this elb are sent to s3 bucket: {target_bucket}. Check the results of sherlog-1-2 for this bucket']
                #             else:
                #                 comments = ['No target bucket has been selected. Choose a target bucket to store ALB access logs. https://docs.aws.amazon.com/elasticloadbalancing/latest/application/enable-access-logging.html']
                #             self.format_data(
                #                 elb_name=elb['LoadBalancerName'],
                #                 region=region,
                #                 tags=tags,
                #                 arn=arn,
                #                 policy='sherlog-5-2',
                #                 comments=comments
                #             )
    
    def format_data(self, log_group_name, region, tags, arn, comments, policy) -> None:
        """
        Format data to for verbose output
        """
        self.log.debug('Formatting finding for %s with %s', log_group_name, policy)
        policies_list = {
            'sherlog-6': self.results_policy
        }
        policies_list[policy].append({
            "name":log_group_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"elbv2",
            "arn":arn,
            "policy":policy,
            "comments": comments,
            "tags": tags
        })
