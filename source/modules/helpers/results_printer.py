'''
'''
class ResultsPrinter:
    '''
    Class to allow other modules print colorful messages
    '''
    def __init__(self, pretty_output):
        self.pretty_output = pretty_output
        
    def print_results(self, results):
            '''
            Function to format the output in the console
            '''
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
                if 'elbv2' in result:
                    print('there is an ELB')
                    headers = ['Name', 'Region', 'arn', 'Policy']
                    if len(result['elbv2']) == 1:
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
                    for elb_result in result['elbv2']:
                        name, region, arn, policy = elb_result['name'], elb_result['region'], elb_result['arn'], elb_result['policy']
                        values.append([name,region,arn,policy])
                    self.pretty_output.print_results(headers=headers, values=values)