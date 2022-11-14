# ## AppSync code analysis
# from typing import List

# def get_role_names(client) -> List[str]:
#     """ Retrieve a list of role names by paginating over list_roles() calls """
#     roles = []
#     role_paginator = client.get_paginator('list_roles')
#     for response in role_paginator.paginate():
#         response_role_names = [r.get('RoleName') for r in response['Roles']]
#         roles.extend(response_role_names)
#     return roles

# def read_appSync(session, region):
#     iam = session.client('iam', region_name=region)
#     roles = iam.list_roles()
#     role_paginator = iam.get_paginator('list_roles')
#     role_names = get_role_names(iam)
#     roles_logging_AppSync = []

#     for name in role_names:
#         policies = iam.list_attached_role_policies(RoleName=name)
#         for policy in policies['AttachedPolicies']:
#             if policy['PolicyName'] == 'AWSAppSyncPushToCloudWatchLogs':
#                 roles_logging_AppSync.append(name)

#     #####################################
#     ##             AppSync             ##
#     #####################################

#     iam = prod_read.client('iam', region_name='us-west-2')
#     roles = iam.list_roles()
#     role_paginator = iam.get_paginator('list_roles')
#     role_names = get_role_names(iam)
#     roles_logging_AppSync = []

#     for name in role_names:
#         policies = iam.list_attached_role_policies(RoleName=name)
#         for policy in policies['AttachedPolicies']:
#             if policy['PolicyName'] == 'AWSAppSyncPushToCloudWatchLogs':
#                 roles_logging_AppSync.append(name)

#     append_new_line('results.txt', '## AppSync ##')
#     if not roles_logging_AppSync:
#         append_new_line('results.txt', '\tThere are no roles to push logs from AppSync to CloudWatch')
#     else:
#         append_new_line('results.txt','Roles with AWSAppSyncPushToCloudWatchLogs:')
#         for role in roles_logging_AppSync:
#             append_new_line('results.txt', '\t'+role)

# '''
# Octoguard
# Sherlog AppSync

# TODO AppSync feature is incomplete. The following requirements must be completed:
#  - Link the role that pushes logs with correspondent AppSync resource
#  - Use pagination
# '''
# from typing import Tuple
# import boto3

# class SherlogCF:
#     '''
#     Sherlog component for CloudFront distributions
#     '''
#     def __init__(self, log, session):
#         # Get available regions list
#         self.log = log
#         self.available_regions = boto3.Session().get_available_regions('iam')
#         self.account_id=session.client('sts').get_caller_identity().get('Account')
#         self.session=session
#         self.formated_results=[]
#         self.associations=[]
#         self.resource_tags=[]
#         self.has_results=False

#     def get_results(self) -> Tuple[list, list, list]:
#         '''
#         Geter for results
#         '''
#         if self.has_results:
#             return self.formated_results, self.resource_tags, self.associations
#         else:
#             return None

#     def analyze(self):
#         '''
#         Function that will read the logging status of the buckets
#         '''
#         iam = self.session.client('iam')
#         roles = iam.list_roles()
#         role_paginator = iam.get_paginator('list_roles')
#         role_names = get_role_names(iam)
#         roles_logging_appsync = []

#         for name in role_names:
#             policies = iam.list_attached_role_policies(RoleName=name)
#         for policy in policies['AttachedPolicies']:
#             if policy['PolicyName'] == 'AWSAppSyncPushToCloudWatchLogs':
#                 roles_logging_AppSync.append(name)
#         try:
#             for page in page_iterator:
#                 distributions += [d["Id"] for d in page['DistributionList']['Items']]
#         except KeyError:
#             self.log.info('No CloudFront Distributions found')

#         for item in distributions:
#             try:
#                 cf_config = cloudfront.get_distribution_config(Id=item)
#                 arn = f"arn:aws:cloudfront::{self.account_id}:distribution/{item}"
#                 tags = cloudfront.list_tags_for_resource(Resource=arn)
#                 dist = cf_config['DistributionConfig']
#                 if dist['Logging']['Enabled'] is False:
#                     self.format_data(cf_name=item, tags=tags, arn=arn)
#                     self.has_results = True
#             except KeyError:
#                 self.log.error('Error while getting info from distribution: %s', item)
#                 self.log.error(KeyError)

#     def format_data(self, cf_name, tags, arn):
#         """
#         Format data to insert on DB
#         """
#         self.formated_results.append({
#             "name":cf_name,
#             "rational":"Public Policy",
#             "accountId":self.account_id,
#             "service":"cloudfront",
#             "arn":arn,
#             "policy":"sherlog-4-1"
#         })
#         self.resource_tags.append(
#             {
#                 "arn":f"{self.account_id}/tags/{arn}",
#                 "tags":tags
#             })
#         self.associations.append(
#             {
#                 "parentId":arn,
#                 "childId":f"{self.account_id}/tags/{arn}"
#             }
#         )
