## DynamoDB analysis code
from typing import Tuple
import boto3
from botocore.exceptions import ClientError

class SherlogDynamo:
    '''
    Sherlog class to inspect RDS databases
    '''
    def __init__(self, log, session):
        # Get available regions list
        self.log = log
        self.available_regions = boto3.Session().get_available_regions('dynamodb')
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
        Function that will read the logging status of rds instances
        '''
        for region in self.available_regions:
            dynamodb = self.session.client('dynamodb', region_name=region)
            try:
                tables = dynamodb.list_tables()
            except ClientError:
                self.log.debug('Error describing instances on region: %s', region)
                continue
            except Exception as error:
                self.log.error(error)
            cloudtrail = self.session.client('cloudtrail')

            trails = cloudtrail.list_trails()
            tables_arn_in_trail_data_event = []
            tables_arn_without_logging = []

            for trail in trails['Trails']:
                trail_arn = trail['TrailARN']
                event_selectors = cloudtrail.get_event_selectors(
                    TrailName=trail_arn
                )
                try:
                    for event_selector in event_selectors['EventSelectors']:
                        if event_selector['DataResources']:
                            for data_source in event_selector['DataResources']:
                                if data_source['Type'] == 'AWS::DynamoDB::Table':
                                    for value in data_source['Values']:
                                        tables_arn_in_trail_data_event.append(value)
                except KeyError as error:
                    self.log.debug('Key Error! '+ error)
                    continue
        
            paginator = dynamodb.get_paginator('list_tables')
            page_iterator = paginator.paginate()

            tables_arn = []
            for page in page_iterator:
                for name in page['TableNames']:
                    arn = dynamodb.describe_table(
                        TableName=name
                    )['Table']['TableArn']
                    tables_arn.append(arn)
                        
            # Comparator
            if tables_arn:
                for arn in tables_arn:
                    if arn not in tables_arn_in_trail_data_event:
                        self.has_results=True
                        tables_arn_without_logging.append(arn)
                        table_name = arn.split("/",1)[1]
                        tags = dynamodb.list_tags_of_resource(ResourceArn=arn)
                        self.format_data(table_name, region, 'table', tags, arn)
            
            # if not tables_arn_in_trail_data_event:
            #     return 'There are no Data Events of type: DynamoDB'
            # else:
            #     return{region:{'dynamoDB_tables_with_logs':tables_arn_in_trail_data_event, 'dynamoDB_tables_without_logs':tables_arn_without_logging}}

    
    def format_data(self, db_name, region, resource_type, tags, arn):
        """
        Format data to insert on DB
        """
        self.formated_results.append({
            "name":db_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"DynamoDB",
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
