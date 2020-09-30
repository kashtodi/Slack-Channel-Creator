
# Slack Channel Creator

### Created by Kashyap Todi (www.kashyaptodi.com)
This script can be used to automatically create a batch of Slack channels, and to invite particular users to each of them. 
It uses methods from the [Slack API](https://api.slack.com) to complete tasks. Input data can be provided either as a JSON or a CSV file.

## Requirements
- Python 3.6 or above 

## Instruction Guide
1. Go to https://api.slack.com/apps => `Create New App`
2. Give the app a name, and select the appropriate workspace
3. In the "Basic Information" page for the app, navigate to `Add features and functionality` => `Permissions`
4. Under "Scopes", add the following "Bot Token Scopes":
    - `channels:manage`
    -  `channels:read`
    -  `groups:read`
    -  `groups:write`
    -  `im:read`
    -  `mpim:read`
    -  `users:read`
5. Scroll to the top => `Install App to Workspace` => `Allow`
6. Copy your Bot User OAuth Access Token
7. Create a JSON or CSV input data file. See the section on `Input File Formats` below for details and example.
8. Run the python script:
    ```python
    python3 slack_channel_creator.py # Input filepath will be entered at runtime
    ```
    ```python
    python3 slack_channel_creator.py <INPUT_FILE_PATH> # Input filepath as an argument
    ```
9. Specify path to input CSV/JSON file (no quotes)
10. The script will display the detected field names. Upon prompt, enter the field names you want to use for `channel names` and `member lists`  
11. Paste token upon prompt
12. The script will display the number of existing channels, and number of members.
13. Finally, it will iterate over all entries in the input data:
    1. Create a new private channel if it does not exist
    2. Get the channel ID
    3. Check the input member list, and get member IDs for all valid members
    4. Serially invite (add) each member to the channel

## Input File Formats
The script allows you to provide input data either using JSON or CSV formats. 
The input file should contain a list of entries, where each entry has a field for `channel name` and a field for `members list`

### JSON:
Your JSON file should contain an array of objects.
Each object should have two keys – one for the `channel name`, and another for the `members list` for the corresponding channel. You can use whatever key names you like, as the script will ask you to specify them at run time.
`channel name`: This should be a **string** value
`members list`: This should either be an **array** object containing strings (one string per member name), or a **string** value with member names separated using **commas or semi-colons**. Each member name within the members list should correspond to a valid `real_name` in the Slack team's user list. Invalid member names will be ignored.
*(You can use the web-based tester at https://api.slack.com/methods/users.list to retrieve the user list)*

#### JSON Example:
```json
[
	{"channel_name":"test-channel1","members":["Member1 Name1", "Member2 Name2"]},
	{"channel_name":"test-channel2","members":["Member1 Name1", "Member2 Name3"]},
	{"channel_name":"test-channel3","members":["Member2 Name2", "Member3 Name3"]}
]
```

### CSV:
Your CSV file should have two columns – one for the `channel name`, and another for the `members list` for the corresponding channel. The header row should contain the column names. You can use whatever names you like, as the script will ask you to specify them at run time.
`channel name`: This should be a **string** value
`members list`: This should be  a **string** value containing member names. Each member name should be separated either by a **comma or semi-colon**. Each member name within the membesr list should correspond to a valid `real_name` in the Slack team's user list. Invalid member names will be ignored.
*(You can use the web-based tester at https://api.slack.com/methods/users.list to retrieve the user list)*

#### CSV Example:
```csv
Channel Name, Members
test-channel1, "Member1 Name1, Member2 Name2"
test-channel2, "Member1 Name1, Member3 Name3"
test-channel3, "Member2 Name2, Member3 Name3"
```