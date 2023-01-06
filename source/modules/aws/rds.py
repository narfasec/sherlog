from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogRDS:
    '''
    Sherlog class to inspect RDS databases
    '''
    def __init__(self, log, session, regions, check_retention):
        # Get available regions list
        self.log = log
        self.check_retention = check_retention
        self.available_regions = boto3.Session().get_available_regions('rds')
        self.regions = regions
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
        self.results_policy_1 = []
        self.results_policy_2 = []
        self.resource_tags=[]
        self.comments = []
        self.has_results=False
 
    def get_module_name(self) -> str:
        '''
        Getter for module/service name
        '''
        return 'rds'

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            policies = ['sherlog-3-1', 'sherlog-3-2']
            policies_list = {
                'sherlog-3-1': self.results_policy_1,
                'sherlog-3-2': self.results_policy_2
            }
            for policy in policies:
                self.formated_results.append({policy:policies_list[policy]})
            self.log.debug('Results: %s', str(self.formated_results))
            return self.formated_results, self.resource_tags
        else:
            return None

    def get_relevant_regions(self):
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
     
    def analyze(self):
        '''
        Function that will read the logging status of rds instances
        '''
        selected_regions = self.get_relevant_regions()
        rds_instances = []
        for region in selected_regions:
            rds = self.session.client('rds', region_name=region)
            try:
                rds_instances = rds.describe_db_instances()
            except ClientError:
                self.log.debug('Error describing instances on region: %s', region)
                continue
            except Exception as error:
                self.log.error(error)
                
            if rds_instances:
                for instance in rds_instances['DBInstances']:
                    rds_name = instance['DBInstanceIdentifier']
                    self.log.debug('Analyzing: %s', rds_name)
                    engine = instance['Engine']
                    self.log.debug('RDS instance found, analysing log configurationfor %s', rds_name)
                    arn = f"arn:aws:rds:{region}:{self.account_id}:db:{rds_name}"
                    policy = 'sherlog-3-1'
                    comments = ['RDS instance without audit logs enabled. Consider enabling them specially if this DB handles critical data']
                    tags = rds.list_tags_for_resource(ResourceName=arn)
                    try:
                        self.log.debug("logs: %s", instance["EnabledCloudwatchLogsExports"])
                        if "audit" not in instance["EnabledCloudwatchLogsExports"] and engine not in ['postgres', 'sqlserver-ex']:
                            self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn, engine=engine, policy=policy, comments=comments)
                            self.has_results = True
                        elif self.check_retention:
                            self.log.debug('RDS with audit logs enabled')
                            self.has_results = True
                            self.evaluate_retention_period(rds_name)
                            self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn, engine=engine, policy='sherlog-3-2', comments=self.comments)
                    except KeyError:
                        self.log.debug('Key Error! This means the instance does not have logs enabled')
                        tags = rds.list_tags_for_resource(ResourceName=arn)
                        self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn, engine=engine, policy=policy, comments=comments)
                        self.has_results = True
                    except Exception as exception:
                        self.log.error(exception)
    
    def evaluate_retention_period(self, rds_name) -> None:
        '''
        Function to check the cloudwatch group for
        '''
        logs = self.session.client('logs').describe_log_groups(
            logGroupNamePrefix=f'example/rds/instance/{rds_name}/audit'
        )
        if logs['logGroups']:
            for group in logs['logGroups']:
                self.log.debug(group)
                try:
                    if group['retentionInDays'] < 30:
                        self.comments.append('Consider increasing the retention up to 30 days')
                    if group['retentionInDays'] > 30:
                        self.comments.append('30 days are enough for hot storage. Consider moving older logs to S3 Standard-IA to reduce costs and keep logs for auditing')
                except KeyError as kerror:
                    self.log.error(kerror)
                    self.comments.append('Retention is set has never expire! Consider setting a retention of 30 days and move older logs to S3 bucket for cold storage')
        else:
            self.comments.append('Log group not found! Check your RDS configuration for Audit logs, make sure the option groups has the right settings')
    
    def format_data(self, rds_name, region, resource_type, tags, arn, engine, policy, comments) -> None:
        """
        Format data to insert on DB
        """
        self.log.debug('Formatting finding for %s with %s', rds_name, policy)
        policies_list = {
            'sherlog-3-1': self.results_policy_1,
            'sherlog-3-2': self.results_policy_2
        }
        policies_list[policy].append({
            "name":rds_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"rds",
            "resourceType":resource_type,
            "engine":engine,
            "arn":arn,
            "policy":policy,
            "comments":comments,
            "tags":tags
        })
