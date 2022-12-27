from typing import Tuple
import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogRDS:
    '''
    Sherlog class to inspect RDS databases
    '''
    def __init__(self, log, session, regions):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('rds')
        self.regions = regions
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
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
                    engine = instance['Engine']
                    self.log.debug('RDS instance found, analysing log configurationfor %s', rds_name)
                    arn = f"arn:aws:rds:{region}:{self.account_id}:db:{rds_name}"
                    try:
                        if "audit" not in instance["EnabledCloudwatchLogsExports"] and engine not in ['postgres', 'sqlserver-ex']:
                            tags = rds.list_tags_for_resource(ResourceName=arn)
                            self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn, engine=engine)
                            self.has_results = True
                        else:
                            self.log.debug('RDS with audit logs enabled')
                    except KeyError:
                        self.log.debug('Key Error! This means the instance does not have logs enabled')
                        tags = rds.list_tags_for_resource(ResourceName=arn)
                        self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn, engine=engine)
                        self.has_results = True
                    except Exception as exception:
                        self.log.error(exception)
    
    def format_data(self, rds_name, region, resource_type, tags, arn, engine):
        """
        Format data to insert on DB
        """
        self.formated_results.append({
            "name":rds_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"rds",
            "resourceType":resource_type,
            "engine":engine,
            "arn":arn,
            "policy":"sherlog-3-1"
        })
        self.resource_tags.append(
            {
                "arn":f"{self.account_id}/tags/{arn}",
                "tags":tags
            }
        )

