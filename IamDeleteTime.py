from datetime import datetime, timedelta

import boto3
import json

client = boto3.client('iam')
resource = boto3.resource('iam')
s3 = boto3.client('s3')

time_now = datetime.now()

# Edit for your environment
days_to_delete = 100
bucketname = 'bucketjeffreyrupp'
filename = 'tekst.txt'

def handler(event,context):
    try:
        roles = client.list_roles()
        N_delete = []
        keep_list=[]
        delete_list=[]

        # Loop through the roles and print it's Last Used date
        for r in roles['Roles']:
            role = resource.Role(name=r['RoleName'])
            try:
                # Check if we have a usable usage dict
                if role.role_last_used:

                    subsegment.put_annotation('RoleLastUsed', str(
                        role.role_last_used['LastUsedDate']))

                    # Subtract the LastUsedDate from todays date
                    time_diff = time_now - \
                        role.role_last_used['LastUsedDate'].replace(tzinfo=None)

                    # Check diff is more than or equal to 100 days
                    if time_diff.days >= days_to_delete:
                        for r in roles['Roles']:
                            role = resource.Role(name=r['RoleName'])
                            string_to_search = str(role)
                        
                            # Get the content of a file stored in S3
                            fileObj = s3.get_object(Bucket=bucketname, Key=filename)
                            file_content = fileObj["Body"].read().decode('utf-8')
                            # Read all lines in the file one by one
                            delete_list.append(string_to_search)

                            try:
                                for line in file_content.split('\r'):
                                    # For each line, check if line contains the string
                                    if string_to_search in line:
                                        keep_list.append(string_to_search)
                                        delete_list.remove(string_to_search)
                                    if not string_to_search in line:
                                        try:
                                            # Get all Managed Policies and detatch them
                                            [role.detach_policy(PolicyArn=policy.arn)
                                            for policy in role.attached_policies.all()]

                                            # Get all Instance Profiles and detatch them
                                            [profile.remove_role(RoleName=role.name)
                                            for profile in role.instance_profiles.all()]

                                            # Get all Inline Policies and delete them
                                            [role_policy.delete() for role_policy in role.policies.all()]

                                            # Delete te role
                                            role.delete()
                                        except Exception as e:
                                            N_delete.append(e)
                            except:
                                pass  
    return {
    'statusCode': 200,
    'keep_list': keep_list,
    'delete_list': delete_list,
    'N_delete': N_delete
    }
