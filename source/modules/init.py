'''
Sherlog Inititator
'''
import logging
import itertools
import time
import sys
import boto3

from botocore.exceptions import ClientError
from .helpers.all_regions import all_regions
from .helpers.loader import Loader
from .helpers.pretty_output import PrettyOutput
from .helpers.results_printer import ResultsPrinter
from .aws.s3 import SherlogS3
from .aws.rds import SherlogRDS
from .aws.cloudfront import SherlogCF
from .aws.dynamoDB import SherlogDynamo
from .aws.elb import SherlogELB

class Sherlog:
    '''
    Sherlog class initiator
    '''

    def __init__(self, debug, profile, output, regions, check_retention):
        # Get available regions list
        self.check_retention = check_retention
        self.debug = debug
        self.output = output
        self.regions = regions
        self.session=boto3.session.Session(profile_name=profile)
        self.pretty_output = PrettyOutput()
        self.all_results = []
        self.target_buckets = []
        self.done = False
    
    def init(self):
        '''
        Function thay initializes sherlog engine
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
        else:
            log.setLevel('INFO')
        self.pretty_output.print_color(text='Starting sherlog engine', color='green')
        if not self.output and not self.debug:
            loader = Loader("Scanning...", "Done!", 0.05).start()
   
        # Verify credentials
        sts = self.session.client('sts')
        try:
            sts.get_caller_identity()
        except ClientError as client_error:
            self.pretty_output.print_color(text=str(client_error), color='red')
            self.pretty_output.print_color(text='Check if your AWS credentials are updated', color='red')
            exit(1)

        # Listing all AWS modules available in Sherlog
        resource_tags=[]
        all_results = []
        resource_modules = [
            SherlogDynamo(log, self.session, self.regions, self.check_retention),
            SherlogRDS(log, self.session, self.regions, self.check_retention),
            SherlogCF(log, self.session, self.check_retention),
            SherlogELB(log, self.session, self.regions, self.check_retention),
            SherlogS3(log, self.session, self.regions, self.check_retention, self.target_buckets)
        ]

        # Start anaysing each module, S3 is the last one because it depends on other modules to get the target buckets (they can be empty)
        for module in resource_modules:
            module.analyze()
            if module.has_results:
                results, tags = module.get_results()
                resource_tags.extend(tags)
                module_name = module.get_module_name()
                if module_name in ['elbv2', 'cloudfront']:
                    t_buckets = module.get_target_buckets()
                    if t_buckets:
                        for t_bucket in t_buckets:
                            self.target_buckets.append(t_bucket)
                log.debug("Evaluation finnished on: %s", module_name)
                all_results.append({module_name:results})

        # Finalizing Sherlog with output option
        if all_results:
            if self.output == "json":
                return print(all_results)
            if not self.output:
                log.debug("Printing results on the console")
                log.debug(all_results)
                self.pretty_output.success()
                if not self.debug:
                    loader.stop()
                printer = ResultsPrinter(self.pretty_output)
                printer.print_results(results=all_results)

        return self.pretty_output.print_color(text="\nScan finished successfully", color='green')
