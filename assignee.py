import requests
from requests.auth import HTTPBasicAuth
import json
from props import props
import base64


# assigns a ticket to someone
def assign(issue_id, assignee):
    credentials = props['credentials'] + "/srelib_credentials.json"
    with open(credentials) as json_data:
        d = json.load(json_data)
    username = base64.b64decode(bytes(d['credentials'][0]['u'], "utf-8")).decode('utf-8')
    password = base64.b64decode(bytes(d['credentials'][0]['p'], "utf-8")).decode('utf-8')
    data = json.dumps({
        "name": assignee,
    })
    d = data.encode('utf-8')
    headers = {"Content-Type": "application/json",
               "Accept": "application/json",
               "Content-length": str(len(d))}
    auth = HTTPBasicAuth(username, password)
    response = requests.put(f"{props['jira_api_base']}/{issue_id}/assignee", headers=headers, auth=auth, data=d)
    return response


# checks to see if assign command is followed by the correct arguments
# will return the error message if not, and True if yes
def check_assign_command(command):
    index = None
    list1 = ['-id', '--id']
    list2 = ['-name', '--name']
    for num, info in enumerate(command):
        if info == "--assign":
            index = num
            break
    if index is not None:
        # err = "'--assign' command must be followed by both '--id' and '--name' commands."
        if len(command) - (index + 1) < 4:
            return False
        if command[index+1] not in list1 and command[index+3] not in list1:
            return False
        if command[index+1] not in list2 and command[index+3] not in list2:
            return False
    return True

