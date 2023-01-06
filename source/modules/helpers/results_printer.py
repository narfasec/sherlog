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
                    for s3_result in result['s3']:
                        policy = ""
                        for key, value in s3_result.items():
                            policy = key
                        if s3_result[policy]:
                            self.pretty_output.print_color(
                                header=policy,
                                text=""
                            )
                            for policy_result in s3_result[policy]:
                                name = policy_result['name']
                                arn = policy_result['arn']
                                comments = policy_result['comments']
                                text = "Bucket: "+policy_result['name']
                                self.pretty_output.print_color(text=text, color="blue")
                                print("Arn: "+policy_result['arn'])
                                if len(comments) > 1:
                                    print("Comments:")
                                    for comment in comments:
                                        print("\t-"+comment)
                                else:
                                    print("Comments: "+comments[0])
                                print("")
                if 'dynamodb' in result:
                    for dynamo_result in result['dynamodb']:
                        policy = ""
                        for key, value in dynamo_result.items():
                            policy = key
                        if dynamo_result[policy]:
                            self.pretty_output.print_color(
                                header=policy,
                                text=""
                            )
                            for policy_result in dynamo_result[policy]:
                                name = policy_result['name']
                                arn = policy_result['arn']
                                region = policy_result['region']
                                comments = policy_result['comments']
                                text = "DynamoDB table: "+policy_result['name']
                                self.pretty_output.print_color(text=text, color="blue")
                                print("Arn: "+policy_result['arn'])
                                print('Region: '+region)
                                if len(comments) > 1:
                                    print("Comments:")
                                    for comment in comments:
                                        print("\t-"+comment)
                                else:
                                    print("Comments: "+comments[0])
                                print("")
                if 'cloudfront' in result:
                    for cf_result in result['cloudfront']:
                        policy = ""
                        for key, value in cf_result.items():
                            policy = key
                        if cf_result[policy]:
                            self.pretty_output.print_color(
                                header=policy,
                                text=""
                            )
                            for policy_result in cf_result[policy]:
                                name = policy_result['name']
                                arn = policy_result['arn']
                                comments = policy_result['comments']
                                text = "Cloudfront: "+policy_result['name']
                                self.pretty_output.print_color(text=text, color="blue")
                                print("Arn: "+policy_result['arn'])
                                if len(comments) > 1:
                                    print("Comments:")
                                    for comment in comments:
                                        print("\t-"+comment)
                                else:
                                    print("Comments: "+comments[0])
                                print("")
                if 'rds' in result:
                    for rds_result in result['rds']:
                        policy = ""
                        for key, value in rds_result.items():
                            policy = key
                        if rds_result[policy]:
                            self.pretty_output.print_color(
                                header=policy,
                                text=""
                            )
                            for policy_result in rds_result[policy]:
                                name = policy_result['name']
                                arn = policy_result['arn']
                                region = policy_result['region']
                                engine = policy_result['engine']
                                comments = policy_result['comments']
                                text = "RDS: "+policy_result['name']
                                self.pretty_output.print_color(text=text, color="blue")
                                print("Arn: "+policy_result['arn'])
                                print('Region: '+region)
                                print('Engine: '+engine)
                                if len(comments) > 1:
                                    print("Comments:")
                                    for comment in comments:
                                        print("\t-"+comment)
                                else:
                                    print("Comments: "+comments[0])
                                print("")
                if 'elbv2' in result:
                    for alb_result in result['elbv2']:
                        policy = ""
                        for key, value in alb_result.items():
                            policy = key
                        if alb_result[policy]:
                            self.pretty_output.print_color(
                                header=policy,
                                text=""
                            )
                            for policy_result in alb_result[policy]:
                                name = policy_result['name']
                                arn = policy_result['arn']
                                region = policy_result['region']
                                comments = policy_result['comments']
                                text = "ALB: "+policy_result['name']
                                self.pretty_output.print_color(text=text, color="blue")
                                print("Arn: "+policy_result['arn'])
                                print('Region: '+region)
                                if len(comments) > 1:
                                    print("Comments:")
                                    for comment in comments:
                                        print("\t-"+comment)
                                else:
                                    print("Comments: "+comments[0])
                                print("")