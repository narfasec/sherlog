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
        self.done = False

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
        if not self.output:
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
        resource_modules = [
            SherlogS3(log, self.session, self.regions, self.check_retention),
            SherlogDynamo(log, self.session, self.regions),
            SherlogRDS(log, self.session, self.regions),
            SherlogCF(log, self.session),
            SherlogELB(log, self.session, self.regions)
        ]

        for module in resource_modules:
            module.analyze()
            if module.get_results():
                results, tags = module.get_results()
                resource_tags.extend(tags)
                all_results.append({results[0]['service']:results})

        if all_results:
            if self.output == "json":
                return print(all_results)
            if not self.output:
                self.pretty_output.success()
                loader.stop()
                printer = ResultsPrinter(self.pretty_output)
                printer.print_results(results=all_results)

        return self.pretty_output.print_color(text="\nScan finished successfully", color='green')
