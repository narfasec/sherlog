'''
Sherlog Inititator
'''
import logging
import boto3
import itertools
import threading
import time
import sys

from botocore.exceptions import ClientError
from .helpers.all_regions import all_regions
from .aws_session import AwsSession
from .sherlog_s3 import SherlogS3
from .sherlog_rds import SherlogRDS
from .sherlog_cloudfront import SherlogCF
from .sherlog_redshift import SherlogRedshift
from .sherlog_dynamoDB import SherlogDynamo
from .sherlog_elb import SherlogELB
from .arango import DBConnection
from .pretty_output import PrettyOutput
from .loader import Loader

class Sherlog:
    '''
    Sherlog class initiator
    '''
    
    def __init__(self, debug, profile, format, output, regions):
        # Get available regions list
        self.debug = debug
        self.output = output
        self.format = format
        self.regions = regions
        self.session=boto3.session.Session(profile_name=profile)
        self.pretty_output = PrettyOutput()
        self.all_results = []
        self.done = False
    
    def print_results(self, results):
        '''
        Function to format the output in the console
        '''
        # print(results)
        for result in results:
            if 's3' in result:
                headers = ['Bucket', 'arn', 'Policy']
                if len(result['s3']) == 1:
                    self.pretty_output.print_color(
                        header='S3, Sherlog-1-1',
                        text="Found one s3 bucket without access logs. Consider enabling access logs on buckets that contain critical information to audit every resquest. See how to enable on https://www.ocotoguard.io/sherlog-1-1",
                        color='yellow'
                    )
                    name = result['name']
                    arn = result['arn']
                    policy = result['policy']
                    values = [name, arn, policy]
                    self.pretty_output.print_results(headers=headers, values=values)
                else:
                    self.pretty_output.print_color(
                        header='S3, Sherlog-1-1',
                        text="Found s3 buckets without access logs. Consider enabling access logs on buckets that contain critical information to audit every resquest. See how to enable on https://www.ocotoguard.io/sherlog-1-1",
                        color='yellow'
                    )
                    values = []
                    for s3_result in result['s3']:
                        name = s3_result['name']
                        arn = s3_result['arn']
                        policy = s3_result['policy']
                        values.append([name,arn,policy])
                    self.pretty_output.print_results(headers=headers, values=values)
            if 'dynamodb' in result:
                headers = ['Name', 'Region', 'arn', 'Policy']
                if len(result['dynamodb']) == 1:
                    self.pretty_output.print_color(
                        header='DynamoDB, Sherlog-2-1',
                        text="Found one DynamoDB table without audit logs. Consider enabling audit logs on database that contain critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-2-1",
                        color='yellow'
                    )
                else:
                    self.pretty_output.print_color(
                        header='DynamoDB, Sherlog-2-1',
                        text="Found DynamoDB tables without audit logs. Consider enabling audit logs on databases that contain critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-3-1",
                        color='yellow'
                    )
                values = []
                for dynamo_result in result['dynamodb']:
                    name, region, arn, policy = dynamo_result['name'], dynamo_result['region'], dynamo_result['arn'], dynamo_result['policy']
                    values.append([name,region,arn,policy])
                self.pretty_output.print_results(headers=headers, values=values)
            if 'cloudfront' in result:
                headers = ['Name', 'arn','Policy']
                if len(result['cloudfront']) == 1:
                    self.pretty_output.print_color(
                        header='Cloudfront, Sherlog-4-1',
                        text="Found one CF distribution instance without audit logs. Consider enabling audit logs on distributions that handle critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-4-1",
                        color='yellow'
                    )
                else:
                    self.pretty_output.print_color(
                        header='Cloudfront, Sherlog-4-1',
                        text="Found cloudfront distributions without audit logs. Consider enabling audit logs on distributions that handle critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-4-1",
                        color='yellow'
                    )
                values = []
                for cf_result in result['cloudfront']:
                    name, arn, policy = cf_result['name'], cf_result['arn'], cf_result['policy']
                    values.append([name,arn,policy])
                self.pretty_output.print_results(headers=headers, values=values)
            if 'rds' in result:
                headers = ['Name', 'Region', 'arn','Engine', 'Policy']
                if len(result['rds']) == 1:
                    self.pretty_output.print_color(
                        header='RDS, Sherlog-3-1',
                        text="Found one rds instance without audit logs. Consider enabling audit logs on database that contain critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-3-1",
                        color='yellow'
                    )
                else:
                    self.pretty_output.print_color(
                        header='RDS, Sherlog-3-1',
                        text="Found rds instances without audit logs. Consider enabling audit logs on databases that contain critical information to audit every operation. See how to enable on https://www.ocotoguard.io/sherlog-3-1",
                        color='yellow'
                    )
                values = []
                for rds_result in result['rds']:
                    name, region, arn, engine, policy = rds_result['name'], rds_result['region'], rds_result['arn'],rds_result['engine'], rds_result['policy']
                    values.append([name,region,arn,engine,policy])
                self.pretty_output.print_results(headers=headers, values=values)
            if 'elb' in result:
                print('there is an ELB')
                headers = ['Name', 'Region', 'arn', 'Policy']
                if len(result['elb']) == 1:
                    self.pretty_output.print_color(
                        header='ELBV2, Sherlog-5-1',
                        text="Found one load balancer without access logs. Consider enabling access logs on elb that handle critical data. See how to enable on https://www.ocotoguard.io/sherlog-5-1",
                        color='yellow'
                    )
                else:
                    self.pretty_output.print_color(
                        header='ELBV2, Sherlog-5-1',
                        text="Found load balancers without access logs. Consider enabling access logs on load balancers that handle critical data. See how to enable on https://www.ocotoguard.io/sherlog-5-1",
                        color='yellow'
                    )
                values = []
                for elb_result in result['elb']:
                    name, region, arn, policy = elb_result['name'], elb_result['region'], elb_result['arn'], elb_result['policy']
                    values.append([name,region,arn,policy])
                self.pretty_output.print_results(headers=headers, values=values)
    
    def animate(self):
        '''
        Simple animation to create a loader during sherlog processing
        '''
        for c in itertools.cycle(["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]):
            if self.done:
                break
            sys.stdout.write('\rloading ' + c +' ')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write('\rDone!     ')
            
    def init(self):
        '''
        Main function
        '''
        if self.regions != "all-regions":
            available_regions = all_regions()
            for region in self.regions:
                if region not in available_regions:
                    print(f'{region} Unvailable region on AWS. Please provide a correct set of regions if you want to use "--region" option')
                    sys.exit(1)
    
        fmt = '%(asctime)s [%(levelname)s] [%(module)s] - %(message)s'
        logging.basicConfig(format=fmt, datefmt='%m/%d/%Y %I:%M:%S')
        log = logging.getLogger('LUCIFER')
        if self.debug:
            log.setLevel('DEBUG')
        log.setLevel('INFO')
        self.pretty_output.print_color(text='Starting sherlog engine', color='green')
        loader = Loader("Scanning...", "Done!", 0.05).start()
        
        
        # Verify credentials
        sts = self.session.client('sts')
        try:
            sts.get_caller_identity()
        except ClientError as client_error:
            self.pretty_output.print_color(text=str(client_error), color='red')
            self.pretty_output.print_color(text='Check if your AWS credentials are updated', color='red')
            exit(1)
        
        resource_tags=[]
        all_results = []
        associations=[]
        
        # Inspecting S3
        sherlog_s3 = SherlogS3(log)
        sherlog_s3.start(self.session)
        if sherlog_s3.get_results():
            buckets, buckets_tags, buckets_associations = sherlog_s3.get_results()
            resource_tags.extend(buckets_tags)
            associations.extend(buckets_associations)
            all_results.append({'s3':buckets})
        else:
            log.debug('Everything ok with s3, nothing to report')

        # Inspecting DynamoDB
        sherlog_dynamodb = SherlogDynamo(log, self.session, self.regions)
        sherlog_dynamodb.analyze()
        if sherlog_dynamodb.get_results():
            dynamo_tables, dynamo_tags, dynamo_associations = sherlog_dynamodb.get_results()
            resource_tags.append(dynamo_tags)
            associations.extend(dynamo_associations)
            all_results.append({'dynamodb':dynamo_tables})
   
        #Inspecting RDS
        sherlog_rds = SherlogRDS(log, self.session, self.regions)
        sherlog_rds.analyze()
        if sherlog_rds.get_results():
            rds_instances, rds_tags, rds_associations = sherlog_rds.get_results()
            resource_tags.extend(rds_tags)
            associations.extend(rds_associations)
            all_results.append({'rds':rds_instances})
            
        # Inspecting CloudFront
        sherlog_cloudfront = SherlogCF(log, self.session)
        sherlog_cloudfront.analyze()
        if sherlog_cloudfront.get_results():
            cf_dists, cf_tags, cf_associations = sherlog_cloudfront.get_results()
            resource_tags.append(cf_tags)
            associations.extend(cf_associations)
            all_results.append({'cloudfront':cf_dists})
        
        #Inspecting ELBs
        sherlog_elb = SherlogELB(log, self.session, self.regions)
        sherlog_elb.analyze()
        if sherlog_elb.get_results():
            elb_instances, elb_tags, elb_associations = sherlog_elb.get_results()
            resource_tags.extend(elb_tags)
            associations.extend(elb_associations)
            all_results.append({'elb':elb_instances})
        
        if all_results:
            self.pretty_output.success()
            if self.format == 'JSON':
                #TODO
                return None
            if self.format == '--arango':
                # Populate DB
                db_connection = DBConnection(log)
                for result in all_results:
                    db_connection.list_to_collection(collection='sherlog_resources', list=result) # pylint: disable=E1101
                    db_connection.list_to_collection(list=resource_tags, collection='resource_tags') # pylint: disable=E1101
                db_connection.create_association(associations=associations) # pylint: disable=E1101
            else:
                loader.stop()
                self.print_results(results=all_results)
        
        return self.pretty_output.print_color(text="\nScan finished successfully", color='green')

		
		# Inspecting Redshift #TODO
		# sherlog_redshift = SherlogRedshift(log, self.account_id)
		# if sherlog_redshift.analyze():
		# 	if sherlog_cloudfront.get_results():
		# 		redshift_clusters, redshift_tags, redshift_associations = sherlog_redshift.get_results()
		# 		resource_tags.extend(redshift_tags)
		# 		associations.extend(redshift_associations)
		# 		all_results.append(redshift_clusters)