import boto3, botocore, os
from botocore.exceptions import ClientError

class SherlogRDS:
    '''
    Sherlog class to inspect RDS databases
    '''
    def __init__(self, log, session):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('rds')
        self.account_id=session.client('sts').get_caller_identity().get('Account')
        self.session=session
        self.formated_results=[]
        self.associations=[]
        self.resource_tags=[]
        self.has_results=False
    
    def get_results(self):
        '''
        Geter for results
        '''
        if self.has_results:
            return self.formated_results, self.resource_tags, self.associations
        else:
            return None

    def analyze(self):
        '''
        Function that will read the logging status of rds instances
        '''
        for region in self.available_regions:
            print(region)
            rds = self.session.client('rds', region_name=region)
            try:
                rds_instances = rds.describe_db_instances()
            except ClientError as c_error:
                self.log.error('Error describing instances on regio: %s', region)
                self.log.error(c_error)
                continue
            if rds_instances:
                for instance in rds_instances['DBInstances']:
                    rds_name = instance['DBInstanceIdentifier']
                    self.log.info('RDS instance found, analysing log configurationfor %s', rds_name)
                    arn = f"arn:aws:rds:{region}:{self.account_id}:db:{rds_name}"
                    try:
                        if "audit" not in instance["EnabledCloudwatchLogsExports"]:
                            tags = rds.list_tags_for_resource(ResourceName=arn)
                            self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn)
                            self.has_results = True
                        else:
                            self.log.info('RDS with audit logs enabled')
                    except KeyError:
                        self.log.debug('Key Error! This means the instance does not have logs enabled')
                        tags = rds.list_tags_for_resource(ResourceName=arn)
                        self.format_data(rds_name=rds_name, region=region, resource_type='db', tags=tags, arn=arn)
                        self.has_results = True
                    except Exception as exception:
                        self.log.error(exception)

    
    def format_data(self, rds_name, region, resource_type, tags, arn):
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
            "arn":arn,
            "policy":"sherlog-2-1"
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

