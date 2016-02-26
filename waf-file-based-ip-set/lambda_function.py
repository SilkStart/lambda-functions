'''
Copyright 2015 SilkStart Technology Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import urllib
import boto3
import re

IP_SET_NAME = "IPSetName"        # Name of your IPSet
BUCKET_ID = "bucket-id"          # ID of your Bucket
OBJECT_KEY = "block-list-file.txt" # Key for your block list file

def lambda_handler (event, context):
    
    # Find the name of the bucket and object that we've been linked with
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key']).decode('utf8')

    ip_block_list = get_blocked_ips_from_s3_object(bucket,key)
    create_or_update_ip_set(IP_SET_NAME, ip_block_list)
    print "Update complete"

def create_or_update_ip_set(ip_set_name,ip_cidrs):
    waf = boto3.client('waf')

    print "Looking for IP set with name {}".format(ip_set_name)
    response = waf.list_ip_sets(Limit=100)

    ip_set_id = None
    if response and 'IPSets' in response:
        for ip_set_result in response['IPSets']:
            if ip_set_result['Name'] == ip_set_name:
                ip_set_id = ip_set_result['IPSetId']
                print "IP Set with name {} found with ID {}".format(ip_set_name,ip_set_id)
                break        
    
    # Update List
    if ip_set_id:
        print "Updating existing IP Set {}".format(ip_set_id) 
        ip_set = waf.get_ip_set(IPSetId=ip_set_id)['IPSet']
        
        incoming_cidrs = set(ip_cidrs)
        existing_cidrs = set([descriptor["Value"] for descriptor in ip_set['IPSetDescriptors']])
        
        to_insert = incoming_cidrs.difference(existing_cidrs)
        to_delete = existing_cidrs.difference(incoming_cidrs)
        
        def update_dict_for_cidr_action(cidr, action):
            print "{} {}".format(action,cidr)
            return {
                "Action": action,
                "IPSetDescriptor": {
                    "Type": "IPV4",
                    "Value": cidr
                }
            }
        
        
        insert_values = [update_dict_for_cidr_action(cidr, "INSERT") for cidr in to_insert]
        delete_values = [update_dict_for_cidr_action(cidr, "DELETE") for cidr in to_delete]
        print "Inserting {} and Deleting {} records".format(len(insert_values),len(delete_values))
        all_values = insert_values + delete_values
        
        if all_values:
            change_token = waf.get_change_token()['ChangeToken']
            waf.update_ip_set(IPSetId=ip_set_id, ChangeToken=change_token, Updates=all_values)
        
    # Create List
    else:
        print "Creating new IP Set"
        
   
def get_blocked_ips_from_s3_object(bucket_id, object_key):
    s3 = boto3.client('s3')

    print "Getting S3 Object from bucket {} with key {}".format(bucket_id,object_key)
    s3_object = s3.get_object(Bucket=bucket_id,Key=object_key)
    content = s3_object['Body'].read()
    
    lines = [re.sub('#.*$','',line).strip() for line in content.split('\n')]
    cidrs = [line if '/' in line else line + "/32" for line in lines if line]
    
    print "{} CIDRs found".format(len(cidrs))

    return cidrs

if __name__ == "__main__":
    event = {  
        "Records":[  
            {  
                "eventVersion":"2.0",
                "eventSource":"aws:s3",
                "s3":{  
                    "s3SchemaVersion":"1.0",
                    "object":{  
                        "key":"ip-block-list.txt",         
                    }
                }
            }
        ]
    }
    lambda_handler(event,None)
    
# Sample Event from SNS
# {  
#     "Records":[  
#        {  
#           "eventVersion":"2.0",
#           "eventSource":"aws:s3",
#           "s3":{  
#              "s3SchemaVersion":"1.0",
#              "object":{  
#                 "key":"object-key",         
#              }
#           }
#        }
#     ]
#  }  
# 