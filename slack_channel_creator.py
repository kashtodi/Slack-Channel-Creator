# Written by Kashyap Todi (https://www.kashyaptodi.com)
# Last updated on 30 September, 2020

# This script uses the Slack API to read channel and member lists, create new (private) channels, and add members to them.

# Find your Bot User OAuth Access Token from https://api.slack.com/apps
# Make sure the following Bot Token Scopes are enabled:
## channels:manage
## channels:read
## groups:read
## groups:write
## im:read
## mpim:read
## users:read

import os
import sys
import json
import csv
import requests
import time


error_log = []
# Input data. Can be initialised from JSON or CSV file.
if len(sys.argv) == 2:
    filepath = sys.argv[1]
else:
    filepath = input("Enter filepath for input file (JSON/CSV): ")

filepath = filepath.replace("\\","")
if not os.path.isfile(filepath):
    raise Exception("No valid file found at input filepath!")

print("Valid file found")
extension = os.path.splitext(filepath)[-1].lower()
if extension == ".json":
    # read json file
    with open(filepath) as json_file:
        input_data = json.load(json_file)            
elif extension == ".csv":
    # read csv
    reader = csv.DictReader(open(filepath), skipinitialspace=True)    
    input_data = list(reader)
else:
    raise Exception("Wrong input file format")

print("Found the following fields in input data: {}".format(input_data[0].keys()))
# Now we query which fields to use for channel names (string) and members list (array) 
found_channel_field = False
while not found_channel_field:
    channel_field = input("Enter the field name to use for channel names: ")
    if channel_field in input_data[0].keys():
        found_channel_field = True
    else: print("Invalid field name")
found_members_field = False
while not found_members_field:
    members_field = input("Enter the field name to use for member names: ")
    if members_field in input_data[0].keys():
        found_members_field = True
    else: print("Invalid field name")


# Read Slack app token
token_id = input("Enter Token (Find your Bot User OAuth Access Token from https://api.slack.com/apps): ")
token = "Bearer " + token_id

# Get existing channels list and store in dictionary
url = "https://slack.com/api/conversations.list?exclude_archived=true&limit=1000&types=public_channel%2Cprivate_channel"
headers = {"Authorization":token, 'Content-type': 'application/x-www-form-urlencoded'}
response_contents = requests.get(url, headers=headers).content.decode()
response_data = json.loads(response_contents)
channels_data = response_data["channels"]
channels = {}
for channel_data in channels_data:
    name = channel_data['name']
    channel_id = channel_data['id']
    channels[name] = channel_id
print("{} channels found".format(len(channels)))

# Get members names and IDs
url = "https://slack.com/api/users.list?limit=1000"
headers = {"Authorization":token, 'Content-type': 'application/x-www-form-urlencoded'}
response_contents = requests.get(url, headers=headers).content.decode()
# TODO: read the response cursor to get next batch in case >1000 members in team
response_data = json.loads(response_contents)
members_data = response_data["members"]
members = {}
for member_data in members_data:
    if not member_data["deleted"]:
        real_name = member_data["real_name"]
        member_id = member_data["id"]
        members[real_name] = member_id
print("{} members found".format(len(members)))

# Now, we are ready to iterate over input data.
# Here, we will create new private channels (if needed), and invite members to them

for channel_to_add in input_data:
    if channel_to_add[channel_field] not in channels.keys():
        # Create the channel and read the channel ID from response.
        url = "https://slack.com/api/conversations.create"
        headers = {"Authorization":token, 'Content-type': 'application/x-www-form-urlencoded'}
        body = {"name":channel_to_add[channel_field], "is_private":True}
        response_contents = requests.post(url, headers=headers, data=body).content.decode()
        channel_data = json.loads(response_contents)
        if channel_data["ok"]:
            channel_id = channel_data["channel"]["id"]
            print("Created new channel {}".format(channel_id))
            channels[channel_to_add[channel_field]] = channel_id
        else: 
            print("Error while creating channel")
            print(channel_data)
            error_entry = {}
            error_entry["type"] = "Channel creation error"
            error_entry["item"] = channel_to_add[channel_field]
            error_entry["detail"] = channel_data
            error_log.append(error_entry)
            continue
    else:
        print("Channel {} exists already".format(channel_to_add[channel_field]))
        error_entry = {}
        error_entry["type"] = "Channel exists warning"
        error_entry["item"] = channel_to_add[channel_field]
        error_entry["detail"] = "Channel {} already exists. Will not create a new one".format(channel_to_add[channel_field])
        error_log.append(error_entry)

    
    channel_id = channels[channel_to_add[channel_field]] # Get channel ID from dictionary
    
    # Convert member names to list if needed
    if not isinstance(channel_to_add[members_field], list):
        members_string = channel_to_add[members_field].replace(";",",")
        member_names = [name.strip() for name in members_string.split(',')] # Member names string to list
    else: member_names = channel_to_add[members_field]

    # Check which members in input list are valid (exist in team)
    valid_members = []
    # Iterate over list of member names
    for member_name in member_names:
        if member_name.strip() in members.keys():
            valid_members.append(members[member_name]) # Member exists in team. Append member ID to list
        else:
            print("Member {} not found in team".format(member_name.strip()))
            error_entry = {}
            error_entry["type"] = "Member not in team"
            error_entry["item"] = member_name
            error_entry["detail"] = "Member with real name {} not found in team".format(member_name)
            error_log.append(error_entry)

    # Now invite all valid members serially. We do not invite all members in one-shot to avoid complete failure in cases where a particular member can not be added. 
    url = "https://slack.com/api/conversations.invite"
    for member in valid_members:
        headers = {"Authorization":token, 'Content-type': 'application/x-www-form-urlencoded'}
        body = {"channel":channel_id, "users":member}
        response_contents = requests.post(url, headers=headers, data=body).content.decode()
        response_data = json.loads(response_contents)
        if response_data["ok"]:
            print("Added member {} to channel {}".format(member,channel_id) )
        else:
            print("Error while adding member")
            print(response_data)
            error_entry = {}
            error_entry["type"] = "User invite error"
            error_entry["item"] = member
            error_entry["detail"] = response_data
            error_log.append(error_entry)

with open("errorlog_{}.json".format(str(time.time())), "w") as fp:
    json.dump(error_log,fp,indent=4)