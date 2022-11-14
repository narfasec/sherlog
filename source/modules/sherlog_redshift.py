'''
Octoguard
Sherlog Redshift
'''
from typing import Tuple
import boto3
from botocore.exceptions import ClientError

class SherlogRedshift:
    '''
    Sherlog component for CloudFront distributions
    '''
    def __init__(self, log, account_id):
        # Get available regions list
        self.log = log
        self.account_id=account_id
        self.formated_results=[]
        self.associations=[]
        self.resource_tags=[]
        self.has_results=False

    def start(self, session):
        '''
        Initiating Redshift scanning for given AES account
        '''
        available_regions = boto3.Session().get_available_regions('redshift')
        for region in available_regions:
            redshift = session.client('redshift', region_name=region)
            clusters = self.get_clusters(client=redshift, region=region)
            for cluster in clusters['Clusters']:
                log_status = self.get_log_status(client=redshift, cluster_id=cluster['ClusterIdentifier'])
                logging = self.analyze(log_status)
                if not logging:
                    redshift_name = cluster['ClusterIdentifier']
                    arn = f"arn:aws:rds:{region}:{self.account_id}:db:{redshift_name}"
                    tags = cluster['Tags']
                    node_type = cluster['NodeType']
                    self.format_data(redshift_name=redshift_name, region=region, node_type=node_type, tags=tags, arn=arn)
                    self.has_results = True

    def get_results(self) -> Tuple[list, list, list]:
        '''
        Geter for results
        '''
        if self.has_results:
            return self.formated_results, self.resource_tags, self.associations
        else:
            return None
        
    def get_clusters(self, client, region) -> dict:
        '''
        Get Redshift Clusters from AWS by region
        '''
        try:
            return client.describe_clusters()
        except ClientError:
            self.log.error('Error describing instances on region: %s', region)
            # self.log.error(c_error)
        return None
            
    def get_log_status(self, client, cluster_id) -> dict:
        '''
        Get log status from Redshift by ID
        '''
        try:
            return client.describe_logging_status(ClusterIdentifier=cluster_id)
        except ClientError as client_error:
            self.log.error("Error getting log status, %s", client_error)
        return None

    def analyze(self, data) -> bool:
        '''
        Function that will read the logging status of redshift cluster
        '''
        if data['LoggingEnabled'] is not True:
            return False
        else:
            self.log.info('Redshift cluster %s has log status enabled', data['ClusterIdentifier'])
            return True


    def format_data(self, redshift_name, region, node_type, tags, arn):
        """
        Format data to insert on DB
        """
        self.formated_results.append({
            "name":redshift_name,
            "rational":"Public Policy",
            "accountId":self.account_id,
            "region":region,
            "service":"redshift",
            "nodeType":node_type,
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
