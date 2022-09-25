import getopt, sys, boto3, json
import string
import logging
import os

from logging import exception
from operator import ge
from botocore.exceptions import ClientError
from typing import Dict, List

from modules import all_regions, redshift, rds, ecs, eks, cloudFront, dynamoDB, arango
from modules.aws_session import AwsSession
from modules.sherlog_s3 import SherlogS3
from modules.arango import DBConnection

## Global variable
listObj = []

def create_output(output):

	# if path.isfile(filename) is False:
  	# 	raise Exception("File not found")

	with open(output, 'w') as json_file:
		json.dump(listObj, json_file, 
							indent=4,  
							separators=(',',': '))
	print(f'Successfully created results {output} file')

	db = arango.DBConnection(results=listObj)
	db.create_results()

def init(profile:string, region:string, debug:bool):
	
	## ## Global resources
	global_session = boto3.session.Session(profile_name=profile)
	s3_results = sherlog_s3.read_s3(global_session); listObj.append(s3_results)
	cf_results = cloudFront.read_cloudFront(global_session); listObj.append(cf_results)

	## ## Regional resources
	reg_session = boto3.session.Session(profile_name=profile,region_name=region)

	## Redshift
	redshift_results = {'Redshift':[]}
	if region == "all-regions":
		regions = all_regions.all_regions()
		for reg in regions:
			try:
				session = boto3.session.Session(profile_name=profile,region_name=reg)
				results = redshift.read_redshift(session, reg)
				if results is not None:
					redshift_results["Redshift"].append(results)
				else:
					pass
			except BaseException as be:
				if debug:
					print(be)
				continue
	else:
		try:
			results = redshift.read_redshift(reg_session, region)
			if results is not None:
					redshift_results["Redshift"].append(results)
			else:
				pass
		except BaseException as be:
			if debug:
				print(be)

	listObj.append(redshift_results)

	## RDS
	rds_results = {'RDS':[]}
	if region == "all-regions":
		regions = all_regions.all_regions()
		for reg in regions:
			try:
				session = boto3.session.Session(profile_name=profile,region_name=reg)
				results = rds.read_rds(session, reg)
				if results is not None:
					rds_results["RDS"].append(results).append(results)
				else:
					pass
			except BaseException as be:
				if debug:
					print(be)
	else:
		try:
			results = rds.read_rds(reg_session, region)
			if results is not None:
				rds_results["RDS"].append(results).append(results)
			else:
				pass
		except BaseException as be:
			if debug:
				print(be)

	listObj.append(rds_results)

	## ECS
	ecs_results = {'ECS':[]}
	if region == "all-regions":
		regions = all_regions.all_regions()
		for reg in regions:
			try:
				session = boto3.session.Session(profile_name=profile,region_name=reg)
				results = ecs.read_ecs(session, reg)
				if results is not None:
					ecs_results["ECS"].append(results)
				else:
					pass
			except BaseException as be:
				if debug:
					print(be)
	else:
		try:
			results = ecs.read_ecs(reg_session, region)
			if results is not None:
				ecs_results["ECS"].append(results)
			else:
				pass
		except BaseException as be:
			if debug:
				print(be)

	listObj.append(ecs_results)

	## EKS
	eks_results = {'EKS':[]}
	if region == "all-regions":
		regions = all_regions.all_regions()
		for reg in regions:
			try:
				session = boto3.session.Session(profile_name=profile,region_name=reg)
				results = eks.read_eks(session, reg)
				if results is not None:
					eks_results["EKS"].append(results)
				else:
					pass
			except BaseException as be:
				if debug:
					print(be)
	else:
		try:
			results = eks.read_eks(reg_session, region)
			if results is not None:
				eks_results["EKS"].append(results)
			else:
				pass
		except BaseException as be:
			if debug:
				print(be)
	
	# DynamoDB
	dynamoDB_results = {'DynamoDB':[]}
	if region == "all-regions":
		regions = all_regions.all_regions()
		for reg in regions:
			try:
				session = boto3.session.Session(profile_name=profile,region_name=reg)
				results = dynamoDB.read_dynamodb(session, reg)
				if results is not None:
					dynamoDB_results["DynamoDB"].append(results)
				else:
					pass
			except BaseException as be:
				if debug:
					print(be)
	else:
		try:
			results = dynamoDB.read_dynamodb(reg_session, region)
			if results is not None:
				dynamoDB_results["DynamoDB"].append(results)
			else:
				pass
		except BaseException as be:
			if debug:
				print(be)

	listObj.append(eks_results)

def main():
	'''
	Main function
	'''
	logging.basicConfig(format="%(levelname)s: %(message)s")
	log = logging.getLogger()
	log_level = os.environ['LOG_LEVEL'].upper()
	log.setLevel(log_level)
	
	role_name = os.environ['ROLE_NAME']
	accounts_configuration = list(eval(os.environ['ACCOUNTS_CONFIGURATION']))
	db_url = os.environ['DB_URL']
	db_username = os.environ['DB_USERNAME']
	db_password = os.environ['DB_PASSWORD']
	db_name = os.environ['DB_NAME']

	resource_tags=[]
	all_results = []
	buckets=[]
	apis=[]
	ec2s=[]
	dbs=[]
	clusters=[]
	elbs=[]
	associations=[]

	for a_c in accounts_configuration:
		role_arn=f"arn:aws:iam::{a_c['accountId']}:role/{role_name}"
		session = AwsSession(
			log=log,
			role_arn=role_arn,
			external_id=a_c['externalId'],
			session_name='test'
		).get_session()

		buckets, buckets_tags, buckets_associations = SherlogS3(log, session).analyze()
		resource_tags.extend(buckets_tags)
		associations.extend(buckets_associations)
		print(resource_tags)
		print(associations)

		db_connection = DBConnection(log)
		db_connection.list_to_collection(collection='sherlog_resources', list=buckets)
		db_connection.list_to_collection(list=resource_tags, collection='resource_tags')
		db_connection.create_association(associations=associations)

if __name__ == "__main__":
    main()